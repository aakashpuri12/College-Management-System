from django.utils.deprecation import MiddlewareMixin
from django.urls import reverse
from django.shortcuts import redirect
from django.db.utils import OperationalError, ProgrammingError


class LoginCheckMiddleWare(MiddlewareMixin):

    def process_view(self, request, view_func, view_args, view_kwargs):

        modulename = view_func.__module__

        auth_allowed_paths = {
            reverse('login_page'),
            reverse('user_login'),
            reverse('user_logout'),
        }

        try:
            user = request.user
            user_type = str(getattr(user, 'user_type', ''))

        except (OperationalError, ProgrammingError):

            # Allow authentication pages to load even when
            # database tables are not initialized.
            if (
                request.path in auth_allowed_paths
                or modulename.startswith('django.contrib.auth')
                or request.path.startswith('/admin/')
            ):
                return None

            return redirect(reverse('login_page'))

        if user.is_authenticated:

            # HOD / Admin
            if user.user_type == '1':

                if modulename == 'main_app.student_views':
                    return redirect(reverse('admin_home'))

            # Staff
            elif user.user_type == '2':

                if (
                    modulename == 'main_app.student_views'
                    or modulename == 'main_app.hod_views'
                ):
                    return redirect(reverse('staff_home'))

            # Student
            elif user.user_type == '3':

                if (
                    modulename == 'main_app.hod_views'
                    or modulename == 'main_app.staff_views'
                ):
                    return redirect(reverse('student_home'))

            # Invalid user type
            else:
                return redirect(reverse('login_page'))

        else:

            # Allow authentication-related pages
            if (
                request.path == reverse('login_page')
                or request.path == reverse('user_login')
                or request.path == reverse('user_logout')
                or modulename == 'django.contrib.auth.views'
            ):
                return None

            return redirect(reverse('login_page'))