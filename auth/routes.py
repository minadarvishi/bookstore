from flask import Blueprint, render_template , redirect , url_for , flash , request
from flask_login import login_user , logout_user , login_required
from auth.services import AuthService



auth_bp = Blueprint('auth', __name__ , template_folder='templates')

# --- User route ---
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        user , error = AuthService.register_user(name , email , password)
        if error:
            flash(error , 'danger')
            return redirect(url_for('auth.register'))
        
        flash('ثبت‌نام موفق! وارد شوید.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = AuthService.authenticate_user(email , password)
        if user : 
            login_user(user)
            return redirect(url_for('main.home'))
        
        flash('ایمیل یا رمز عبور اشتباه است.', 'danger')
    
    return render_template('auth/login.html')