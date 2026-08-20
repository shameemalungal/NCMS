from flask import (
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from app.auth import auth_bp
from app.auth.decorators import get_current_user
from app.auth.models import User
from app.extensions import db
from app.utils.audit import log_audit


# ==========================================================
# User Login
# ==========================================================

@auth_bp.route(
    "/login",
    methods=["GET", "POST"],
)
def login():

    # ------------------------------------------------------
    # Already logged in
    # ------------------------------------------------------

    if session.get("user_id"):

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
                "",
            )
            .strip()
        )

        password = request.form.get(
            "password",
            "",
        )

        # --------------------------------------------------
        # Find database user
        # --------------------------------------------------

        user = (
            User.query
            .filter_by(username=username)
            .first()
        )

        # --------------------------------------------------
        # Validate credentials
        # --------------------------------------------------

        if (
            user is None
            or not user.is_active
            or not user.check_password(password)
        ):

            log_audit(
                username=username or "Unknown",
                module="Authentication",
                action="Failed Login",
            )

            flash(
                "Invalid username or password.",
                "danger",
            )

            return render_template(
                "auth/login.html",
                page_title="Administrator Login",
            )

        # --------------------------------------------------
        # Successful authentication
        # --------------------------------------------------

        session.clear()

        session[
            "user_id"
        ] = user.id

        session[
            "username"
        ] = user.username


        # --------------------------------------------------
        # Update last login
        # --------------------------------------------------

        from datetime import datetime

        user.last_login_at = datetime.utcnow()

        db.session.commit()

        # --------------------------------------------------
        # Audit
        # --------------------------------------------------

        log_audit(
            username=user.username,
            module="Authentication",
            action="User Login",
        )

        # --------------------------------------------------
        # Return to requested page
        # --------------------------------------------------

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

    # ------------------------------------------------------
    # Login Screen
    # ------------------------------------------------------

    return render_template(
        "auth/login.html",
        page_title="Administrator Login",
    )


# ==========================================================
# User Logout
# ==========================================================

@auth_bp.route(
    "/logout",
    methods=["POST"],
)
def logout():

    user = get_current_user()

    username = (
        user.username
        if user
        else "Unknown"
    )

    log_audit(
        username=username,
        module="Authentication",
        action="User Logout",
    )

    session.clear()

    flash(
        "You have been logged out.",
        "success",
    )

    return redirect(
        url_for("auth.login")
    )
