import ckan.controllers.admin as admin

from pylons import config

import ckan.lib.base as base
import ckan.lib.helpers as h
import ckan.lib.app_globals as app_globals
import ckan.lib.navl.dictization_functions as dict_fns
import ckan.model as model
import ckan.logic as logic
import ckan.plugins as plugins
from ckan.controllers.home import CACHE_PARAMETERS

import ckanext.gov_theme.base as custom_base

c = base.c
request = base.request
_ = base._


class CustomAdminController(admin.AdminController):

    def reset_config(self):
        '''FIXME: This method is probably not doing what people would expect.
           It will reset the configuration to values cached when CKAN started.
           If these were coming from the database during startup, that's the
           ones that will get applied on reset, not the ones in the ini file.
           Only after restarting the server and having CKAN reset the values
           from the ini file (as the db ones are not there anymore) will these
           be used.
        '''

        if 'cancel' in request.params:
            h.redirect_to(controller='admin', action='config')

        if request.method == 'POST':
            #check against csrf attacks
            custom_base.csrf_check(self)
            # remove sys info items
            for item in self._get_config_form_items():
                name = item['name']
                model.delete_system_info(name)
            # reset to values in config
            app_globals.reset()
            h.redirect_to(controller='admin', action='config')

        return base.render('admin/confirm_reset.html')

    def config(self):

        items = self._get_config_form_items()
        data = request.POST
        if 'save' in data:
            #check against csrf attacks
            custom_base.csrf_check(self)
            try:
                # really?
                data_dict = logic.clean_dict(
                    dict_fns.unflatten(
                        logic.tuplize_dict(
                            logic.parse_params(
                                request.POST, ignore_keys=CACHE_PARAMETERS))))

                del data_dict['save']

                data = logic.get_action('config_option_update')(
                    {'user': c.user}, data_dict)
            except logic.ValidationError, e:
                errors = e.error_dict
                error_summary = e.error_summary
                vars = {'data': data, 'errors': errors,
                        'error_summary': error_summary, 'form_items': items}
                return base.render('admin/config.html', extra_vars=vars)

            h.redirect_to(controller='admin', action='config')

        schema = logic.schema.update_configuration_schema()
        data = {}
        for key in schema:
            data[key] = config.get(key)

        vars = {'data': data, 'errors': {}, 'form_items': items}
        return base.render('admin/config.html',
                           extra_vars=vars)