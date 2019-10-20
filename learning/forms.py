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
import os

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS
from django.forms import Form, Select
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _, gettext
from markdownx.fields import MarkdownxFormField

from learning import logger
from learning.models import Course, Activity, CourseState, CourseAccess, Resource, CollaboratorRole, \
    CourseCollaborator


class CustomClassesOnFormMixin(Form):
    custom_classes = ["form-control"]

    def __init__(self, *args, **kwargs):
        super(CustomClassesOnFormMixin, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, Select):
                field.widget.attrs.update({'class': 'custom-select'})
            else:
                field.widget.attrs.update({'class': 'form-control'})

    def clean(self):
        if not self.has_error(NON_FIELD_ERRORS):
            for field_name, field in self.fields.items():
                current_class = field.widget.attrs.get('class', str())
                if field_name in self.errors.as_data():
                    field.widget.attrs.update({'class': current_class + ' ' + 'is-invalid'})
                elif field_name in self.changed_data:
                    field.widget.attrs.update({'class': current_class + ' ' + 'is-valid'})


class FormWithMarkdownFieldMixin(forms.ModelForm):
    description = MarkdownxFormField(
        help_text=mark_safe(_('You can use the <a href="https://www.markdownguide.org/basic-syntax/" target="_blank">Markdown</a> syntax here.'))  # nosec
    )


################
# Course forms #
################
course_fields_for_author = ['name', 'description', 'state', 'access', 'language', 'registration_enabled', 'tags']


class CourseFormMixin(CustomClassesOnFormMixin, FormWithMarkdownFieldMixin, forms.ModelForm):

    def clean(self):
        # Check is registration is enabled on a draft course
        registration_enabled = self.cleaned_data.get('registration_enabled', None)
        state = self.cleaned_data.get('state', None)
        if state and registration_enabled:
            if registration_enabled and CourseState[state] == CourseState.DRAFT:
                raise ValidationError(
                    gettext("Registration is not possible on draft course.") + ' ' +
                    gettext("Change the status of the course if you wish to enable registration.")
                )
            if registration_enabled and CourseState[state] == CourseState.ARCHIVED:
                raise ValidationError(
                    gettext("Registration is no longer possible on an archived course.") + ' ' +
                    gettext("Change the status of the course if you wish to enable registration.")
                )

        # Having something published but without access does not have any purpose
        access = self.cleaned_data.get("access", None)
        if access and state:
            if CourseAccess[access] >= CourseAccess.COLLABORATORS_ONLY and CourseState[state] == CourseState.PUBLISHED:
                raise ValidationError(
                    gettext("Level access is collaborators only but course is published. It seems inconsistent.")
                )

        super().clean()

    class Meta:
        model = Course
        fields = ['name', 'description', 'state', 'author', 'access', 'registration_enabled', 'tags']


class CourseCreateForm(CourseFormMixin, forms.ModelForm):
    class Meta:
        model = Course
        fields = course_fields_for_author


class CourseUpdateFormForOwner(CourseFormMixin, forms.ModelForm):
    """
    Update a course as owner
    """

    class Meta:
        model = Course
        fields = course_fields_for_author


class CourseUpdateForm(CourseFormMixin, forms.ModelForm):
    """
    Update a course without being owner
    """

    class Meta:
        model = Course
        fields = ['name', 'description', 'state', 'tags']


class CourseCollaboratorUpdateRoleForm(CustomClassesOnFormMixin, forms.ModelForm):
    """
    Change the role of a collaborator on a course
    """

    class Meta:
        model = CourseCollaborator
        fields = ['role']


class CourseUpdateAdminForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = course_fields_for_author + ['author']


##################
# Activity forms #
##################
activity_fields_for_author = ['name', 'description', 'language', 'access', 'reuse', 'tags']


class ActivityFormMixin(CustomClassesOnFormMixin, FormWithMarkdownFieldMixin, forms.ModelForm):
    pass


class ActivityCreateForm(ActivityFormMixin):
    class Meta:
        model = Activity
        fields = activity_fields_for_author


class ActivityUpdateForm(ActivityFormMixin):
    class Meta:
        model = Activity
        fields = activity_fields_for_author


##################
# Resource forms #
##################
resource_fields_for_author = ['name', 'description', 'type', 'tags', 'language', 'licence', 'access', 'reuse', 'duration', 'media']


def delete_resource_media(resource, form_initial, form_changed_data, cleaned_data):
    """
    Delete the media file manually, as Django does not do this automatically.
    """
    if not cleaned_data.get('media'):  # Field is False, media should be removed
        os.remove(os.path.join(settings.MEDIA_ROOT, form_initial.get('media').name))

    if 'media' in form_changed_data and form_initial.get('media') and Resource.acceptable_media(cleaned_data.get('media')):
        try:
            os.remove(os.path.join(settings.MEDIA_ROOT, form_initial.get('media').name))
        except OSError as ex:
            logger.error("Deleting media for resource %(resource)s failed (%(cause)s)", {'resource': resource, 'cause': str(ex)})


class ResourceUpdateFormMixin(forms.ModelForm):
    pass


class ResourceCreateForm(CustomClassesOnFormMixin, FormWithMarkdownFieldMixin, forms.ModelForm):
    class Meta:
        model = Resource
        fields = resource_fields_for_author


class ResourceUpdateForm(CustomClassesOnFormMixin, FormWithMarkdownFieldMixin, ResourceUpdateFormMixin):

    class Meta:
        model = Resource
        fields = resource_fields_for_author

    def clean(self):
        delete_resource_media(self.instance, self.initial, self.changed_data, self.cleaned_data)


class ResourceAdminUpdateForm(ResourceUpdateFormMixin):
    """
    The admin form allows to change the resource author
    """
    class Meta:
        model = Resource
        fields = resource_fields_for_author + ['author']

    def clean(self):
        delete_resource_media(self.instance, self.initial, self.changed_data, self.cleaned_data)


######################################
# Forms to link users with resources #
######################################

class AddUserOn(CustomClassesOnFormMixin, forms.Form):
    """
    Add a user on an object. The available users are shown in the linked user_list element.
    """
    username = forms.CharField(
        label=_('Username'),
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={'list': 'user_list'})
    )


class AddStudentOnCourseForm(AddUserOn):
    """
    Adding a user on a course only requires the username.
    """


class AddCollaboratorOnCourseForm(AddUserOn):
    """
    When adding a collaborator on a course, the collaborator role is required.
    """
    roles = forms.ChoiceField(
        label=_('Role'),
        choices=[(role.name, role.value) for role in CollaboratorRole]
    )


###############
# Search form #
###############


class BasicSearchForm(CustomClassesOnFormMixin):
    query = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': _("A title, keywords, tags, topics…")})
    )
