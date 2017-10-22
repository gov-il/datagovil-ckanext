import logging
import ckan.lib.base as base
import ckan.plugins as p
import ckan.logic as logic
import ckan.model as model
import ckan.lib.captcha as captcha
import ckan.lib.navl.dictization_functions as dictization_functions
import ckan.lib.mailer as mailer
import ckanext.gov_theme.mailer as custom_mailer
import ckan.lib.helpers as h
import socket
from bottle import route, run, request



from pylons import config
from ckan.common import _, request, c, response
from ckanext.report.interfaces import Ireport


log = logging.getLogger(__name__)

render = base.render
abort = base.abort
redirect = base.redirect

DataError = dictization_functions.DataError
unflatten = dictization_functions.unflatten

check_access = logic.check_access
get_action = logic.get_action
flatten_to_string_key = logic.flatten_to_string_key

#global to share it from form to submit functions
author_email_address = "1"
report_referrer = "1"

class reportController(base.BaseController):
    """
    Controller for displaying a report form
    """

    def __before__(self, action, **env):

        super(reportController, self).__before__(action, **env)
        if "form" in request.GET:
            if "link" in request.GET.getone('form'):
                c.report_title = _('Broken link report')
        else:
            c.report_title = _('Report')
        global report_referrer
        c.report_ref = report_referrer
        try:
            
            self.context = {'model': model, 'session': model.Session, 'user': base.c.user or base.c.author, 'auth_user_obj': base.c.userobj}
            check_access('send_report', self.context)

        except logic.NotAuthorized:
            base.abort(401, _('Not authorized to use report form'))

        
    @staticmethod
    def _submit(context):
        try:
            data_dict = logic.clean_dict(unflatten(logic.tuplize_dict(logic.parse_params(request.params))))
            context['message'] = data_dict.get('log_message', '')
            c.form = data_dict['name']
            captcha.check_recaptcha(request)
        except logic.NotAuthorized:
            base.abort(401, _('Not authorized to see this page'))
        except captcha.CaptchaError:
            error_msg = _(u'Bad Captcha. Please try again.')
            h.flash_error(error_msg)

        errors = {}
        error_summary = {}

        if data_dict["email"] == '':
            errors['email'] = [_(u'Missing value')]
            error_summary[_(u'email')] = _(u'Missing value')

        if data_dict["name"] == '':
            errors['name'] = [_(u'Missing Value')]
            error_summary[_(u'name')] = _(u'Missing value')

        if data_dict["content"] == '':
            errors['content'] = [_(u'Missing value')]
            error_summary[_(u'request')] = _(u'Missing value')

        if len(errors) == 0:
            global author_email_address
            global report_referrer
            global report_resource_name
            global report_organization_name
            global report_dataset_name

            if report_organization_name is None:
                report_organization_name = ""
            if report_dataset_name is None:
                report_dataset_name = ""
            if report_dataset_name is None:
                report_dataset_name = ""

            if "form" in request.GET:
                if "link" in request.GET.getone('form'):
                    report_mail_title = _(u'Report Broken Link - Government Data')
                    report_mail_secondary_title = _(u'A broken link report is recieved')
            else:
                report_mail_title = _(u'Report - Government Data')
                report_mail_secondary_title = _(u'A report is recieved')
            body = _('Hello')+","
            body += '\n'+report_mail_secondary_title
            body += '\n'+_(u'First name and surname')+": "+data_dict["name"]
            body += '\n'+_(u'Email')+": "+data_dict["email"]
            body += '\n'+_(u'Data ID')+': '+data_dict["id"]
            body += '\n'+_(u'Link to data')+': '+report_referrer
            body += '\n'+_(u'Message')+': '+data_dict["content"]
            body += '\n'+_(u'Organization')+': '+report_organization_name
            body += '\n'+_(u'Dataset')+': '+report_dataset_name
            body += '\n'+_(u'Resource')+': '+report_resource_name
            body += '\n\n'+_(u'Best Regards')
            body += '\n'+_(u'Government Data Site')

            mail_dict = {
                #added it to send it to the maintainer of the data
                'recipient_email': config.get('email_to'),
                'recipient_name': config.get("ckanext.report.recipient_name", config.get('ckan.site_title')),
                'subject': config.get("ckanext.report.subject", report_mail_title),
                'body': body,
                'headers': {'reply-to': data_dict["email"]}
            }

            mail_dict_author = {
                #added it to send it to the author of the data
                'recipient_email': author_email_address,
                'recipient_name': config.get("ckanext.report.recipient_name", config.get('ckan.site_title')),
                'subject': config.get("ckanext.report.subject", report_mail_title),
                'body': body,
                'headers': {'reply-to': data_dict["email"]}
            }
            
            # Allow other plugins to modify the mail_dict
            for plugin in p.PluginImplementations(Ireport):
                plugin.mail_alter(mail_dict, data_dict)
                plugin.mail_alter(mail_dict_author, data_dict)
            try:
                #sending email
                custom_mailer.mail_recipient(**mail_dict)
                if author_email_address:
                    custom_mailer.mail_recipient(**mail_dict_author)
            except (mailer.MailerException, socket.error):
                h.flash_error(_(u'Sorry, there was an error sending the email. Please try again later'))
            else:
                data_dict['success'] = True
                
        return data_dict, errors, error_summary

    def ajax_submit(self):
        """
        AJAX form submission
        @return:
        """
        data, errors, error_summary = self._submit(self.context)
        data = flatten_to_string_key({'data': data, 'errors': errors, 'error_summary': error_summary})
        response.headers['Content-Type'] = 'application/json;charset=utf-8'
        return h.json.dumps(data)

    def form(self):
        """
        Return a report form
        :return: html
        """

        data = {}
        errors = {}
        error_summary = {}
        # Submit the data
        if 'save' in request.params:
            data, errors, error_summary = self._submit(self.context)
        else:
            # get the referrer header
            # cut it to get the the source id
            # use the ckan api to get the autohr and maintainer details of the data and assign it to the global parameters
            try:

                uri = request.headers.get('Referer')
                global report_referrer
                report_referrer = uri
                dataid = ""
                if uri:
                    if "resource" in uri:
                        dataidIndex = uri.index("resource")
                        dataid = uri[dataidIndex+9:]
                if "?" in dataid:
                    dataid = dataid.split("?")[0]  
                data['id'] = dataid

                # /api/3/action/package_show?id=c388e16d-72bf-4cbf-b9b0-1b6ef9caf8cf
                import urllib2, urllib, json
                # Put the details of the dataset we're going to create into a dict.
                dataset_dict = {
                    'id': dataid,
                }
                # Use the json module to dump the dictionary to a string for posting.
                data_string = urllib.quote(json.dumps(dataset_dict))
                # We'll use the package_create function to create a new dataset.
                resource_show_api = config.get('ckan.site_url')+'/api/3/action/resource_show'
                resource = urllib2.Request(resource_show_api)
                # Creating a dataset requires an authorization header.
                # Replace *** with your API key, from your user account on the CKAN site
                # that you're creating the dataset on.
                resource.add_header('Authorization', '8c644165-16ef-4f45-b081-c17236b486fe')
                # Make the HTTP request.
                response = urllib2.urlopen(resource, data_string)
                assert response.code == 200
                # Use the json module to load CKAN's response into a dictionary.
                response_dict = json.loads(response.read())

                global report_resource_name
                global author_email_address
                global report_organization_name
                global report_dataset_name

                report_resource_name = response_dict['result']['name']

                dataset_dict = {
                    'id': response_dict['result']['package_id'],
                }
                data_string = urllib.quote(json.dumps(dataset_dict))
                package_show_api = config.get('ckan.site_url')+'/api/3/action/package_show'
                resource = urllib2.Request(package_show_api)
                resource.add_header('Authorization', '8c644165-16ef-4f45-b081-c17236b486fe')
                response = urllib2.urlopen(resource, data_string)
                response_dict = json.loads(response.read())



                author_email_address = response_dict['result']['author_email']
                report_organization_name = response_dict['result']['organization']['title']
                report_dataset_name = response_dict['result']['title']



            except AttributeError:
                data['id'] = None
            try:   # Try and use logged in user values for default values                
                data['name'] = base.c.userobj.fullname or base.c.userobj.name
                data['email'] = base.c.userobj.email
            except AttributeError:
                data['name'] = data['email'] = None
        if data.get('success', False):
            return p.toolkit.render('report/success.html')
        else:
            vars = {'data': data, 'errors': errors, 'error_summary': error_summary}
            return p.toolkit.render('report/form.html', extra_vars=vars)