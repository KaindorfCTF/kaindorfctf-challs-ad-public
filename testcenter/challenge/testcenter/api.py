import io
import json
from datetime import datetime

import flask
from flask import Blueprint, redirect, url_for, request, flash, send_file
from flask_login import login_required, current_user

from model import db
from model.TestResults import TestResult
from model.Users import User
from model.TrustedKeys import TrustedKey
from util import util

api = Blueprint('api', __name__)


@api.route('/api/')
def api_main():
    return redirect(url_for("main.index"))


@api.route('/api/trustedkeys/<action>/', methods=['GET', 'POST'])
def trust(action=""):
    if request.method == "POST":
        if action == "add":
            if "pub" in request.files and "priv" in request.files:
                pub = request.files["pub"].read()
                priv = request.files["priv"].read()

                if util.import_trusted_keys(pub, priv):
                    flash("Added Trusted Key Pair", "success")
                else:
                    flash("Error adding Trusted Key Pair!", "danger")
    if request.method == "GET":
        if action == "get":
            keys = TrustedKey.get_all()
            return flask.jsonify(TrustedKey.serialize_list(keys))

    return redirect(url_for("main.dashboard"))


@api.route('/api/test/<action>/', methods=['GET', 'POST'])
@login_required
def test(action=""):
    if request.method == "POST":
        if action == "add":
            if "user" in request.form and current_user.is_admin:
                user_id = request.form["user"]
                ret = redirect(url_for("main.dashboard"))
            else:
                user_id = current_user.id
                ret = redirect(url_for("main.profile"))

            if "type" in request.form and "result" in request.form:
                test_type = request.form["type"]
                result = request.form["result"]
                test_date = datetime.now()

                testresult = TestResult(test_type, result, test_date, user_id)
                db.session.add(testresult)
                db.session.commit()

                flash("Test Result added succesfully!", "success")
                return ret
            else:
                flash("Parameters missing!", "warning")
                return redirect(url_for("main.index"))
    else:
        return redirect(url_for("main.index"))


@api.route('/api/users/')
def api_users():
    users = User.get_all()
    return flask.jsonify(User.serialize_list(users))
