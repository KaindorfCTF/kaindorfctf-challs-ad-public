from functools import wraps

from flask import request, current_app, flash, redirect, url_for
from flask_login import current_user
from flask_login.config import EXEMPT_METHODS


def is_admin(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if request.method in EXEMPT_METHODS:
            return func(*args, **kwargs)
        elif current_app.config.get('LOGIN_DISABLED'):
            return func(*args, **kwargs)
        elif not current_user.is_authenticated:
            return current_app.login_manager.unauthorized()
        elif not current_user.is_admin:
            flash("You must be Admin to access this!", "warning")
            return redirect(url_for("main.index"))
        return func(*args, **kwargs)

    return decorated_view
