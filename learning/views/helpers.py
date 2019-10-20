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
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.generic.edit import FormMixin

from learning.forms import BasicSearchForm


class InvalidFormHandlerMixin(FormMixin):

    def __show_messages(self, form):
        for field_errors in form.errors.as_data().values():
            for validation_error in field_errors:
                for message in validation_error.messages:
                    # noinspection PyUnresolvedReferences
                    messages.error(self.request, message)
        return super().form_invalid(form)

    def form_invalid(self, form):  # pragma: no cover
        self.__show_messages(form)
        return super().form_invalid(form)


def int_or_default(value, default):
    try:
        value = int(value)
    except ValueError:
        value = default
    return value


def get_attr_form_query_dict_or_kwargs(attr_name, query_dict, callback, default, **kwargs):
    if attr_name in kwargs.keys():
        value = callback(kwargs.get(attr_name, default), default)
    else:
        try:
            value = callback(query_dict.get(attr_name, default), default)
        except KeyError:
            value = default
    return value


class PaginatorFactory:

    @classmethod
    def get_paginator_as_context(cls, objects, query_dict, prefix=None, nb_per_page=3, **kwargs):
        # Make attribute names
        paginator_str = '{}_paginator'.format(prefix) if prefix else 'paginator'
        page_obj_str = '{}_page_obj'.format(prefix) if prefix else 'page_obj'
        has_obj_str = '{}_has_obj'.format(prefix) if prefix else 'has_obj'
        nb_per_page_str = '{}_nb_per_page'.format(prefix) if prefix else 'nb_per_page'
        current_page_str = '{}_page'.format(prefix) if prefix else 'page'

        # Extract values: if value is defined in **kwargs, it has priority over the query dict
        nb_per_page = get_attr_form_query_dict_or_kwargs(nb_per_page_str, query_dict, int_or_default, nb_per_page, **kwargs)
        current_page = get_attr_form_query_dict_or_kwargs(current_page_str, query_dict, int_or_default, 1, **kwargs)

        paginator = Paginator(objects, nb_per_page)
        return {
            paginator_str: paginator,
            page_obj_str: paginator.get_page(current_page),
            nb_per_page_str: nb_per_page,
            has_obj_str: bool(paginator.object_list)
        }


class SearchQuery:

    @classmethod
    def search_query_as_context(cls, obj_class, query_dict):
        context = dict()
        form = BasicSearchForm(data=query_dict)
        if form.is_valid() and form.cleaned_data.get('query', str()):
            query = form.cleaned_data.get('query', str())
            queryset = obj_class.objects.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query)
            ).all()
            context.update(PaginatorFactory.get_paginator_as_context(queryset, query_dict, prefix="search"))
        context['form'] = form
        return context
