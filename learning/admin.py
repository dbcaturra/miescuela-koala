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

from django.contrib import admin
from django.contrib.admin import TabularInline, ModelAdmin

from learning.forms import CourseUpdateAdminForm, ResourceAdminUpdateForm
from learning.models import Course, Activity, CourseActivity, CourseCollaborator, Resource, RegistrationOnCourse


class CourseActivityInline(TabularInline):
    model = CourseActivity
    extra = 0


class CourseCollaboratorsInline(TabularInline):
    model = CourseCollaborator
    readonly_fields = ('created', 'updated', )
    extra = 0


class RegistrationOnCourseInline(TabularInline):
    model = RegistrationOnCourse
    readonly_fields = ('created', 'updated', 'self_registration')
    extra = 0


@admin.register(Activity)
class ActivityAdmin(ModelAdmin):
    model = Activity
    list_display = ('id', 'name', 'author', 'published', 'updated')
    list_display_links = ('id', 'name')
    readonly_fields = ('slug',)


@admin.register(Course)
class CourseAdmin(ModelAdmin):
    """
     Inheriting from GuardedModelAdmin just adds access to per-object
     permission management tools. This can be replaced by ModelAdmin at any
     time.
    """

    form = CourseUpdateAdminForm
    list_display = ('id', 'name', 'state', 'author', 'published', 'updated')
    list_display_links = ('id', 'name')
    list_filter = ('published', 'state')
    readonly_fields = ('slug',)

    inlines = [
        RegistrationOnCourseInline,
        CourseCollaboratorsInline,
        CourseActivityInline,
    ]

    def save_formset(self, request, form, formset, change):
        super(CourseAdmin, self).save_formset(request, form, formset, change)
        # When CourseActivity objects are added, they may not be in proper order, or with gaps
        # between ranks. Calling save again will ensure they are ordered properly
        form.instance.reorder_course_activities()


@admin.register(Resource)
class ResourceAdmin(ModelAdmin):
    form = ResourceAdminUpdateForm
    list_display = ('id', 'name', 'type', 'author', 'published', 'updated')
    list_display_links = ('id', 'name')
    list_filter = ('type', 'published')
    readonly_fields = ('slug',)
