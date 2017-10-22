import re
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.lib.plugins import DefaultTranslation
import pylons.config as config
import urllib2, urllib, json
from ckan.common import _, request, c, response
import webhelpers.pylonslib.secure_form as auth_token
import ckanext.gov_theme.action as _action
import ckanext.gov_theme.auth as _auth
import ckanext.gov_theme.base as _base

import ckan.lib.formatters as formatters
from ckan.lib.helpers import date_str_to_datetime

def anti_csrf_hidden_field():
    hidden_field = auth_token.auth_token_hidden_field()
    return hidden_field


def is_back():
    value = config.get('ckan.gov_theme.is_back', False)
    return value


def tags_count():
    '''Return a sorted list of the groups with the most datasets.'''

    tags_translate = [ _('Transport'), _('Justice'), _('Energy Watter'), _('Environment'), _('Finance Economy'), _('Population'), _('Religion'),   _('Education Culture'),   _('Health Wellness'), _('Accommodation'), _('Tourism') ]

   #/api/action/package_search?fq=tags:"economy"
    tags_counter = []

   #Put the details into a dict.
    for num in range(1,11):
        homepage_tag_num = "homepage_tag"+str(num)
        homepage_tag = config.get(homepage_tag_num)
        homepage_tag_translate = _(homepage_tag)
        homepage_tag_translate.encode('utf-8')
        query = "tags:"+'"'+homepage_tag_translate+'"'
        dataset_dict = {
           'fq': query,
        }

        homepage_tag_icon_num = "homepage_tag_icon"+str(num)
        homepage_tag_icon = config.get(homepage_tag_icon_num)

        # Use the json module to dump the dictionary to a string for posting.
        data_string = urllib.quote(json.dumps(dataset_dict))
        package_search_api = config.get('ckan.site_url')+'/api/3/action/package_search'
        tag = urllib2.Request(package_search_api)
        # Make the HTTP request.
        response = urllib2.urlopen(tag, data_string)
        assert response.code == 200
        # Use the json module to load CKAN's response into a dictionary.
        response_dict = json.loads(response.read())
        tag_count = response_dict['result']['count']
        tags_counter.append(dict([('name', homepage_tag_translate), ('icon', homepage_tag_icon), ('count', tag_count)]))

    return tags_counter


def format_resource_items(items):
    ''' Take a resource item list and format nicely with blacklisting etc. '''
    blacklist = ['name','description','url','tracking_summary','format','position', 'is_local_resource']
    output = []
    translations = [ _('created') , _('format') ,_('has views') , _('last modified'),_('package id'),_('revision id'),
                     _('state'),_('url type') ,_('active') ,_('upload'), _('position') ]
    # regular expressions for detecting types in strings
    reg_ex_datetime = '^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{6})?$'
    reg_ex_int = '^-?\d{1,}$'
    reg_ex_float = '^-?\d{1,}\.\d{1,}$'
    for key, value in items:
        if not value or key in blacklist:
            continue
        # size is treated specially as we want to show in MiB etc
        if key == 'size':
            try:
                value = formatters.localised_filesize(int(value))
            except ValueError:
                # Sometimes values that can't be converted to ints can sneak
                # into the db. In this case, just leave them as they are.
                pass
        elif isinstance(value, basestring):
            # check if strings are actually datetime/number etc
            if re.search(reg_ex_datetime, value):
                datetime_ = date_str_to_datetime(value)
                value = formatters.localised_nice_date(datetime_)
            elif re.search(reg_ex_float, value):
                value = formatters.localised_number(float(value))
            elif re.search(reg_ex_int, value):
                value = formatters.localised_number(int(value))
        elif isinstance(value, int) or isinstance(value, float):
            value = formatters.localised_number(value)
        key = key.replace('_', ' ')
        key = _(key)

        output.append((key, value))
    return sorted(output, key=lambda x: x[0])


