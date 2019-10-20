#
# Copyright (C) 2019 Guillaume Bernard <guillaume.bernard@koala-lms.org>
#
# This file is part of Koala LMS (Learning Management system)

# Koala LMS is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# We make an extensive use of the Django framework, https://www.djangoproject.com/
#
import markdown
from django import template
from django.contrib.auth import get_user_model
from django.template.defaultfilters import stringfilter
from django.utils.html import strip_tags, format_html
from django.utils.translation import gettext_lazy as _

from learning.forms import CourseCollaboratorUpdateRoleForm
from learning.models import CollaboratorRole, CourseAccess, ResourceType, CourseCollaborator, ActivityAccess, \
    ActivityReuse, ResourceAccess, ResourceReuse, Licences, Duration, Course
from learning.models import CourseState
from learning.permissions import ObjectPermissionManagerMixin

register = template.Library()


##################
# Course filters #
##################

@register.filter
@stringfilter
def get_course_permission_icon(value):  # pragma: no cover
    button_template = """
        <span class="btn btn-sm btn-{btn_class}" data-toggle="tooltip" data-placement="top" title="{btn_tooltip}">
            <i class="fa fa-{icon}"></i>
        </span>
    """
    filled_button = ""
    if value == "view_course":
        filled_button = format_html(button_template, icon="eye", btn_class="primary", btn_tooltip=_("Can view the course"))
    elif value == "change_course":
        filled_button = format_html(button_template, icon="pen", btn_class="warning", btn_tooltip=_("Change change the course"))
    elif value == "delete_course":
        filled_button = format_html(button_template, icon="trash", btn_class="danger", btn_tooltip=_("Can delete the course"))
    return filled_button


@register.filter
@stringfilter
def get_course_state_badge_type(value):  # pragma: no cover
    if value == CourseState.DRAFT.name:
        badge_type = 'info'
    elif value == CourseState.PUBLISHED.name:
        badge_type = 'success'
    elif value == CourseState.ARCHIVED.name:
        badge_type = 'warning'
    else:
        badge_type = 'light'
    return badge_type


@register.filter
@stringfilter
def get_course_state_badge_title(value):  # pragma: no cover
    if value == CourseState.DRAFT.name:
        badge_title = _("This course is a draft. It is not visible by others except collaborators and no one can register.")
    elif value == CourseState.PUBLISHED.name:
        badge_title = _("This course is published. Every change will be immediately available.")
    elif value == CourseState.ARCHIVED.name:
        badge_title = _("This course is archived. Therefore, it is read-only. No one can register to the course anymore.")
    else:
        badge_title = ""
    return badge_title


@register.filter
@stringfilter
def get_course_role_badge_type(value):  # pragma: no cover
    if value == CollaboratorRole.NON_EDITOR_TEACHER.name:
        badge_type = "secondary"
    elif value == CollaboratorRole.TEACHER.name:
        badge_type = "primary"
    elif value == CollaboratorRole.OWNER.name:
        badge_type = "success"
    else:
        badge_type = "info"
    return badge_type


@register.filter
@stringfilter
def get_course_access_badge_title(value):  # pragma: no cover
    if value == CourseAccess.PRIVATE.name:
        badge_title = _("This course is private. You’re the only one able to access it.")
    elif value == CourseAccess.COLLABORATORS_ONLY.name:
        badge_title = _("Access to this course is restricted to collaborators only.")
    elif value == CourseAccess.STUDENTS_ONLY.name:
        badge_title = _("Access to this course is restricted to registered students only.")
    elif value == CourseAccess.PUBLIC.name:
        badge_title = _("This course is public. Everyone can view it, but edition is restricted to its author and his collaborators.")
    else:
        badge_title = ""
    return badge_title


@register.filter
@stringfilter
def get_course_access_badge_type(value):  # pragma: no cover
    if value == CourseAccess.PUBLIC.name:
        badge_type = "success"
    elif value == CourseAccess.PRIVATE.name:
        badge_type = "danger"
    elif value == CourseAccess.COLLABORATORS_ONLY.name:
        badge_type = "primary"
    elif value == CourseAccess.STUDENTS_ONLY.name:
        badge_type = "secondary"
    else:
        badge_type = "info"
    return badge_type


@register.filter
@stringfilter
def get_course_role_badge_title(value):  # pragma: no cover
    if value == CollaboratorRole.NON_EDITOR_TEACHER.name:
        badge_title = _("You can view course details, students and collaborators but without edition permissions.")
    elif value == CollaboratorRole.TEACHER.name:
        badge_title = _("You can add, change, delete elements within the course, but cannot delete it.")
    elif value == CollaboratorRole.OWNER.name:
        badge_title = _("You can do anything on the course, without restriction.")
    else:
        badge_title = ""
    return badge_title


