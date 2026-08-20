from flask import (
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from sqlalchemy import func

from app.auth import auth_bp
from app.auth.decorators import require_permission
from app.auth.models import Role, User
from app.extensions import db
from app.utils.audit import log_audit


# ==========================================================
# Helpers
# ==========================================================

def _active_admin_count():
    """
    Return the number of active users who currently have
    the ADMIN role.
    """

    return (
        User.query
        .join(User.roles)
        .filter(
            User.is_active.is_(True),
            Role.name == "ADMIN",
        )
        .count()
    )


def _user_has_admin_role(user):
    """
    Return True when the user currently has ADMIN role.
    """

    return any(
        role.name == "ADMIN"
        for role in user.roles
    )


def _can_remove_admin_status(user):
    """
    Prevent removal of the last active ADMIN.
    """

    if not _user_has_admin_role(user):
        return True

    return _active_admin_count() > 1


def _normalise_username(value):
    return (value or "").strip()


def _normalise_email(value):
    value = (value or "").strip()

    return value or None


# ==========================================================
# User List
# ==========================================================

@auth_bp.route(
    "/users",
    methods=["GET"],
)
@require_permission("users.manage")
def users():

    users = (
        User.query
        .order_by(
            func.lower(User.username)
        )
        .all()
    )

    return render_template(
        "auth/users.html",
        users=users,
        page_label="NCMS Administration",
        page_title="User Management",
        page_subtitle=(
            "Manage NCMS users, account status "
            "and role assignments"
        ),
    )


# ==========================================================
# Create User
# ==========================================================

@auth_bp.route(
    "/users/create",
    methods=["GET", "POST"],
)
@require_permission("users.manage")
def create_user():

    roles = (
        Role.query
        .order_by(
            func.lower(Role.name)
        )
        .all()
    )

    if request.method == "POST":

        username = _normalise_username(
            request.form.get("username")
        )

        full_name = (
            request.form.get(
                "full_name",
                "",
            )
            .strip()
        )

        email = _normalise_email(
            request.form.get("email")
        )

        password = request.form.get(
            "password",
            "",
        )

        confirm_password = request.form.get(
            "confirm_password",
            "",
        )

        selected_role_ids = {
            role_id
            for role_id in request.form.getlist(
                "role_ids"
            )
            if role_id
        }

        # --------------------------------------------------
        # Basic validation
        # --------------------------------------------------

        if not username:

            flash(
                "Username is required.",
                "danger",
            )

            return render_template(
                "auth/user_form.html",
                user=None,
                roles=roles,
                selected_role_ids=selected_role_ids,
                form_mode="create",
                page_label="NCMS Administration",
                page_title="Create User",
            )

        if not full_name:

            flash(
                "Full name is required.",
                "danger",
            )

            return render_template(
                "auth/user_form.html",
                user=None,
                roles=roles,
                selected_role_ids=selected_role_ids,
                form_mode="create",
                page_label="NCMS Administration",
                page_title="Create User",
            )

        if len(password) < 8:

            flash(
                "Password must be at least 8 characters.",
                "danger",
            )

            return render_template(
                "auth/user_form.html",
                user=None,
                roles=roles,
                selected_role_ids=selected_role_ids,
                form_mode="create",
                page_label="NCMS Administration",
                page_title="Create User",
            )

        if password != confirm_password:

            flash(
                "Passwords do not match.",
                "danger",
            )

            return render_template(
                "auth/user_form.html",
                user=None,
                roles=roles,
                selected_role_ids=selected_role_ids,
                form_mode="create",
                page_label="NCMS Administration",
                page_title="Create User",
            )

        # --------------------------------------------------
        # Duplicate username
        # --------------------------------------------------

        existing_user = (
            User.query
            .filter(
                func.lower(User.username)
                == username.lower()
            )
            .first()
        )

        if existing_user is not None:

            flash(
                "That username is already in use.",
                "danger",
            )

            return render_template(
                "auth/user_form.html",
                user=None,
                roles=roles,
                selected_role_ids=selected_role_ids,
                form_mode="create",
                page_label="NCMS Administration",
                page_title="Create User",
            )

        # --------------------------------------------------
        # Duplicate email
        # --------------------------------------------------

        if email:

            existing_email = (
                User.query
                .filter(
                    func.lower(User.email)
                    == email.lower()
                )
                .first()
            )

            if existing_email is not None:

                flash(
                    "That email address is already in use.",
                    "danger",
                )

                return render_template(
                    "auth/user_form.html",
                    user=None,
                    roles=roles,
                    selected_role_ids=selected_role_ids,
                    form_mode="create",
                    page_label="NCMS Administration",
                    page_title="Create User",
                )

        # --------------------------------------------------
        # Create user
        # --------------------------------------------------

        user = User(
            username=username,
            full_name=full_name,
            email=email,
            is_active=True,
            must_change_password=True,
        )

        user.set_password(password)

        # --------------------------------------------------
        # Assign selected roles
        # --------------------------------------------------

        if selected_role_ids:

            user.roles = [
                role
                for role in roles
                if str(role.id) in selected_role_ids
            ]

        db.session.add(user)
        db.session.commit()

        log_audit(
            username=user.username,
            module="User Management",
            action="User Created",
        )

        flash(
            f"User '{user.username}' created successfully. "
            "The user must change the initial password at first login.",
            "success",
        )

        return redirect(
            url_for("auth.users")
        )

    return render_template(
        "auth/user_form.html",
        user=None,
        roles=roles,
        selected_role_ids=set(),
        form_mode="create",
        page_label="NCMS Administration",
        page_title="Create User",
    )


# ==========================================================
# Edit User
# ==========================================================

@auth_bp.route(
    "/users/<int:user_id>/edit",
    methods=["GET", "POST"],
)
@require_permission("users.manage")
def edit_user(user_id):

    user = User.query.get_or_404(user_id)

    roles = (
        Role.query
        .order_by(
            func.lower(Role.name)
        )
        .all()
    )

    if request.method == "POST":

        full_name = (
            request.form.get(
                "full_name",
                "",
            )
            .strip()
        )

        email = _normalise_email(
            request.form.get("email")
        )

        selected_role_ids = {
            role_id
            for role_id in request.form.getlist(
                "role_ids"
            )
            if role_id
        }

        if not full_name:

            flash(
                "Full name is required.",
                "danger",
            )

            return render_template(
                "auth/user_form.html",
                user=user,
                roles=roles,
                selected_role_ids=selected_role_ids,
                form_mode="edit",
                page_label="NCMS Administration",
                page_title="Edit User",
            )

        # --------------------------------------------------
        # Duplicate email
        # --------------------------------------------------

        if email:

            existing_email = (
                User.query
                .filter(
                    func.lower(User.email)
                    == email.lower(),
                    User.id != user.id,
                )
                .first()
            )

            if existing_email is not None:

                flash(
                    "That email address is already in use.",
                    "danger",
                )

                return render_template(
                    "auth/user_form.html",
                    user=user,
                    roles=roles,
                    selected_role_ids=selected_role_ids,
                    form_mode="edit",
                    page_label="NCMS Administration",
                    page_title="Edit User",
                )

        # --------------------------------------------------
        # Determine requested roles
        # --------------------------------------------------

        requested_roles = [
            role
            for role in roles
            if str(role.id) in selected_role_ids
        ]

        currently_admin = _user_has_admin_role(
            user
        )

        will_be_admin = any(
            role.name == "ADMIN"
            for role in requested_roles
        )

        # --------------------------------------------------
        # Last ADMIN protection
        # --------------------------------------------------

        if (
            currently_admin
            and not will_be_admin
            and not _can_remove_admin_status(user)
        ):

            flash(
                "The last active ADMIN account cannot "
                "have its ADMIN role removed.",
                "danger",
            )

            return render_template(
                "auth/user_form.html",
                user=user,
                roles=roles,
                selected_role_ids={
                    str(role.id)
                    for role in user.roles
                },
                form_mode="edit",
                page_label="NCMS Administration",
                page_title="Edit User",
            )

        # --------------------------------------------------
        # Update
        # --------------------------------------------------

        user.full_name = full_name
        user.email = email
        user.roles = requested_roles

        db.session.commit()

        log_audit(
            username=user.username,
            module="User Management",
            action="User Updated",
        )

        flash(
            f"User '{user.username}' updated successfully.",
            "success",
        )

        return redirect(
            url_for("auth.users")
        )

    return render_template(
        "auth/user_form.html",
        user=user,
        roles=roles,
        selected_role_ids={
            str(role.id)
            for role in user.roles
        },
        form_mode="edit",
        page_label="NCMS Administration",
        page_title="Edit User",
    )


# ==========================================================
# Activate / Deactivate User
# ==========================================================

@auth_bp.route(
    "/users/<int:user_id>/toggle-active",
    methods=["POST"],
)
@require_permission("users.manage")
def toggle_user_active(user_id):

    user = User.query.get_or_404(user_id)

    # ------------------------------------------------------
    # Prevent deactivation of the last ADMIN
    # ------------------------------------------------------

    if user.is_active and _user_has_admin_role(user):

        if not _can_remove_admin_status(user):

            flash(
                "The last active ADMIN account cannot "
                "be deactivated.",
                "danger",
            )

            return redirect(
                url_for("auth.users")
            )

    user.is_active = not user.is_active

    db.session.commit()

    action = (
        "User Activated"
        if user.is_active
        else "User Deactivated"
    )

    log_audit(
        username=user.username,
        module="User Management",
        action=action,
    )

    flash(
        f"User '{user.username}' "
        f"{'activated' if user.is_active else 'deactivated'} successfully.",
        "success",
    )

    return redirect(
        url_for("auth.users")
    )


# ==========================================================
# Reset User Password
# ==========================================================

@auth_bp.route(
    "/users/<int:user_id>/reset-password",
    methods=["GET", "POST"],
)
@require_permission("users.manage")
def reset_user_password(user_id):

    user = User.query.get_or_404(user_id)

    if request.method == "POST":

        new_password = request.form.get(
            "new_password",
            "",
        )

        confirm_password = request.form.get(
            "confirm_password",
            "",
        )

        # --------------------------------------------------
        # Password validation
        # --------------------------------------------------

        if len(new_password) < 8:

            flash(
                "Password must be at least 8 characters.",
                "danger",
            )

            return render_template(
                "auth/reset_password.html",
                user=user,
                page_label="NCMS Administration",
                page_title="Reset User Password",
            )

        if new_password != confirm_password:

            flash(
                "Passwords do not match.",
                "danger",
            )

            return render_template(
                "auth/reset_password.html",
                user=user,
                page_label="NCMS Administration",
                page_title="Reset User Password",
            )

        # --------------------------------------------------
        # Set reset password
        # --------------------------------------------------

        user.set_password(new_password)

        user.must_change_password = True

        db.session.commit()

        log_audit(
            username=user.username,
            module="User Management",
            action="Administrator Password Reset",
        )

        flash(
            f"Password reset for '{user.username}'. "
            "The user must change the password at next login.",
            "success",
        )

        return redirect(
            url_for("auth.users")
        )

    return render_template(
        "auth/reset_password.html",
        user=user,
        page_label="NCMS Administration",
        page_title="Reset User Password",
    )
