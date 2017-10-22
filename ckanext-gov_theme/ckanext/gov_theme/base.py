import ckan
import logging
import ckan.lib.base as _base
from ckan.common import c,request

log = logging.getLogger(__name__)


def csrf_check(self):
    from pylons.decorators.secure import authenticated_form
    from webhelpers.pylonslib import secure_form

    if authenticated_form(request.POST):
        del request.POST[secure_form.token_key]
    else:
        log.warn('Cross-site request forgery detected, request denied: %r '
                 'REMOTE_ADDR: %s' % (request, request.remote_addr))
        _base.abort(403, detail="Cross-site request forgery detected, request denied. See "
                          "http://en.wikipedia.org/wiki/Cross-site_request_forgery for more "
                          "information.")


def g_analitics():

    # GOV CUSTOM CODE START
    url = request.environ['CKAN_CURRENT_URL'].split('?')[0]
    # /fanstatic/"ns=asdas<![endif]--><BODY ONLOAD=alert('xxx')><SCRIPT>
    #if "fanstatic" in url:
    #    _base.abort(401, ('You can not enter fanstatic directory directly'))

    c.organization_id = None
    # get the first folder after the site name
    type_from_url = url.split('/')[1]
    # get the last folder (the id) to search
    type_id = url.split('/')[-1]
    import urllib2, urllib, json
    if type_from_url == "organization":
        # check if we are inside an organization
        try:
            dataset_dict = {
                'id': type_id,
            }
            data_string = urllib.quote(json.dumps(dataset_dict))
            organization_show_api = _base.config.get('ckan.site_url') + '/api/3/action/organization_show'
            organization = urllib2.Request(organization_show_api)
            organization.add_header('Authorization', '8c644165-16ef-4f45-b081-c17236b486fe')
            response = urllib2.urlopen(organization, data_string)
            assert response.code == 200
            response_dict = json.loads(response.read())
            c.organization_id = response_dict['result']['extras'][0]['value']
        except:
            c.organization_id = None
    if type_from_url == "dataset":
        # check if we are inside a dataset
        try:
            if "resource" in url:
                # we are at resource level (resource id)
                # use the resource id to get the package id
                dataset_dict = {
                    'id': type_id,
                }
                data_string = urllib.quote(json.dumps(dataset_dict))
                resource_show_api = _base.config.get('ckan.site_url') + '/api/3/action/resource_show'
                resource = urllib2.Request(resource_show_api)
                resource.add_header('Authorization', '8c644165-16ef-4f45-b081-c17236b486fe')
                response = urllib2.urlopen(resource, data_string)
                assert response.code == 200
                response_dict = json.loads(response.read())
                # use the package id to get the organization id
                dataset_dict = {
                    'id': response_dict['result']['package_id'],
                }
                data_string = urllib.quote(json.dumps(dataset_dict))
                package_show_api = _base.config.get('ckan.site_url') + '/api/3/action/package_show'
                resource = urllib2.Request(package_show_api)
                resource.add_header('Authorization', '8c644165-16ef-4f45-b081-c17236b486fe')
                response = urllib2.urlopen(resource, data_string)
                response_dict = json.loads(response.read())
                dataset_dict = {
                    'id': response_dict['result']['organization']['id'],
                }
                data_string = urllib.quote(json.dumps(dataset_dict))
                package_show_api = _base.config.get('ckan.site_url') + '/api/3/action/organization_show'
                resource = urllib2.Request(package_show_api)
                resource.add_header('Authorization', '8c644165-16ef-4f45-b081-c17236b486fe')
                response = urllib2.urlopen(resource, data_string)
                response_dict = json.loads(response.read())
                c.organization_id = response_dict['result']['extras'][0]['value']
            else:
                # we are at dataset level (package id)
                dataset_dict = {
                    'id': type_id,
                }
                data_string = urllib.quote(json.dumps(dataset_dict))
                package_show_api = _base.config.get('ckan.site_url') + '/api/3/action/package_show'
                resource = urllib2.Request(package_show_api)
                resource.add_header('Authorization', '8c644165-16ef-4f45-b081-c17236b486fe')
                response = urllib2.urlopen(resource, data_string)
                response_dict = json.loads(response.read())
                dataset_dict = {
                    'id': response_dict['result']['organization']['id'],
                }
                data_string = urllib.quote(json.dumps(dataset_dict))
                package_show_api = _base.config.get('ckan.site_url') + '/api/3/action/organization_show'
                resource = urllib2.Request(package_show_api)
                resource.add_header('Authorization', '8c644165-16ef-4f45-b081-c17236b486fe')
                response = urllib2.urlopen(resource, data_string)
                response_dict = json.loads(response.read())
                c.organization_id = response_dict['result']['extras'][0]['value']
        except:
            c.organization_id = None
            # GOV CUSTOM CODE END


