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
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Q
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, CreateView, DeleteView, UpdateView, FormView, TemplateView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import ProcessFormView

from learning.exc import LearningError
from learning.forms import ActivityCreateForm, ActivityUpdateForm, ResourceCreateForm, BasicSearchForm
from learning.models import Activity, Resource, ResourceReuse
from learning.views.helpers import PaginatorFactory, SearchQuery, InvalidFormHandlerMixin


class ActivityDetailMixin(PermissionRequiredMixin, SingleObjectMixin):
    """
    A mixin to provide united context or functions to resource views.

    .. caution:: Viewing an activity requires the **view_activity** permission.
    """
    model = Activity
    template_name = "learning/activity/detail.html"

    def has_permission(self):
        # noinspection PyUnresolvedReferences
        return self.get_object().user_can_view(self.request.user)


class ActivityDetailView(ActivityDetailMixin, PermissionRequiredMixin, DetailView):
    def handle_no_permission(self):
        messages.error(self.request, _("You do not have the required permissions to access this activity."))
        return super().handle_no_permission()


class ActivityCreateView(LoginRequiredMixin, InvalidFormHandlerMixin, CreateView):
    model = Activity
    form_class = ActivityCreateForm
    template_name = "learning/activity/add.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, _('Activity “%(activity)s” created.') % {'activity': form.instance.name})
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("learning:activity/detail", kwargs={'slug': self.object.slug})


class ActivityUpdateView(LoginRequiredMixin, InvalidFormHandlerMixin, ActivityDetailMixin, UpdateView):
    """
    Update an existing activity

    .. caution:: Delete an activity requires the **change_activity** permission.
    """
    form_class = ActivityUpdateForm
    template_name = "learning/activity/details/change.html"

    def has_permission(self):
        return self.get_object().user_can_change(self.request.user)

    def handle_no_permission(self):
        messages.error(self.request, _("You do not have the required permissions to change this activity."))
        return super().handle_no_permission()

    def form_valid(self, form):
        if form.has_changed():
            messages.success(self.request, _('The activity “%(activity)s” has been updated.') % {'activity': self.object.name})
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('learning:activity/detail', kwargs={'slug': self.object.slug})


class ActivityDeleteView(LoginRequiredMixin, ActivityDetailMixin, DeleteView):
    """
    Delete an activity

    .. caution:: Delete an activity requires the **delete_activity** permission.
    """
    success_url = reverse_lazy('learning:activity/my')
    template_name = 'learning/activity/delete.html'

    def has_permission(self):
        return self.get_object().user_can_delete(self.request.user)

    def handle_no_permission(self):
        messages.error(self.request, _("You do not have the required permissions to delete this activity."))
        return super().handle_no_permission()

    def get_success_url(self):
        messages.success(self.request, _('The activity ”%(activity)s” has been deleted') % {'activity': self.object.name})
        return super().get_success_url()


class ActivityListView(LoginRequiredMixin, TemplateView):
    """
    List the activities that the logged-on user is the author of.

    When action is performed, the context is filled with:

    * **form**: a BasicSearchForm instance, allowing you to search for specific words
    * **activities_page_obj,activities_has_obj**…: what is given by the PaginatorFactory to display activities owned \
                                                   by the user
    * **search_page_obj,search_has_obj**…: same but for the resource search result.
    """
    model = Activity
    template_name = "learning/activity/my_list.html"
    form_class = BasicSearchForm  # This is used to perform the search

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Activities by the logged-on user
        context.update(
            PaginatorFactory.get_paginator_as_context(
                Activity.objects.filter(author=self.request.user).all(),
                self.request.GET, prefix="activities", nb_per_page=9
            )
        )
        # Resources that match the query
        context.update(SearchQuery.search_query_as_context(Activity, self.request.GET))
        return context


