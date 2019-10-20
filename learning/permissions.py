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
import abc


class ObjectPermissionManagerMixin:

    def _get_object_type(self):
        return type(self).__name__.lower()

    def _make_simple_perm(self, perm):
        return perm + '_{}'.format(self._get_object_type())

    def _make_perms(self, perms):
        return [self._make_simple_perm(perm) for perm in perms]

    @abc.abstractmethod
    def _get_user_perms(self, user):
        raise NotImplementedError()

    def get_user_perms(self, user):
        return self._make_perms(self._get_user_perms(user))

    def user_can_view(self, user):
        return self._make_simple_perm("view") in self.get_user_perms(user)

    def user_can_change(self, user):
        return self._make_simple_perm("change") in self.get_user_perms(user)

    def user_can_delete(self, user):
        return self._make_simple_perm("delete") in self.get_user_perms(user)

    def user_can_add(self, user):
        return self._make_simple_perm("add") in self.get_user_perms(user)

    def user_can(self, perm, user):
        return self._make_simple_perm(perm) in self.get_user_perms(user)
