import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit


class CustomUserPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IRoutes, inherit=True)



    # IConfigurer
    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'customuser')


    ## IRoutes
    def before_map(self, map):

        map.connect('/user/edit',
                    controller='ckanext.customuser.customuser:CustomUserController',
                    action='edit')
        map.connect('user_edit', '/user/edit/{id:.*}',
                    controller='ckanext.customuser.customuser:CustomUserController',
                    action='edit')
        map.connect('register', '/user/register',
                    controller='ckanext.customuser.customuser:CustomUserController',
                    action='register')
        map.connect('user_delete', '/user/delete/{id}',
                    controller='ckanext.customuser.customuser:CustomUserController',
                    action='delete')
        map.connect('login', '/user/login',
                    controller='ckanext.customuser.customuser:CustomUserController',
                    action='login')
        map.connect('/user/_logout',
                    controller='ckanext.customuser.customuser:CustomUserController',
                    action='logout')
        map.connect('/user/reset',
                    controller='ckanext.customuser.customuser:CustomUserController',
                    action='request_reset')

        return map
