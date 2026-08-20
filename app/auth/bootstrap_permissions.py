from app import create_app
from app.extensions import db
from app.auth.models import Permission, Role


PERMISSIONS = [
    ("audit.view", "View audit logs"),
    ("campaign.view", "View campaigns"),
    ("campaign.create", "Create campaigns"),
    ("campaign.edit", "Edit campaigns"),
    ("campaign.delete", "Delete campaigns"),
    ("masterdata.view", "View master data"),
    ("masterdata.import", "Import master data"),
    ("monitoring.view", "View district monitoring"),
    ("monitoring.squads.view", "View squad monitoring"),
    ("monitoring.resubmission", "Manage squad re-submission"),
    ("monitoring.history.view", "View submission history"),
    ("panchayath.view", "View Panchayaths"),
    ("panchayath.create", "Create Panchayaths"),
    ("panchayath.edit", "Edit Panchayaths"),
    ("panchayath.delete", "Delete Panchayaths"),
    ("reports.view", "View reports"),
    ("settings.view", "View settings"),
    ("settings.edit", "Edit settings"),
    ("backup.download", "Download NCMS backup"),
]


def bootstrap_permissions():

    app = create_app()

    with app.app_context():

        admin_role = Role.query.filter_by(
            name="ADMIN"
        ).first()

        if admin_role is None:
            raise RuntimeError(
                "ADMIN role does not exist."
            )

        created = 0
        assigned = 0

        for code, description in PERMISSIONS:

            permission = Permission.query.filter_by(
                code=code
            ).first()

            if permission is None:

                permission = Permission(
                    code=code,
                    description=description,
                )

                db.session.add(permission)
                db.session.flush()

                created += 1

            if permission not in admin_role.permissions:

                admin_role.permissions.append(
                    permission
                )

                assigned += 1

        db.session.commit()

        print(
            f"Permissions created: {created}"
        )

        print(
            f"Permissions assigned to ADMIN: {assigned}"
        )

        print(
            "ADMIN permissions:"
        )

        for permission in sorted(
            admin_role.permissions,
            key=lambda item: item.code,
        ):

            print(
                f"  {permission.code}"
            )


if __name__ == "__main__":
    bootstrap_permissions()