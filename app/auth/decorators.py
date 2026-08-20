from functools import wraps

from flask import (
    flash,
    redirect,
    request,
    session,
    url_for,
)

from app.auth.models import User
from app.extensions import db


# ==========================================================
# Current User
# ==========================================================

def get_current_user():
    """
    Return the currently authenticated database user.

    Returns None when:
    - no user is authenticated
    - the user no longer exists
    - the user is inactive
    """

    user_id = session.get("user_id")

    if not user_id:
        return None

    user = db.session.get(
        User,
        user_id,
    )

    if user is None or not user.is_active:
        return None

    return user


# ==========================================================
# Password Change Requirement
# ==========================================================

def _password_change_required(user):
    """
    Return True when the authenticated user must change
    their password before accessing normal NCMS pages.
    """

    return bool(
        user.must_change_password
    )


def _password_change_redirect():
    """
    Redirect the authenticated user to the password-change
    page while preserving the requested destination.
    """

    next_url = (
        request.full_path
        if request.query_string
        else request.path
    )

    return redirect(
        url_for(
            "auth.change_password",
            next=next_url,
        )
    )


# ==========================================================
# Authentication Required
# ==========================================================

def login_required(view_function):
    """
    Require an authenticated, active NCMS user.

    Users whose password has been administratively reset
    or who have been created with an initial password must
    change that password before accessing normal NCMS pages.

    The password-change page itself remains accessible.
    """

    @wraps(view_function)
    def wrapped_view(*args, **kwargs):

        user = get_current_user()

        # --------------------------------------------------
        # Not authenticated
        # --------------------------------------------------

        if user is None:

            return redirect(
                url_for(
                    "auth.login",
                    next=(
                        request.full_path
                        if request.query_string
                        else request.path
                    ),
                )
            )

        # --------------------------------------------------
        # Forced password change
        # --------------------------------------------------

        if _password_change_required(user):

            endpoint = request.endpoint or ""

            if endpoint != "auth.change_password":

                flash(
                    "You must change your password before "
                    "continuing.",
                    "warning",
                )

                return _password_change_redirect()

        # --------------------------------------------------
        # Access granted
        # --------------------------------------------------

        return view_function(
            *args,
            **kwargs,
        )

    return wrapped_view


# ==========================================================
# Permission Required
# ==========================================================

def require_permission(permission_code):
    """
    Require an authenticated database user with the
    specified permission.

    Authentication:
        session["user_id"]

    Authorization:
        User -> Role -> Permission

    Users who must change their password are redirected
    to the password-change page before permission checks
    are performed.
    """

    def decorator(view_function):

        @wraps(view_function)
        def wrapped_view(*args, **kwargs):

            # --------------------------------------------------
            # Database-backed identity
            # --------------------------------------------------

            user_id = session.get("user_id")

            if not user_id:

                return redirect(
                    url_for(
                        "auth.login",
                        next=(
                            request.full_path
                            if request.query_string
                            else request.path
                        ),
                    )
                )

            # --------------------------------------------------
            # Load user
            # --------------------------------------------------

            user = db.session.get(
                User,
                user_id,
            )

            # --------------------------------------------------
            # Invalid / inactive user
            # --------------------------------------------------

            if user is None or not user.is_active:

                session.clear()

                flash(
                    "Your account is inactive or no longer available.",
                    "danger",
                )

                return redirect(
                    url_for(
                        "auth.login",
                        next=(
                            request.full_path
                            if request.query_string
                            else request.path
                        ),
                    )
                )

            # --------------------------------------------------
            # Forced password change
            # --------------------------------------------------

            if _password_change_required(user):

                endpoint = request.endpoint or ""

                if endpoint != "auth.change_password":

                    flash(
                        "You must change your password before "
                        "continuing.",
                        "warning",
                    )

                    return _password_change_redirect()

            # --------------------------------------------------
            # Permission check
            # --------------------------------------------------

            if not user.has_permission(
                permission_code
            ):

                flash(
                    "You do not have permission to access this page.",
                    "danger",
                )

                return redirect(
                    url_for(
                        "dashboard.index"
                    )
                )

            # --------------------------------------------------
            # Permission granted
            # --------------------------------------------------

            return view_function(
                *args,
                **kwargs,
            )

        return wrapped_view

    return decorator
