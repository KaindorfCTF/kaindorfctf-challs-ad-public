import io
from datetime import datetime, timezone

from sqlalchemy.exc import IntegrityError
from flask import Blueprint, render_template, redirect, url_for, request, flash, send_file
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash

from util import util
from model import db
from model.Users import User

auth = Blueprint('auth', __name__)


@auth.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    return render_template("login.html", title="TestCentral - Login")


@auth.route('/login', methods=['POST'])
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')

    user = User.query.filter_by(username=username).first()

    if not user:
        flash("Error logging in", "danger")
        return redirect(url_for('auth.login'))

    if login_user(user):
        flash("Logged in", "success")
    else:
        flash("Error logging in", "danger")

    if user.is_admin:
        flash("Welcome Admin!", "info")
        return redirect(url_for('main.dashboard'))
    else:
        return redirect(url_for('main.profile'))


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@auth.route('/getcert', methods=['GET', 'POST'])
def get_signup_cert():
    if current_user.is_authenticated:
        return redirect(url_for("main.profile"))

    if request.method == "GET":
        return render_template("getcert.html")
    elif request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        cert = util.generate_signup_cert(username, password, False)

        return send_file(io.BytesIO(cert.encode()), mimetype='plain/text', as_attachment=True,
                         download_name=f"{username}.signupcert")


@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("main.profile"))

    if request.method == "POST":
        if "cert" in request.files:
            cert = request.files["cert"].read()
            data = util.parse_signup_cert(cert)

            if data is None:
                flash("Signup Certificate Error", "danger")
                return redirect(url_for('auth.signup'))

            username = data["username"]
            password = data["username"]
            is_admin = data["is_admin"]
            creation_date = datetime.now(timezone.utc)

            new_user = User(username, generate_password_hash(password, method='scrypt'), cert, is_admin, creation_date)

            try:
                db.session.add(new_user)
                db.session.commit()
            except IntegrityError as e:
                flash("Username already taken!", "danger")
                return redirect(url_for('auth.signup'))

            if login_user(new_user):
                flash(f"Signup complete", "success")
                return redirect(url_for('main.profile'))
            else:
                return redirect(url_for('auth.login'))

    return render_template("signup.html")
