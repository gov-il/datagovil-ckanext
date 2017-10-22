import ckan.controllers.group as group
import logging
import datetime
from urllib import urlencode

from pylons.i18n import get_lang

import ckan.lib.base as base
import ckan.lib.helpers as h
import ckan.lib.maintain as maintain
import ckan.lib.navl.dictization_functions as dict_fns
import ckan.logic as logic
import ckan.lib.search as search
import ckan.model as model
import ckan.authz as authz
import ckan.lib.plugins
import ckan.plugins as plugins
from ckan.common import OrderedDict, c, g, request, _
import ckanext.gov_theme.base as custom_base

log = logging.getLogger(__name__)

render = base.render
abort = base.abort

NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized
ValidationError = logic.ValidationError
check_access = logic.check_access
get_action = logic.get_action
tuplize_dict = logic.tuplize_dict
clean_dict = logic.clean_dict
parse_params = logic.parse_params

lookup_group_plugin = ckan.lib.plugins.lookup_group_plugin
lookup_group_controller = ckan.lib.plugins.lookup_group_controller


class CustomGroupController(group.GroupController):

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
