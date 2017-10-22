import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit


class CustomHomePlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IRoutes, inherit=True)

    # IConfigurer
    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'customhome')

    ## IRoutes
    def before_map(self, map):

        map.connect('home', '/',
                    controller='ckanext.customhome.customhome:CustomHomeController',
                    action='index')
        map.connect('terms', '/terms',
                    controller='ckanext.customhome.customhome:CustomHomeController',
                    action='terms')

        return map