class ActivityDetailUsageView(LoginRequiredMixin, ActivityDetailView):
    """
    View which courses use this activity.

    When action is performed, the context is filled with:

    * **page_obj,has_obj**…: what is given by the PaginatorFactory to display courses that use this activity.

    .. caution:: Viewing courses that use this activities requires the **view_usage_activity** permission.
    """
    template_name = "learning/activity/details/usage.html"

    def has_permission(self):
        return self.get_object().user_can("view_usage", self.request.user) and super().has_permission()

    def handle_no_permission(self):
        messages.error(self.request, _("You do not have the required permissions to view where this activity is used."))
        return super().handle_no_permission()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Courses where this activity is used
        context.update(PaginatorFactory.get_paginator_as_context(
            self.object.course_activities.all(), self.request.GET, nb_per_page=10)
        )
        return context


class ActivityDetailSimilarView(ActivityDetailView):
    """
    View similar activities. Similar activities are based on the activity tags.

    When action is performed, the context is filled with:

    * **page_obj,has_obj**…: what is given by the PaginatorFactory to display similar activities.

    .. caution:: Viewing similar activities requires the **view_similar_activity** permission.
    .. note:: warning: The dependency we use to do so, django-taggit has a weird behaviour that can lead to an exception.
    """
    template_name = "learning/activity/details/similar.html"

    def has_permission(self):
        return self.get_object().user_can("view_similar", self.request.user) and super().has_permission()

    def handle_no_permission(self):
        messages.error(self.request, _("You do not have the required permissions to view similar activities."))
        return super().handle_no_permission()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # noinspection PyBroadException
        try:
            similar_list = [
                similar for similar in self.object.tags.similar_objects()
                if isinstance(similar, Activity) and similar.user_can_view(self.request.user)
            ]
            context.update(PaginatorFactory.get_paginator_as_context(similar_list, self.request.GET, nb_per_page=9))
        # django-taggit similar tags can have weird behaviour sometimes: https://github.com/jazzband/django-taggit/issues/80
        except Exception:
            messages.error(
                self.request,
                _("The component used to detect similar activities crashed. We try to fix this as soon as possible.")
            )
        return context


class ResourceOnActivityDetailView(ActivityDetailView):
    """
    View a resource that is used by an activity.

    When action is performed, the context is filled with:

    * **resource**: the resource of the activity to display

    .. caution:: Viewing a resource on an activity requires the permission to view the resource itself and the activity.
    .. important:: The resource to view is given as a POST parameter called “resource_slug” and containing the resource slug.
    """
    template_name = "learning/activity/details/resource.html"

    # noinspection PyAttributeOutsideInit
    def has_permission(self):
        self.resource = get_object_or_404(Resource, slug=self.kwargs.get('resource_slug'), activities=self.get_object())
        return self.resource.user_can_view(self.request.user) and super().has_permission()

    def handle_no_permission(self):
        messages.warning(self.request, _("You do not have the required permission to access the resource you requested."))
        return super().handle_no_permission()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['resource'] = self.resource
        return context


class ActivityCreateResourceView(LoginRequiredMixin, InvalidFormHandlerMixin, ActivityDetailView, ProcessFormView):
    """
    Create a new resource and automatically link it with the current activity.
    The **GET request** displays the form, a **POST** request handles it and creates the resource.
    It redirects to the activity detail page.

    .. caution:: Add a resource changes the activity and requires the **change_activity** permission.
    """
    template_name = "learning/activity/details/add_resource.html"

    def get_form(self, form_class=None):
        if self.request.POST:
            return ResourceCreateForm(self.request.POST)
        return ResourceCreateForm()

    # noinspection PyAttributeOutsideInit
    def has_permission(self):
        self.object = self.get_object()
        return self.get_object().user_can_change(self.request.user) and super().has_permission()

    def handle_no_permission(self):
        messages.warning(
            self.request, _("You do not have the required permission to create a new resource on this activity.")
        )
        return super().handle_no_permission()

    # noinspection PyAttributeOutsideInit
    def form_valid(self, form):
        form.instance.author = self.request.user
        try:
            self.object.add_resource(form.instance)
            messages.success(
                self.request,
                _("The resource “%(resource)s” has been created and added to activity “%(activity)s”.")
                % {'resource': form.instance, 'activity': self.object}
            )
            return redirect("learning:activity/detail", slug=self.object.slug)
        except LearningError as ex:
            messages.error(self.request, ex)
            return self.form_invalid(form)

    def form_invalid(self, form):
        super().form_invalid(form)
        context = super().get_context_data()
        context.update({'activity': self.object, 'form': self.get_form()})
        return render(self.request, self.template_name, context)