####################
# Resource filters #
####################

@register.filter
@stringfilter
def get_resource_type_icon(value):  # pragma: no cover
    try:
        return ResourceType[value].icon
    except KeyError:
        return ""


@register.filter
@stringfilter
def get_resource_access_badge_type(value):  # pragma: no cover
    if value == ResourceAccess.PUBLIC.name:
        badge_type = "success"
    elif value == ResourceAccess.EXISTING_ACTIVITIES.name:
        badge_type = "warning"
    elif value == ResourceAccess.PRIVATE.name:
        badge_type = "danger"
    else:
        badge_type = "info"
    return badge_type


@register.filter
@stringfilter
def get_resource_access_badge_title(value):  # pragma: no cover
    if value == ResourceAccess.PUBLIC.name:
        badge_title = _("This resource is public. Anyone with access can view it.")
    elif value == ResourceAccess.EXISTING_ACTIVITIES.name:
        badge_title = _("This resource can only be viewed in activities. This means that if you can view the activity "
                        "that use this resource, you can view this resource.")
    elif value == ResourceAccess.PRIVATE.name:
        badge_title = _("This resource is private. The author is the only one able to view it.")
    else:
        badge_title = ""
    return badge_title


@register.filter
@stringfilter
def get_resource_reuse_badge_type(value):  # pragma: no cover
    if value == ResourceReuse.NO_RESTRICTION.name:
        badge_type = "success"
    elif value == ResourceReuse.ONLY_AUTHOR.name:
        badge_type = "warning"
    elif value == ResourceReuse.NON_REUSABLE.name:
        badge_type = "danger"
    else:
        badge_type = "info"
    return badge_type


@register.filter
@stringfilter
def get_resource_reuse_badge_title(value):  # pragma: no cover
    if value == ResourceReuse.NO_RESTRICTION.name:
        badge_title = _("This resource can be used in other activities without restriction.")
    elif value == ResourceReuse.ONLY_AUTHOR.name:
        badge_title = _("This resource can only be reused by its author.")
    elif value == ResourceReuse.NON_REUSABLE.name:
        badge_title = _("This resource cannot be reused by anyone.")
    else:
        badge_title = "info"
    return badge_title


@register.filter
@stringfilter
def get_resource_licence_badge_type(value):  # pragma: no cover
    licence = Licences[value]
    if licence < Licences.CC_BY_NC:
        badge_type = "success"
    elif licence < Licences.CC_BY_NC_ND:
        badge_type = "warning"
    else:
        badge_type = "danger"
    return badge_type


@register.filter
@stringfilter
def get_resource_licence_badge_title(value):  # pragma: no cover
    licence = Licences[value]
    if licence < Licences.CC_BY_NC:
        badge_title = _("This resource is distributed under a licence that allow others to reuse it freely.")
    elif licence < Licences.CC_BY_NC_ND:
        badge_title = _("Reusing this resource in an activity is limited to some conditions.")
    else:
        badge_title = _("This resource cannot be reused by anyone except its author.")
    return badge_title


@register.filter
@stringfilter
def get_resource_duration_badge_type(value):  # pragma: no cover
    duration = Duration[value]
    if duration < Duration.FIFTEEN_OR_LESS:
        badge_type = "success"
    elif duration < Duration.TWENTY_FIVE_OR_LESS:
        badge_type = "warning"
    else:
        badge_type = "danger"
    return badge_type


@register.filter
@stringfilter
def get_resource_duration_badge_title(value):  # pragma: no cover
    duration = Duration[value]
    if duration < Duration.FIFTEEN_OR_LESS:
        badge_title = _("Consulting this resource takes little time.")
    elif duration < Duration.TWENTY_FIVE_OR_LESS:
        badge_title = _("Consulting this resources takes a little more time.")
    elif duration == Duration.THIRTY_OR_MORE:
        badge_title = _("Consulting this resources takes a lot of time.")
    elif duration == Duration.NOT_SPECIFIED:
        badge_title = _("The author of this resource did not indicate how much time is necessary to consult the resource.")
    else:
        badge_title = ""
    return badge_title


####################
# Activity filters #
####################

@register.filter
@stringfilter
def get_activity_access_badge_type(value):  # pragma: no cover
    if value == ActivityAccess.PUBLIC.name:
        badge_type = "success"
    elif value == ActivityAccess.EXISTING_COURSES.name:
        badge_type = "warning"
    elif value == ActivityAccess.PRIVATE.name:
        badge_type = "danger"
    else:
        badge_type = "info"
    return badge_type


