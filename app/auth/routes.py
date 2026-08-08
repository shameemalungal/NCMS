from hmac import compare_digest

from flask import (
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from app.auth import auth_bp
from app.utils.audit import log_audit


# ==========================================================
# Admin Login
# ==========================================================

@auth_bp.route(
    "/login",
    methods=["GET", "POST"],
)
def login():

    # Already logged in
    if session.get("admin_authenticated"):

        return redirect(
            url_for("dashboard.index")
        )

    # ------------------------------------------------------
    # Login Submission
    # ------------------------------------------------------

    if request.method == "POST":

        username = (
            request.form.get(
                "username",
                ""
            )
            .strip()
        )

        password = request.form.get(
            "password",
            ""
        )

        expected_username = (
            current_app.config.get(
                "ADMIN_USERNAME",
                "",
            )
        )

        expected_password = (
            current_app.config.get(
                "ADMIN_PASSWORD",
                "",
            )
        )

        username_ok = compare_digest(
            username,
            expected_username,
        )

        password_ok = compare_digest(
            password,
            expected_password,
        )

        if username_ok and password_ok:

            session.clear()

            session[
                "admin_authenticated"
            ] = True

            session[
                "admin_username"
            ] = username

            log_audit(
                username=username,
                module="Authentication",
                action="Administrator Login",
            )

            # ----------------------------------------------
            # Return to requested admin page
            # ----------------------------------------------

            next_url = request.args.get(
                "next"
            )

            if (
                next_url
                and next_url.startswith("/")
                and not next_url.startswith("//")
            ):

                return redirect(next_url)

            return redirect(
                url_for(
                    "dashboard.index"
                )
            )

        flash(
            "Invalid username or password.",
            "danger",
        )

    # ------------------------------------------------------
    # Login Screen
    # ------------------------------------------------------

    return render_template(
        "auth/login.html",
        page_title="Administrator Login",
    )


# ==========================================================
# Admin Logout
# ==========================================================

@auth_bp.route(
    "/logout",
    methods=["POST"],
)
def logout():

    log_audit(
        username=session.get(
            "admin_username",
            "Unknown",
        ),
        module="Authentication",
        action="Administrator Logout",
    )

    session.clear()

    flash(
        "You have been logged out.",
        "success",
    )

    return redirect(
        url_for("auth.login")
    )
