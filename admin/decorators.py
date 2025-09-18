
from functools import wraps
from flask import session, redirect, url_for, flash

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'is_admin' not in session:
            flash("برای دسترسی به این صفحه باید وارد شوید.", "warning")
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function