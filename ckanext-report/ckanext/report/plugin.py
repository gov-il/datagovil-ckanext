"""
CKAN report Extension
"""
import os
from logging import getLogger
import ckan.plugins as p
from ckanext.report.auth import send_report
import ckan.plugins.toolkit as toolkit
from ckan.lib.plugins import DefaultTranslation


log = getLogger(__name__)

class reportPlugin(p.SingletonPlugin, DefaultTranslation):
    p.implements(p.ITranslation)
    """
    CKAN report Extension
    """
    p.implements(p.IRoutes, inherit=True)
    p.implements(p.IConfigurer)
    p.implements(p.IAuthFunctions)

    ## IConfigurer
    def update_config(self, config):
        p.toolkit.add_template_directory(config, 'theme/templates')
        p.toolkit.add_public_directory(config, 'theme/public')
        p.toolkit.add_resource('theme/public', 'ckanext-report')

    ## IRoutes
    def before_map(self, map):

        # Add controller for KE EMu specimen records
        map.connect('report_form', '/report',
                    controller='ckanext.report.controllers.report:reportController',
                    action='form')

        # Add AJAX request handler
        map.connect('report_ajax_submit', '/report/ajax',
                    controller='ckanext.report.controllers.report:reportController',
                    action='ajax_submit')

        return map

    ## IAuthFunctions
    def get_auth_functions(self):
        return {'send_report': send_report}

