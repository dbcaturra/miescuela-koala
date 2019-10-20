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

from django.urls import path, include

import learning.views.activity as activity_views
import learning.views.course as course_views
import learning.views.resource as resource_views
from learning.views.views import WelcomePageView

app_name = 'learning'  # Application namespace

###############
# Course ULRs #
###############

course_details_urlpatterns = [
    # The course itself
    path('', course_views.CourseDetailView.as_view(), name='course/detail'),

    # Access courses similar to the current one
    path('similar/', course_views.CourseDetailSimilarView.as_view(), name="course/detail/similar"),

    # Registration on a course, for a student
    path('register', course_views.CourseRegisterView.as_view(), name="course/detail/register"),
    path('unregister', course_views.CourseUnregisterView.as_view(), name="course/detail/unregister"),

    # Activities: view (as student and as teacher), add, unlink and delete from a course
    path('activities', course_views.CourseDetailActivitiesView.as_view(), name="course/detail/activities"),
    path(
        'activity/<slug:activity_slug>/',
        course_views.CourseDetailActivitiesView.as_view(),
        name="course/detail/activity"
    ),
    path(
        'activity/<slug:activity_slug>/resource/<slug:resource_slug>',
        course_views.CourseDetailActivityResourceView.as_view(),
        name="course/detail/activities/resource"
    ),
    path('activity/up', course_views.activity_on_course_up_view, name="course/detail/activity/up"),
    path('activity/add', course_views.ActivityCreateOnCourseView.as_view(), name="course/detail/activity/add"),
    path('activity/attach', course_views.ActivityAttachOnCourseView.as_view(), name="course/detail/activity/attach"),
    path('activity/unlink', course_views.activity_on_course_unlink_view, name="course/detail/activity/unlink"),
    path('activity/delete', course_views.activity_on_course_delete_view, name="course/detail/activity/delete"),

    # Collaborators: view, add and delete from a course
    path('collaborators', course_views.CourseDetailCollaboratorsView.as_view(), name="course/detail/collaborators"),
    path('collaborator/add', course_views.CourseDetailCollaboratorsAddView.as_view(), name="course/detail/collaborator/add"),
    path('collaborator/update', course_views.CourseDetailCollaboratorsChangeView.as_view(), name="course/detail/collaborator/change"),
    path('collaborator/delete', course_views.CourseDetailCollaboratorsDeleteView.as_view(), name="course/detail/collaborator/delete"),

    # Students: view, add and delete from a course
    path('students/', course_views.CourseDetailStudentsView.as_view(), name="course/detail/students"),
    path('students/add', course_views.CourseDetailStudentsAddView.as_view(), name="course/detail/students/add"),
    path('students/delete', course_views.CourseDetailStudentsDeleteView.as_view(), name="course/detail/students/delete"),
]

course_urlpatterns = [
    path('study', course_views.CourseAsStudentListView.as_view(), name='course/my'),
    path('teach/', course_views.CourseAsTeacherListView.as_view(), name="course/teaching"),
    path('search/', course_views.CourseSearchView.as_view(), name="course/search"),

    # Course view, add, update and delete views
    path('add/', course_views.CourseCreateView.as_view(), name='course/add'),
    path('update/<slug:slug>/', course_views.CourseUpdateView.as_view(), name='course/update'),
    path('delete/<slug:slug>/', course_views.CourseDeleteView.as_view(), name='course/delete'),
    path('detail/<slug:slug>/', include(course_details_urlpatterns)),
]

#################
# Activity ULRs #
#################

activity_details_urlpatterns = [
    # The activity itself
    path('', activity_views.ActivityDetailView.as_view(), name='activity/detail'),

    # Add a new resource on this activity
    path('resource/add', activity_views.ActivityCreateResourceView.as_view(), name="activity/detail/resource/add"),
    path('resource/attach', activity_views.ResourceAttachOnActivityView.as_view(), name="activity/detail/resource/attach"),
    path('resource/unlink', activity_views.ResourceUnlinkOnActivityView.as_view(), name="activity/detail/resource/unlink"),
    path('resource/detail/<slug:resource_slug>', activity_views.ResourceOnActivityDetailView.as_view(), name="activity/resource/detail"),

    # By which courses the activity is used
    path('usage/', activity_views.ActivityDetailUsageView.as_view(), name="activity/detail/usage"),

    # Activities similar to the current one
    path('similar/', activity_views.ActivityDetailSimilarView.as_view(), name="activity/detail/similar"),
]

activity_urlpatterns = [
    path('', activity_views.ActivityListView.as_view(), name="activity/my"),

    # Activity view, add, update and delete views
    path('add/', activity_views.ActivityCreateView.as_view(), name='activity/add'),
    path('delete/<slug:slug>/', activity_views.ActivityDeleteView.as_view(), name='activity/delete'),
    path('update/<slug:slug>/', activity_views.ActivityUpdateView.as_view(), name='activity/update'),
    path('detail/<slug:slug>/', include(activity_details_urlpatterns)),
]

#################
# Resource ULRs #
#################

resource_details_urlpatterns = [
    # The resource itself
    path('', resource_views.ResourceDetailView.as_view(), name="resource/detail"),

    # By which activities the activity is used
    path('usage/', resource_views.ResourceDetailUsageView.as_view(), name="resource/detail/usage"),

    # Resources similar to the current one
    path('similar/', resource_views.ResourceDetailSimilarView.as_view(), name="resource/detail/similar"),
]

resource_urlpatterns = [
    path('', resource_views.ResourceListView.as_view(), name="resource/my"),

    # Resource view, add, update and delete views
    path('add/', resource_views.ResourceCreateView.as_view(), name='resource/add'),

    path('delete/<slug:slug>/', resource_views.ResourceDeleteView.as_view(), name='resource/delete'),
    path('update/<slug:slug>/', resource_views.ResourceUpdateView.as_view(), name='resource/update'),
    path('detail/<slug:slug>/', include(resource_details_urlpatterns)),
]

####################
# Application URLs #
####################
urlpatterns = [
    path('', WelcomePageView.as_view(), name='index'),
    path('course/', include(course_urlpatterns)),
    path('activity/', include(activity_urlpatterns)),
    path('resource/', include(resource_urlpatterns))
]
