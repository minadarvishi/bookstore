from flask import Blueprint, render_template , redirect , url_for , flash , request ,abort
from flask import session
from flask_login import login_user , logout_user , login_required , current_user
from auth.services import AuthService , AddressService
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
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard')) if current_user.is_admin else redirect(url_for('main.home'))


    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = AuthService.authenticate_user(email , password)
        if user : 
            login_user(user)

            if user.is_admin:
                flash('خوش آمدید ادمین گرامی!', 'success')
                return redirect(url_for('admin.dashboard'))
            else: 
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('main.home'))
        
        flash('ایمیل یا رمز عبور اشتباه است.', 'danger')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('cart', None) 
    flash('شما با موفقیت خارج شدید.', 'info')
    return redirect(url_for('main.home'))


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        name = request.form.get('name')

        AuthService.update_profile(current_user, name, current_user.phone, current_user.address)
        flash('اطلاعات کاربری بروزرسانی شد.', 'success')
        return redirect(url_for('auth.profile', active_tab='profile-tab'))

    orders = AuthService.get_user_orders(current_user.id)    
    addresses = AddressService.get_user_addresses(current_user.id)

    order_id = request.args.get('open_order', type=int)
    order = None
    if order_id:
        order = Order.query.get_or_404(order_id)
        if order.user_id != current_user.id:
            abort(403)

    return render_template('auth/profile.html', orders=orders, addresses=addresses, order=order)

@auth_bp.route('/my-orders')
@login_required
def my_orders():
    #orders = AuthService.get_user_orders(current_user.id)
    #return render_template('auth/my_orders.html', orders=orders)
    return redirect(url_for('auth.profile', active_tab='orders-tab'))


@auth_bp.route('/order/<int:order_id>')
@login_required
def order_detail(order_id): 
    #order = Order.query.get_or_404(order_id)
    #if order.user_id != current_user.id:
        #abort(403)
    #return render_template('auth/order_detail.html', order=order)
    return redirect(url_for('auth.profile', open_order=order_id))

@auth_bp.route('/profile/address/add', methods=['POST'])
@login_required
def add_address():
    title = request.form.get('title')
    recipient_name = request.form.get('recipient_name')
    phone = request.form.get('phone')
    address_line = request.form.get('address_line')
    is_default = True if request.form.get('is_default') else False
    
    AddressService.add_address(current_user.id, title, recipient_name, phone, address_line, is_default)
    flash('آدرس جدید با موفقیت اضافه شد.', 'success')
    return redirect(url_for('auth.profile'))


@auth_bp.route('/profile/address/delete/<int:address_id>')
@login_required
def delete_address(address_id):
    success = AddressService.delete_address(current_user.id, address_id)
    if success:
        flash('آدرس با موفقیت حذف شد.', 'info')
    else:
        flash('آدرس پیدا نشد یا دسترسی ندارید.', 'danger')
    return redirect(url_for('auth.profile'))


@auth_bp.route('/profile/address/default/<int:address_id>')
@login_required
def set_default_address(address_id):
    success = AddressService.set_default(current_user.id, address_id)
    if success:
        flash('آدرس پیش‌فرض تغییر کرد.', 'success')
    return redirect(url_for('auth.profile'))
