from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from model.Users import User
from util.util import *
from decorators.views import is_admin

main = Blueprint('main', __name__)


@main.route('/')
def index():
    new_users = User.get_latest_users()
    new_users.sort(key=lambda user: max([r.test_date for r in user.test_results]))
    return render_template("index.html", title="TestCentral", new_users=new_users)


@main.route('/dashboard/')
@is_admin
def dashboard():
    return render_template("dashboard.html", title="TestCentral - Admin Dashboard", users=User.get_all())


@main.route('/profile/')
@login_required
def profile():
    return render_template("profile.html", title=f"TestCentral - {current_user.username}", user=current_user)


@main.route('/profile/<user_id>/')
def user_profile(user_id):
    try:
        user = User.get_user_by_id(int(user_id))
        return render_template("profile.html", title=f"TestCentral - {user.username}", user=user)
    except ValueError as e:
        flash("Wrong user id!", "danger")
        return redirect(url_for("main.index"))
