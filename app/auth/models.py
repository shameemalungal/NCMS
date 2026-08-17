from datetime import datetime

from werkzeug.security import (
    generate_password_hash,
    check_password_hash,
)

from app.extensions import db


# ==========================================================
# User <-> Role Association
# ==========================================================

user_roles = db.Table(
    "user_roles",

    db.Column(
        "user_id",
        db.Integer,
        db.ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    ),

    db.Column(
        "role_id",
        db.Integer,
        db.ForeignKey(
            "roles.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    ),
)


# ==========================================================
# Role <-> Permission Association
# ==========================================================

role_permissions = db.Table(
    "role_permissions",

    db.Column(
        "role_id",
        db.Integer,
        db.ForeignKey(
            "roles.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    ),

    db.Column(
        "permission_id",
        db.Integer,
        db.ForeignKey(
            "permissions.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    ),
)


# ==========================================================
# User
# ==========================================================

class User(db.Model):

    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    username = db.Column(
        db.String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    full_name = db.Column(
        db.String(200),
        nullable=False,
    )

    email = db.Column(
        db.String(255),
        unique=True,
        nullable=True,
        index=True,
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False,
    )

    is_active = db.Column(
        db.Boolean,
        nullable=False,
        default=True,
        server_default="true",
        index=True,
    )

    must_change_password = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )

    last_login_at = db.Column(
        db.DateTime,
        nullable=True,
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    roles = db.relationship(
        "Role",
        secondary=user_roles,
        back_populates="users",
        lazy="select",
    )

    # ------------------------------------------------------
    # Password Handling
    # ------------------------------------------------------

    def set_password(self, password):
        self.password_hash = generate_password_hash(
            password
        )

    def check_password(self, password):
        return check_password_hash(
            self.password_hash,
            password,
        )

    # ------------------------------------------------------
    # Permission Helpers
    # ------------------------------------------------------

    @property
    def is_admin(self):
        return any(
            role.name == "ADMIN"
            for role in self.roles
        )

    def has_permission(self, permission_code):

        if self.is_admin:
            return True

        return any(
            permission.code == permission_code
            for role in self.roles
            for permission in role.permissions
        )

    def has_any_permission(self, permission_codes):

        if self.is_admin:
            return True

        return any(
            self.has_permission(code)
            for code in permission_codes
        )

    def __repr__(self):
        return (
            f"<User {self.username}>"
        )


# ==========================================================
# Role
# ==========================================================

class Role(db.Model):

    __tablename__ = "roles"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    name = db.Column(
        db.String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    description = db.Column(
        db.String(255),
        nullable=True,
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    users = db.relationship(
        "User",
        secondary=user_roles,
        back_populates="roles",
        lazy="select",
    )

    permissions = db.relationship(
        "Permission",
        secondary=role_permissions,
        back_populates="roles",
        lazy="select",
    )

    def __repr__(self):
        return (
            f"<Role {self.name}>"
        )


# ==========================================================
# Permission
# ==========================================================

class Permission(db.Model):

    __tablename__ = "permissions"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    code = db.Column(
        db.String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    description = db.Column(
        db.String(255),
        nullable=False,
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    roles = db.relationship(
        "Role",
        secondary=role_permissions,
        back_populates="permissions",
        lazy="select",
    )

    def __repr__(self):
        return (
            f"<Permission {self.code}>"
        )