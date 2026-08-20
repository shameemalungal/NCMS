from functools import wraps

from flask import (
    flash,
    redirect,
    request,
    session,
    url_for,
)

from app.auth.models import User

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

    user = User.query.get(user_id)

    if user is None or not user.is_active:
        return None

    return user


def require_permission(permission_code):
    """
    Require an authenticated database user with
    the specified permission.

    Authentication:
        session["user_id"]

    Authorization:
        User -> Role -> Permission
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

            user = User.query.get(user_id)

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
            # Permission check
            # --------------------------------------------------

            if not user.has_permission(permission_code):

                flash(
                    "You do not have permission to access this page.",
                    "danger",
                )

                return redirect(
                    url_for("dashboard.index")
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
