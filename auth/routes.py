from flask import Blueprint, render_template , redirect , url_for , flash , request ,abort
from flask_login import login_user , logout_user , login_required , current_user
from auth.services import AuthService
from models import Order



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
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        
        flash('ایمیل یا رمز عبور اشتباه است.', 'danger')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('شما با موفقیت خارج شدید.', 'info')
    return redirect(url_for('main.home'))

@auth_bp.route('/my-orders')
@login_required
def my_orders():
    orders = AuthService.get_user_orders(current_user.id)
    return render_template('auth/my_orders.html', orders=orders)


@auth_bp.route('/order/<int:order_id>')
@login_required
def order_detail(order_id): 
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        abort(403)
    return render_template('auth/order_detail.html', order=order)

