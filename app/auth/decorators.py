from functools import wraps

from flask import (
    redirect,
    request,
    session,
    url_for,
)


def admin_required(view_function):

    @wraps(view_function)
    def wrapped_view(*args, **kwargs):

        # --------------------------------------------------
        # Administrator already authenticated
        # --------------------------------------------------

        if session.get("admin_authenticated"):

            return view_function(
                *args,
                **kwargs,
            )

        # --------------------------------------------------
        # Not authenticated
        #
        # Remember the requested page so NCMS can return
        # the administrator there after successful login.
        # --------------------------------------------------

        return redirect(
            url_for(
                "auth.login",
                next=request.full_path
                if request.query_string
                else request.path,
            )
        )

    return wrapped_view