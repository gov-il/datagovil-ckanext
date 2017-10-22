import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit


class CustomOrganizationPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IRoutes, inherit=True)

    # IConfigurer
    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'customorganization')

    ## IRoutes
    def before_map(self, map):
        map.connect('organizations_index', '/organization',
                    controller='ckanext.customorganization.customorganization:CustomOrganizationController',
                    action='index'),
        map.connect('/organization/new',
                    controller='ckanext.customorganization.customorganization:CustomOrganizationController',
                    action='new'),
        map.connect('/organization/delete/{id}',
                    controller='ckanext.customorganization.customorganization:CustomOrganizationController',
                    action='delete')
        return map