class Gov_ThemePlugin(plugins.SingletonPlugin, DefaultTranslation):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITranslation)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.IAuthFunctions)

    # IConfigurer
    def update_config(self, config):
        toolkit.add_template_directory(config, 'templates')
        toolkit.add_public_directory(config, 'public')
        toolkit.add_resource('fanstatic', 'gov_theme')

    #ITemplateHelpers
    def get_helpers(self):
        return {'is_back_site': is_back,
                'get_tags_count': tags_count,
                'token_hidden_field': anti_csrf_hidden_field, #for csrf hidden field
                'format_resource_items': format_resource_items,
               }
    #IActions
    def get_actions(self):
        return {'user_invite': _action.user_invite,
                'follow_user': _action.follow_user,
                'follow_dataset': _action.follow_dataset,
                'follow_group': _action.follow_group,
                'unfollow_user': _action.unfollow_user,
                'unfollow_dataset': _action.unfollow_dataset,
                'unfollow_group': _action.unfollow_group,
                'send_email_notifications': _action.send_email_notifications,
                'term_translation_update_many': _action.term_translation_update_many,
                'task_status_update_many': _action.task_status_update_many,
                'package_patch': _action.package_patch,
                'resource_patch': _action.resource_patch,
                'group_patch': _action.group_patch,
                'organization_patch': _action.organization_patch,

                'related_list':  _action.related_list,
                'member_list':  _action.member_list,
                'group_package_show':  _action.group_package_show,
                'resource_search':  _action.resource_search,
                'tag_search':  _action.tag_search,
                'term_translation_show':  _action.term_translation_show,
                'status_show':  _action.status_show,
                'user_activity_list':  _action.user_activity_list,
                'package_activity_list':  _action.package_activity_list,
                'group_activity_list':  _action.group_activity_list,
                'organization_activity_list':  _action.organization_activity_list,
                'recently_changed_packages_activity_list':  _action.recently_changed_packages_activity_list,
                'user_activity_list_html':  _action.user_activity_list_html,
                'package_activity_list_html':  _action.package_activity_list_html,
                'group_activity_list_html':  _action.group_activity_list_html,
                'organization_activity_list_html':  _action.organization_activity_list_html,
                'user_follower_count':  _action.user_follower_count,
                'dataset_follower_count':  _action.dataset_follower_count,
                'group_follower_count':  _action.group_follower_count,
                'organization_follower_count':  _action.organization_follower_count,
                '_follower_list':  _action._follower_list,
                'user_follower_list':  _action.user_follower_list,
                'dataset_follower_list':  _action.dataset_follower_list,
                'group_follower_list':  _action.group_follower_list,
                'organization_follower_list':  _action.organization_follower_list,
                'am_following_user':  _action.am_following_user,
                'am_following_dataset':  _action.am_following_dataset,
                'am_following_group':  _action.am_following_group,
                'followee_count':  _action.followee_count,
                'user_followee_count':  _action.user_followee_count,
                'dataset_followee_count':  _action.dataset_followee_count,
                'group_followee_count':  _action.group_followee_count,
                'followee_list':  _action.followee_list,
                'user_followee_list':  _action.user_followee_list,
                'dataset_followee_list':  _action.dataset_followee_list,
                'group_followee_list':  _action.group_followee_list,
                'dashboard_activity_list':  _action.dashboard_activity_list,
                'dashboard_activity_list_html':  _action.dashboard_activity_list_html,
                'dashboard_new_activities_count':  _action.dashboard_new_activities_count,
                'member_roles_list': _action.member_roles_list}

    #IAuthFunctions
    def get_auth_functions(self):
        return {'package_create': _auth.package_create,
                'resource_create': _auth.resource_create,
                'related_create': _auth.related_create,
                'resource_view_create': _auth.resource_view_create,
                'resource_create_default_resource_views': _auth.resource_create_default_resource_views,
                'package_create_default_resource_views': _auth.package_create_default_resource_views,
                'package_relationship_create': _auth.package_relationship_create,
                'group_create': _auth.group_create,
                'organization_create': _auth.organization_create,
                'rating_create': _auth.rating_create,
                'user_create': _auth.user_create,
                'user_invite': _auth.user_invite,
                'organization_member_create': _auth.organization_member_create,
                'group_member_create': _auth.group_member_create,
                'member_create': _auth.member_create,

                'package_update': _auth.package_update,
                'package_resource_reorder': _auth.package_resource_reorder,
                'resource_update': _auth.resource_update,
                'resource_view_update': _auth.resource_view_update,
                'resource_view_reorder': _auth.resource_view_reorder,
                'package_relationship_update': _auth.package_relationship_update,
                'group_update': _auth.group_update,
                'organization_update': _auth.organization_update,
                'related_update': _auth.related_update,
                'user_update': _auth.user_update,
                'user_generate_apikey': _auth.user_generate_apikey,
                'dashboard_mark_activities_old': _auth.dashboard_mark_activities_old,
                'bulk_update_private': _auth.bulk_update_private,
                'bulk_update_public': _auth. bulk_update_public,
                'bulk_update_delete': _auth.bulk_update_delete,

                'package_delete': _auth.package_delete,
                'resource_delete': _auth.resource_delete,
                'resource_view_delete': _auth.resource_view_delete,
                'related_delete': _auth.related_delete,
                'package_relationship_delete': _auth.package_relationship_delete,
                'group_delete': _auth.group_delete,
                'organization_delete': _auth.organization_delete,
                'group_member_delete': _auth.group_member_delete,
                'organization_member_delete': _auth.organization_member_delete,
                'member_delete': _auth.member_delete,

                'revision_list': _auth.revision_list,
                'group_revision_list': _auth.group_revision_list,
                'organization_revision_list': _auth.organization_revision_list,
                'package_revision_list': _auth.package_revision_list,
                'user_list': _auth.user_list,
                'revision_show': _auth.revision_show,
                'user_show': _auth.user_show,
                'task_status_show': _auth.task_status_show,
                'resource_status_show': _auth.resource_status_show
                }










