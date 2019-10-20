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
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, DeleteView, UpdateView, CreateView, TemplateView
from django.views.generic.detail import SingleObjectMixin
from learning.forms import ResourceCreateForm, ResourceUpdateForm, BasicSearchForm
from learning.models import Resource, get_max_upload_size

from learning.views.helpers import PaginatorFactory, SearchQuery, InvalidFormHandlerMixin


class ResourceDetailMixin(PermissionRequiredMixin, SingleObjectMixin):
    """
    .. caution:: Viewing a resource requires the **view_resource** permission.
    """
    model = Resource
    template_name = "learning/resource/detail.html"

    def has_permission(self):
        # noinspection PyUnresolvedReferences
        return self.get_object().user_can_view(self.request.user)


class ResourceDetailView(ResourceDetailMixin, PermissionRequiredMixin, DetailView):
    def handle_no_permission(self):
        messages.error(self.request, _("You do not have the required permissions to access this resource."))
        return super().handle_no_permission()


class ResourceCreateView(LoginRequiredMixin, InvalidFormHandlerMixin, CreateView):
    model = Resource
    form_class = ResourceCreateForm
    template_name = "learning/resource/add.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, _('Resource “%(resource)s” created.') % {'resource': form.instance.name})
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("learning:resource/detail", kwargs={'slug': self.object.slug})


class ResourceUpdateView(LoginRequiredMixin, InvalidFormHandlerMixin, ResourceDetailMixin, UpdateView):
    """
    Update an existing activity

    .. caution:: Delete an activity requires the **change_resource** permission.
    """
    form_class = ResourceUpdateForm
    template_name = 'learning/resource/details/change.html'
    extra_context = {
        'media_upload_size': get_max_upload_size()
    }

    def has_permission(self):
        return self.get_object().user_can_change(self.request.user)

    def handle_no_permission(self):
        messages.error(self.request, _("You do not have the required permissions to change this resource."))
        return super().handle_no_permission()

    def form_valid(self, form):
        if form.has_changed():
            messages.success(self.request, _('The resource “%(resource)s” has been updated.') % {'resource': self.object.name})
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('learning:resource/detail', kwargs={'slug': self.object.slug})


class ResourceDeleteView(LoginRequiredMixin, ResourceDetailMixin, DeleteView):
    """
    Delete an activity

    .. caution:: Delete an activity requires the **delete_resource** permission.
    """
    success_url = reverse_lazy('learning:resource/my')
    template_name = 'learning/resource/delete.html'

    def has_permission(self):
        return self.get_object().user_can_delete(self.request.user)

    def handle_no_permission(self):
        messages.error(self.request, _("You do not have the required permissions to delete this resource."))
        return super().handle_no_permission()

    def get_success_url(self):
        messages.success(
            self.request, _('The resource ”%(resource)s” has been deleted.') % {'resource': self.object.name}
        )
        return super().get_success_url()


class ResourceListView(LoginRequiredMixin, TemplateView):
    """
    List the activities that the logged-on user is the author of.

    When action is performed, the context is filled with:

    * **form**: a BasicSearchForm instance, allowing you to search for specific words
    * **resources_page_obj,resources_has_obj**…: what is given by the PaginatorFactory to display resources owned \
                                                   by the user
    * **search_page_obj,search_has_obj**…: same but for the activity search result.
    """
    model = Resource
    template_name = "learning/resource/my_list.html"
    form_class = BasicSearchForm  # This is used to perform the search

    # pylint: disable=unused-argument
    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        # Resources by the logged-on user
        context.update(
            PaginatorFactory.get_paginator_as_context(
                Resource.objects.filter(author=self.request.user).all(),
                self.request.GET, prefix="resources", nb_per_page=9
            )
        )
        # Resources that match the query
        context.update(SearchQuery.search_query_as_context(Resource, self.request.GET))
        return context


class ResourceDetailUsageView(LoginRequiredMixin, ResourceDetailView):
    """
    View which activities use this resource.

    When action is performed, the context is filled with:

    * **page_obj,has_obj**…: what is given by the PaginatorFactory to display courses that use this resource.

    .. caution:: Viewing activities that use this activities requires the **view_usage_resource** permission.
    """
    template_name = "learning/resource/details/usage.html"

    def has_permission(self):
        return self.get_object().user_can("view_usage", self.request.user) and super().has_permission()

    def handle_no_permission(self):
        messages.error(self.request, _("You do not have the required permissions to view where this resource is used."))
        return super().handle_no_permission()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Activities where the resources is used
        context.update(PaginatorFactory.get_paginator_as_context(
            self.object.activities.all(), self.request.GET, nb_per_page=10)
        )
        return context


class ResourceDetailSimilarView(ResourceDetailView):
    """
    View similar resources. Similar resources are based on the resource tags.

    When action is performed, the context is filled with:

    * **page_obj,has_obj**…: what is given by the PaginatorFactory to display similar resources.

    .. caution:: Viewing similar resources requires the **view_similar_resource** permission.
    .. note:: warning: The dependency we use to do so, django-taggit has a weird behaviour that can lead to an exception.
    """
    template_name = "learning/resource/details/similar.html"

    def has_permission(self):
        return self.get_object().user_can("view_similar", self.request.user) and super().has_permission()

    def handle_no_permission(self):
        messages.error(self.request, _("You do not have the required permissions to view similar resources."))
        return super().handle_no_permission()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # noinspection PyBroadException
        try:
            similar_list = [
                similar for similar in self.object.tags.similar_objects()
                if isinstance(similar, Resource) and similar.user_can_view(self.request.user)
            ]
            context.update(PaginatorFactory.get_paginator_as_context(similar_list, self.request.GET, nb_per_page=9))
        # django-taggit similar tags can have weird behaviour sometimes: https://github.com/jazzband/django-taggit/issues/80
        except Exception:
            messages.error(self.request, _("The component used to detect similar resources crashed. We try to fix this as soon as possible."))
        return context