@register.filter
@stringfilter
def get_activity_access_badge_title(value):  # pragma: no cover
    if value == ActivityAccess.PUBLIC.name:
        badge_title = _("This activity is public. Anyone with access can view it.")
    elif value == ActivityAccess.EXISTING_COURSES.name:
        badge_title = _("This activity can only be view in courses that already use it.")
    elif value == ActivityAccess.PRIVATE.name:
        badge_title = _("This activity is private. You are the only one able to view it.")
    else:
        badge_title = ""
    return badge_title


@register.filter
@stringfilter
def get_activity_reuse_badge_type(value):  # pragma: no cover
    if value == ActivityReuse.NO_RESTRICTION.name:
        badge_type = "success"
    elif value == ActivityReuse.ONLY_AUTHOR.name:
        badge_type = "warning"
    elif value == ActivityReuse.NON_REUSABLE.name:
        badge_type = "danger"
    else:
        badge_type = "info"
    return badge_type


@register.filter
@stringfilter
def get_activity_reuse_badge_title(value):  # pragma: no cover
    if value == ActivityReuse.NO_RESTRICTION.name:
        badge_title = _("This activity can be used in other courses without restriction.")
    elif value == ActivityReuse.ONLY_AUTHOR.name:
        badge_title = _("This activity can only be reused by its author.")
    elif value == ActivityReuse.NON_REUSABLE.name:
        badge_title = _("This activity cannot be reused by anyone.")
    else:
        badge_title = "info"
    return badge_title


#################
# Other filters #
#################
@register.filter
@stringfilter
def render_markdown(value):
    """
    FIXME: This can be use to generate XSS attacks. Putting something like
    <script>window.location.replace("http://koala-lms.org");</script> may work well.
    At least, setting up a Content Security Policy to disable inline-script is required.
    Below is a little workaround, I do not know how secure it is yet.
    """

    try:
        markdown_rendering = markdown.markdown(value)
        if "script" in markdown_rendering:
            return strip_tags(markdown_rendering)
        return markdown_rendering
    except ImportError:
        return value


#################
# Template tags #
#################

@register.simple_tag
def get_course_activity_previous_page(paginator, current_page):  # pragma: no cover
    return paginator.get_page(current_page - 1)


@register.simple_tag
def get_course_activity_next_page(paginator, current_page):  # pragma: no cover
    return paginator.get_page(current_page + 1)


@register.simple_tag
def get_object_perms(instance: ObjectPermissionManagerMixin, user: get_user_model()):  # pragma: no cover
    """
    Call the get_user_perms method of the instance

    :param instance: an instance of a concrete object implement ObjectPermissionManagerMixin interface
    :type instance: ObjectPermissionManagerMixin
    :param user: the user for which to get the permissions
    :type user: get_user_model()
    :return: the set of permissions, relative to the object
    :rtype: set
    """
    perms = set()
    try:
        perms = instance.get_user_perms(user)
    except AttributeError:
        pass
    return perms


@register.simple_tag
def get_course_collaborator_object(course: Course, user: get_user_model()):  # pragma: no cover
    """
    Get the course collaborator object from a course and a specific user.

    :param course: the course on which the user collaborates
    :type: Course
    :param user: the user that collaborates on the course
    :type user: get_user_model()
    :return: the course collaborator object
    :rtype: CourseCollaborator
    """
    return CourseCollaborator.objects.filter(course=course, collaborator=user).first()


@register.simple_tag
def get_collaborator_role_form(course_collaborator: CourseCollaborator):  # pragma: no cover
    """
    Get the course CourseCollaboratorUpdateRoleForm, filled with initial values from the CourseCollaborator parameter.

    :param course_collaborator: the collaborator to use to populate initial values
    :type course_collaborator: CourseCollaborator
    :return: a form used to update the collaborator role
    :rtype: CourseCollaboratorUpdateRoleForm
    """
    return CourseCollaboratorUpdateRoleForm(
        initial={
            'collaborator': course_collaborator.collaborator,
            'course': course_collaborator.course,
            'role': course_collaborator.role
        }
    )


@register.simple_tag
def relative_url(value, field_name, url_encode=None):
    """
    This snippet comes from the website simpleifbetterthancomplex.com and was made by Vitor Freitas, as part of his
    article “Dealing with querystring parameters” (published on 22th 08/2016, read the 12/05/2016)

    :param value: the parameter to add to the existing query string
    :param field_name: the name of the parameter
    :param url_encode: the existing query string
    :return: a new querystring with the new parameter.
    """
    url = '?{}={}'.format(field_name, value)
    if url_encode:
        querystring = url_encode.split('&')
        filtered_querystring = filter(lambda p: p.split('=')[0] != field_name, querystring)
        encoded_querystring = '&'.join(filtered_querystring)
        url = '{}&{}'.format(url, encoded_querystring)
    return url