class ResourceAttachOnActivityView(LoginRequiredMixin, ActivityDetailView, FormView):
    """
    Attach an existing resource to an activity. This is used to display the resources that can be attached
    to the activity, and to handle the link request.

    When action is performed, the context is filled with:

    * **form**: a BasicSearchForm instance, allowing you to search for specific words
    * **suggested_page_obj,suggested_has_obj**…: what is given by the PaginatorFactory to display suggested resources.
    * **search_page_obj,search_has_obj**…: same but for the resource search result.

    On **POST request**, attaches the corresponding resource and redirects to the **attach resource** page (this view using **GET**).

    .. caution:: Add a link to an activity changes the activity and requires the **change_activity** permission.
    .. important:: The resource to link is given as a POST parameter called “resource” and containing the resource primary key.
    """
    template_name = "learning/activity/details/attach_resource.html"
    form_class = BasicSearchForm

    def has_permission(self):
        return self.get_object().user_can_change(self.request.user) and super().has_permission()

    def handle_no_permission(self):
        messages.warning(self.request, _("You do not have the required permission to attach a resource on this activity."))
        return super().handle_no_permission()

    # noinspection PyAttributeOutsideInit
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        resource = get_object_or_404(Resource, pk=self.request.POST.get('resource'))
        try:
            self.object.add_resource(resource)
            messages.success(
                self.request,
                _('Resource “%(resource)s” added to the activity “%(activity)s”.')
                % {'resource': resource, 'activity': self.object}
            )
        except LearningError as ex:
            messages.error(self.request, ex)
        return redirect("learning:activity/detail/resource/attach", slug=self.object.slug)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        reusable_resources = Resource.objects.exclude(activities=self.object).exclude(reuse=ResourceReuse.NON_REUSABLE.name).exclude(
            Q(reuse=ResourceReuse.ONLY_AUTHOR.name) & ~Q(author=self.request.user)  # Resources that can be reused by their author
        )

        # Suggestion for new activities
        context.update(PaginatorFactory.get_paginator_as_context(
            reusable_resources.all(), self.request.GET, prefix="suggested", nb_per_page=9)
        )

        # User may query some words using the search filter
        form = BasicSearchForm(data=self.request.GET)
        if form.is_valid() and form.cleaned_data.get('query', str()):
            query = form.cleaned_data.get('query', str())
            context.update(PaginatorFactory.get_paginator_as_context(
                reusable_resources.filter(Q(name__icontains=query) | Q(description__icontains=query)).all(),
                self.request.GET, prefix="search")
            )

        # Add the query form to the view
        context['form'] = form
        return context


class ResourceUnlinkOnActivityView(LoginRequiredMixin, ActivityDetailView, FormView):
    """
    Remove the link from a an activity to a specific resource.
    A **GET request** redirects to the activity detail page. A **POST request** handles the action to perform.

    .. note:: When action is performed, it redirects to the activity detail page.
    .. caution:: Remove a link from an activity changes the activity and requires the **change_activity** permission.
    .. important:: The resource to unlink is given as a POST parameter called **resource** and containing the resource primary key.
    """

    def has_permission(self):
        return self.get_object().user_can_change(self.request.user) and super().has_permission()

    def handle_no_permission(self):
        messages.warning(self.request, _("You do not have the required permission to unlink a resource from this activity."))
        return super().handle_no_permission()

    def get(self, request, *args, **kwargs):
        return redirect("learning:activity/detail", slug=self.kwargs.get('slug'))

    # noinspection PyAttributeOutsideInit
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        resource = get_object_or_404(Resource, pk=self.request.POST.get('resource'))
        try:
            self.object.remove_resource(resource)
            messages.success(
                self.request,
                _("Resource “%(resource)s” removed from the activity “%(activity)s”.")
                % {'resource': resource, 'activity': self.object}
            )
        except LearningError as ex:
            messages.error(self.request, ex)
        return redirect("learning:activity/detail", slug=self.object.slug)
