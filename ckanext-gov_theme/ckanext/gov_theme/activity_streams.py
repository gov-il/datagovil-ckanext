
import ckan.lib.activity_streams as activity_streams




def get_snippet_actor(activity, detail):
    # return literal('''<span class="actor">%s</span>'''
    #     % (h.linked_user(activity['user_id'], 0, 30))
    #     )
     return ''



def activity_list_to_html(context, activity_stream, extra_vars):
    '''Return the given activity stream as a snippet of HTML.

    :param activity_stream: the activity stream to render
    :type activity_stream: list of activity dictionaries
    :param extra_vars: extra variables to pass to the activity stream items
        template when rendering it
    :type extra_vars: dictionary

    :rtype: HTML-formatted string

    '''
    activity_list = [] # These are the activity stream messages.
    for activity in activity_stream:
        detail = None
        activity_type = activity['activity_type']
        # Some activity types may have details.
        if activity_type in activity_streams.activity_stream_actions_with_detail:
            details = activity_streams.logic.get_action('activity_detail_list')(context=context,
                data_dict={'id': activity['id']})
            # If an activity has just one activity detail then render the
            # detail instead of the activity.
            if len(details) == 1:
                detail = details[0]
                object_type = detail['object_type']

                if object_type == 'PackageExtra':
                    object_type = 'package_extra'

                new_activity_type = '%s %s' % (detail['activity_type'],
                                            object_type.lower())
                if new_activity_type in activity_streams.activity_stream_string_functions:
                    activity_type = new_activity_type

        if not activity_type in activity_streams.activity_stream_string_functions:
            raise NotImplementedError("No activity renderer for activity "
                "type '%s'" % activity_type)

        if activity_type in activity_streams.activity_stream_string_icons:
            activity_icon = activity_streams.activity_stream_string_icons[activity_type]
        else:
            activity_icon = activity_streams.activity_stream_string_icons['undefined']

        activity_msg = activity_streams.activity_stream_string_functions[activity_type](context,
                activity)

        # Get the data needed to render the message.
        matches = activity_streams.re.findall('\{([^}]*)\}', activity_msg)
        data = {}
        for match in matches:
            snippet = activity_snippet_functions[match](activity, detail)
            data[str(match)] = snippet

        activity_list.append({'msg': activity_msg,
                              'type': activity_type.replace(' ', '-').lower(),
                              'icon': activity_icon,
                              'data': data,
                              'timestamp': activity['timestamp'],
                              'is_new': activity.get('is_new', False)})
    extra_vars['activities'] = activity_list
    return activity_streams.literal(activity_streams.base.render('activity_streams/activity_stream_items.html',
        extra_vars=extra_vars))


# A dictionary mapping activity snippets to functions that expand the snippets.
activity_snippet_functions = {
    'actor': get_snippet_actor,
    'user': activity_streams.get_snippet_user,
    'dataset': activity_streams.get_snippet_dataset,
    'tag': activity_streams.get_snippet_tag,
    'group': activity_streams.get_snippet_group,
    'organization': activity_streams.get_snippet_organization,
    'extra': activity_streams.get_snippet_extra,
    'resource': activity_streams.get_snippet_resource,
    'related_item': activity_streams.get_snippet_related_item,
    'related_type': activity_streams.get_snippet_related_type,
}