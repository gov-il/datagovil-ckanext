import ckan.controllers.organization as organization
import ckan.controllers.group as group
import ckan.lib.base as base
import ckan.lib.helpers as h
import ckan.logic as logic
import ckan.model as model
from ckan.common import OrderedDict, c, g, request, _
import ckanext.gov_theme.base as custom_base

render = base.render
abort = base.abort
NotAuthorized = logic.NotAuthorized
NotFound = logic.NotFound


class CustomOrganizationController(organization.OrganizationController, group.GroupController):

    def index(self):

        custom_base.g_analitics()

        group_type = self._guess_group_type()

        page = self._get_page_number(request.params) or 1
        items_per_page = 21

        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author, 'for_view': True,
                   'with_private': False}

        q = c.q = request.params.get('q', '')
        sort_by = c.sort_by_selected = request.params.get('sort')
        # default sort by number of organization's datasets
        if sort_by is None:
            sort_by = 'package_count desc'
        try:
            self._check_access('site_read', context)
        except NotAuthorized:
            abort(401, _('Not authorized to see this page'))

        # pass user info to context as needed to view private datasets of
        # orgs correctly
        if c.userobj:
            context['user_id'] = c.userobj.id
            context['user_is_admin'] = c.userobj.sysadmin

        data_dict_global_results = {
            'all_fields': False,
            'q': q,
            'sort': sort_by,
            'type': group_type or 'group',
        }
        global_results = self._action('group_list')(context,
                                                    data_dict_global_results)

        data_dict_page_results = {
            'all_fields': True,
            'q': q,
            'sort': sort_by,
            'type': group_type or 'group',
            'limit': items_per_page,
            'offset': items_per_page * (page - 1),
        }
        page_results = self._action('group_list')(context,
                                                  data_dict_page_results)

        c.page = h.Page(
            collection=global_results,
            page=page,
            url=h.pager_url,
            items_per_page=items_per_page,
        )

        c.page.items = page_results
        return render(self._index_template(group_type),
                      extra_vars={'group_type': group_type})

    def new(self, data=None, errors=None, error_summary=None):
        if data and 'type' in data:
            group_type = data['type']
        else:
            group_type = self._guess_group_type(True)
        if data:
            data['type'] = group_type

        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author,
                   'save': 'save' in request.params,
                   'parent': request.params.get('parent', None)}
        try:
            self._check_access('group_create', context)
        except NotAuthorized:
            abort(401, _('Unauthorized to create a group'))

        if context['save'] and not data:
            #check against csrf attacks
            custom_base.csrf_check(self)
            return self._save_new(context, group_type)

        data = data or {}
        if not data.get('image_url', '').startswith('http'):
            data.pop('image_url', None)

        errors = errors or {}
        error_summary = error_summary or {}
        vars = {'data': data, 'errors': errors,
                'error_summary': error_summary, 'action': 'new',
                'group_type': group_type}

        self._setup_template_variables(context, data, group_type=group_type)
        c.form = render(self._group_form(group_type=group_type),
                        extra_vars=vars)
        return render(self._new_template(group_type),
                      extra_vars={'group_type': group_type})

    def delete(self, id):
        group_type = self._ensure_controller_matches_group_type(id)

        if 'cancel' in request.params:
            self._redirect_to_this_controller(action='edit', id=id)

        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author}

        try:
            self._check_access('group_delete', context, {'id': id})
        except NotAuthorized:
            abort(401, _('Unauthorized to delete group %s') % '')

        try:
            if request.method == 'POST':
                #check against csrf attacks
                custom_base.csrf_check(self)
                self._action('group_delete')(context, {'id': id})
                if group_type == 'organization':
                    h.flash_notice(_('Organization has been deleted.'))
                elif group_type == 'group':
                    h.flash_notice(_('Group has been deleted.'))
                else:
                    h.flash_notice(_('%s has been deleted.')
                                   % _(group_type.capitalize()))
                self._redirect_to_this_controller(action='index')
            c.group_dict = self._action('group_show')(context, {'id': id})
        except NotAuthorized:
            abort(401, _('Unauthorized to delete group %s') % '')
        except NotFound:
            abort(404, _('Group not found'))
        return self._render_template('group/confirm_delete.html', group_type)


