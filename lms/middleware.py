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

from django.conf import settings
from django.contrib.auth import get_user_model

from lms import logger


class DemonstrationUserAuthentication:
    """
    Automatically login the demonstration user, if any
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.demo = getattr(settings, 'DEMO', False)
        if self.demo and hasattr(settings, 'DEMONSTRATION_LOGIN'):
            self.user = get_user_model().objects.filter(username=getattr(settings, 'DEMONSTRATION_LOGIN')).get()
        else:
            raise ValueError("When you enable the demonstration server, you must provide "
                             "the login of the user that will be connected automatically."
                             "You have to provide the login using the DEMONSTRATION_LOGIN "
                             "key in your settings")

    def __call__(self, request):
        # This works only when running a demonstration server
        if self.demo:
            # If the user is already connected, it is not necessary to go further
            if not request.user.is_authenticated:
                request.user = self.user
        else:
            logger.warning("Automatic login works only when running the demonstration mode.")
        return self.get_response(request)
