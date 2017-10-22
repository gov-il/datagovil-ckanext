import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit


class CustomPackagePlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IRoutes, inherit=True)

    # IConfigurer
    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'custompackage')


    ## IRoutes
    def before_map(self, map):
        map.connect('add dataset', '/dataset/new',
                    controller='ckanext.custompackage.custompackage:CustomPackageController',
                    action='new')
        map.connect('/dataset',
                    controller='ckanext.custompackage.custompackage:CustomPackageController',
                    action='search')
        map.connect('/dataset/{id}',
                    controller='ckanext.custompackage.custompackage:CustomPackageController',
                    action='read')
        map.connect('/dataset/new_resource/{id}',
                    controller='ckanext.custompackage.custompackage:CustomPackageController',
                    action='new_resource')
        map.connect('/dataset/{id}/resource/{resource_id}',
                    controller='ckanext.custompackage.custompackage:CustomPackageController',
                    action='resource_read')
        map.connect('/dataset/{id}/resource/{resource_id}/download',
                    controller='ckanext.custompackage.custompackage:CustomPackageController',
                    action='resource_download')
        map.connect('/dataset/{id}/resource/{resource_id}/download/{filename}',
                    controller='ckanext.custompackage.custompackage:CustomPackageController',
                    action='resource_download')
        map.connect('resource_edit', '/dataset/{id}/resource_edit/{resource_id}',
                    controller='ckanext.custompackage.custompackage:CustomPackageController',
                    action='resource_edit', ckan_icon='edit')
        map.connect('dataset_edit', '/dataset/edit/{id}', action='edit',
                    controller='ckanext.custompackage.custompackage:CustomPackageController',
                    ckan_icon='edit')
        map.connect('/dataset/{id}/resource_delete/{resource_id}',
                    controller='ckanext.custompackage.custompackage:CustomPackageController',
                    action='resource_delete')
        map.connect('/dataset/delete/{id}',
                    controller='ckanext.custompackage.custompackage:CustomPackageController',
                    action='delete')
        map.connect('/dataset/{id}/resource/{resource_id}/embed',
                    controller='ckanext.custompackage.custompackage:CustomPackageController',
                    action='resource_embedded_dataviewer')
        map.connect('/dataset/{id}/resource/{resource_id}/viewer',
                    controller='ckanext.custompackage.custompackage:CustomPackageController',
                    action='resource_embedded_dataviewer', width="960",
                    height="800")
        map.connect('views', '/dataset/{id}/resource/{resource_id}/views',
                    controller='ckanext.custompackage.custompackage:CustomPackageController',
                    action='resource_views', ckan_icon='reorder')
        map.connect('new_view', '/dataset/{id}/resource/{resource_id}/new_view',
                    controller='ckanext.custompackage.custompackage:CustomPackageController',
                    action='edit_view', ckan_icon='edit')
        map.connect('edit_view',
                    '/dataset/{id}/resource/{resource_id}/edit_view/{view_id}',
                    controller='ckanext.custompackage.custompackage:CustomPackageController',
                    action='edit_view', ckan_icon='edit')
        map.connect('resource_view',
                    '/dataset/{id}/resource/{resource_id}/view/{view_id}',
                    controller='ckanext.custompackage.custompackage:CustomPackageController',
                    action='resource_view')
        map.connect('/dataset/{id}/resource/{resource_id}/view/',
                    controller='ckanext.custompackage.custompackage:CustomPackageController',
                    action='resource_view')
        map.connect('/dataset/{id}/resource/{resource_id}/preview',
                    controller='ckanext.custompackage.custompackage:CustomPackageController',
                    action='resource_datapreview')
        return map