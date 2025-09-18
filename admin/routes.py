from flask import Blueprint, render_template
from flask import request, redirect, url_for, flash,session
from models import Product, Category, Order, Publisher
from . import services
from .decorators import admin_required
admin_bp = Blueprint('admin', __name__,template_folder='templates',static_folder='static')
@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    stats = services.get_dashboard_stats()
    return render_template("home/index.html",stats=stats)

# --- Product route ---
@admin_bp.route('/add-product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        form_data = request.form
        img= request.files.get("image_file")
        success=services.add_new_product(form_data,img)

        if success:
            flash('محصول جدید با موفقیت اضافه شد!', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('خطا در افزودن محصول. لطفاً دوباره تلاش کنید.', 'danger')
    categories = services.get_all_category()
    publishers = services.get_all_publisher()
    return render_template("home/add-product.html", categories=categories, publishers=publishers)
@admin_bp.route('/products')
def list_products():
    #نمایش لیست محصولات
    products = Product.query.all()
    return render_template('home/products.html', products=products)
@admin_bp.route('/edit-product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    product_to_edit = Product.query.filter_by(id=product_id).first()
    if request.method == 'POST':
        form_data = request.form
        img= request.files.get("image_file")
        success=services.update_existing_product(product_to_edit,form_data,img)
        if success:
            flash('محصول با موفقیت به‌روزرسانی شد!', 'success')
            return redirect(url_for('admin.list_products'))
        else:
            flash('خطا در به‌روزرسانی محصول.', 'danger')
    categories = services.get_all_category()
    publishers = services.get_all_publisher()
    return render_template('home/add-product.html', product=product_to_edit , categories=categories,
                           publishers=publishers)
@admin_bp.route('/delete-product/<int:product_id>', methods=['GET', 'POST'])
def delete_product(product_id):
    success=services.delete_product(product_id)
    if success:
        flash('محصول با موفقیت حذف شد.', 'success')
    else:
        flash('خطا در حذف محصول.', 'danger')
    return redirect(url_for('admin.list_products'))

# --- Category route ---
@admin_bp.route('/categories',methods=['GET','POST'])
def list_categories():
    if request.method == 'POST':
        category_name = request.form.get('name')
        if category_name:
            success=services.add_new_category(category_name)
            if success:
                flash('دسته‌بندی جدید با موفقیت اضافه شد.', 'success')
            else:
                flash('خطا: نام دسته‌بندی نمی‌تواند تکراری باشد.', 'danger')
        return redirect(url_for('admin.list_categories'))

    categories = Category.query.all()
    return render_template('home/categories-list.html', categories=categories)
@admin_bp.route('/edit-category/<int:category_id>', methods=['GET', 'POST'])
def edit_category(category_id):
    category=services.get_category_id(category_id)
    if not category:
        return "Category not found", 404
    if request.method == 'POST':
        new_name = request.form.get('name')
        if new_name:
            success = services.update_category(category, new_name)
            if success:
                flash('دسته‌بندی با موفقیت به‌روزرسانی شد.', 'success')
            else:
                flash('خطا: نام دسته‌بندی نمی‌تواند تکراری باشد.', 'danger')
            return redirect(url_for('admin.list_categories'))
    return render_template('home/category-form-edit.html', category=category)
@admin_bp.route('/delete-category/<int:category_id>', methods=['GET', 'POST'])
def delete_category(category_id):
    success, message = services.delete_category(category_id)
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    return redirect(url_for('admin.list_categories'))

# --- Order route ---
@admin_bp.route('/orders')
def list_orders():
    status_filter = request.args.get('status')
    query = Order.query.order_by(Order.order_date.desc())
    if status_filter in ['Pending', 'Posted']:
        query = query.filter(Order.status == status_filter)
    orders = query.all()
    return render_template('home/orders-list.html', orders=orders, current_filter=status_filter)
@admin_bp.route('/order/posted/<int:order_id>', methods=['POST'])
def posted_product(order_id):
    success, message = services.change_order_status(order_id, 'Posted')
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')

    return redirect(url_for('admin.list_orders'))
@admin_bp.route('/order/<int:order_id>', methods=['GET', 'POST'])
def order_details(order_id):
    order = Order.query.get(order_id)
    if not order:
        return "Order not found", 404
    return render_template('home/order-details.html', order=order)

# --- Publisher route
@admin_bp.route('/publisher',methods=['GET','POST'])
def list_publishers():
    if request.method == 'POST':
        form_data = request.form
        logo_file = request.files.get('logo_file')
        success, message = services.add_new_publisher(form_data, logo_file)
        if success:
            flash(message, 'success')
        else:
            flash(message, 'danger')
        return redirect(url_for('admin.list_publishers'))
        # برای درخواست GET
    all_publishers = services.get_all_publisher()
    return render_template('home/publishers-list.html',publishers=all_publishers)
@admin_bp.route('/edit-publisher/<int:publisher_id>', methods=['GET', 'POST'])
def edit_publisher(publisher_id):
    publisher = services.get_publisher_id(publisher_id)
    if not publisher:
        return "Publisher not found", 404
    if request.method == 'POST':
        form_data = request.form
        logo_file = request.files.get('logo_file')
        success, message = services.update_publisher(publisher, form_data, logo_file)
        if success:
            flash(message, 'success')
        else:
            flash(message, 'danger')
        return redirect(url_for('admin.list_publishers'))
    return render_template('home/publisher-form-edit.html', publisher=publisher)
@admin_bp.route('/delete-publisher/<int:publisher_id>', methods=['GET', 'POST'])
def delete_publisher(publisher_id):
    success, message = services.delete_publisher(publisher_id)
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')

    return redirect(url_for('admin.list_publishers'))

#--- Login admin
@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'admin' and password == '12345':
            session['is_admin'] = True
            flash('شما با موفقیت وارد شدید.', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('نام کاربری یا رمز عبور اشتباه است.', 'danger')

    return render_template('login.html')
@admin_bp.route('/logout')
def logout():
    session.pop('is_admin', None)
    flash('شما با موفقیت خارج شدید.', 'info')
    return redirect(url_for('admin.login'))