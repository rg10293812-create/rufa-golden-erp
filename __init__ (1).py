from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect


def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            profile = getattr(request.user, 'profile', None)
            if request.user.is_superuser or (profile and profile.role in roles):
                return view_func(request, *args, **kwargs)
            messages.error(request, 'ليس لديك صلاحية لهذه الصفحة.')
            return redirect('dashboard')
        return wrapper
    return decorator


def is_executive(user):
    profile = getattr(user, 'profile', None)
    return user.is_superuser or (profile and profile.role == 'executive')
