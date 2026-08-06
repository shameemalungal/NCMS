from flask import (
    render_template,
    redirect,
    url_for,
    flash,
    request,
)

from app.extensions import db
from app.models import Panchayath
from app.panchayath import panchayath_bp
from app.panchayath.forms import PanchayathForm
from app.auth.decorators import admin_required


@panchayath_bp.route("/")
@admin_required
def index():

    search = request.args.get("search", "").strip()

    query = Panchayath.query

    if search:
        query = query.filter(
            Panchayath.name.ilike(f"%{search}%")
        )

    panchayaths = (
        query
        .order_by(Panchayath.name)
        .all()
    )

    return render_template(
        "panchayath/index.html",
        panchayaths=panchayaths,
        search=search,
    )


@panchayath_bp.route("/add", methods=["GET", "POST"])
@admin_required
def add():

    form = PanchayathForm()

    if form.validate_on_submit():

        panchayath = Panchayath(
            name=form.name.data
        )

        db.session.add(panchayath)
        db.session.commit()

        flash(
            "Panchayath added successfully.",
            "success",
        )

        return redirect(
            url_for("panchayath.index")
        )

    return render_template(
        "panchayath/form.html",
        form=form,
        title="Add Panchayath",
    )


@panchayath_bp.route("/edit/<int:id>", methods=["GET", "POST"])
@admin_required
def edit(id):

    panchayath = Panchayath.query.get_or_404(id)

    form = PanchayathForm(
        original_name=panchayath.name,
        obj=panchayath,
    )

    if form.validate_on_submit():

        panchayath.name = form.name.data

        db.session.commit()

        flash(
            "Panchayath updated successfully.",
            "success",
        )

        return redirect(
            url_for("panchayath.index")
        )

    return render_template(
        "panchayath/form.html",
        form=form,
        title="Edit Panchayath",
    )


@panchayath_bp.route("/delete/<int:id>", methods=["POST"])
@admin_required
def delete(id):

    panchayath = Panchayath.query.get_or_404(id)

    db.session.delete(panchayath)
    db.session.commit()

    flash(
        "Panchayath deleted successfully.",
        "success",
    )

    return redirect(
        url_for("panchayath.index")
    )