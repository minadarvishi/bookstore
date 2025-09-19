import os
import uuid # برای ساختن نام فایل منحصر به فرد
from werkzeug.utils import secure_filename #  امن‌سازی نام فایل
from flask import current_app
from extensions import db
from sqlalchemy import func
from models import Product, Category, Order, Publisher, OrderItem
from sqlalchemy.exc import IntegrityError


# --- Product Services ---
#ذخیره عکس
def save_product_img(img_file):
    # اگر عکسی آپلود نشده بود، از عکس پیش‌فرض استفاده میکند
    if not img_file or img_file.filename == '':
        return 'default.jpg'

    # ساخت یک نام منحصر برای تصویر
    filename = secure_filename(img_file.filename)
    file_ext=os.path.splitext(filename)[1]# پسوند فایل را جدا کن
    unique_filename = str(uuid.uuid4()) + file_ext

    #  ساخت مسیر کامل و ذخیره فایل
    upload_folder = os.path.join(current_app.root_path,'admin','static','uploads')
    os.makedirs(upload_folder, exist_ok=True)
    img_path = os.path.join(upload_folder, unique_filename)
    img_file.save(img_path)

    return unique_filename
#افزودن محصول و ذخیره در دیتابیس
def add_new_product(form_data,img):
    publisher_id_val = form_data.get('publisher_id')
    # داده های فرم
    new_product = Product(
        category_id=int(form_data.get('category_id')),
        publisher_id=int(publisher_id_val) if publisher_id_val else None,
        name=form_data.get('name'),
        author=form_data.get('author'),
        price=form_data.get('price'),
        stock=form_data.get('stock'),
        description=form_data.get('description'),
        isbn=form_data.get('isbn'),
        year=form_data.get('year'),
        pages=form_data.get('pages'),
        image_file=save_product_img(img)
    )

    # ذخیره در دیتابیس
    try:
        db.session.add(new_product)
        db.session.commit()
        return True
    except Exception as e:
        print(f"Error adding product: {e}")
        db.session.rollback()
        return False
# اپدیت محصول
def update_existing_product(product,form_data,img):
    product.category_id=int(form_data.get('category_id'))
    publisher_id_val = form_data.get('publisher_id')
    product.publisher_id = int(publisher_id_val) if publisher_id_val else None
    product.name = form_data.get('name')
    product.author = form_data.get('author')
    product.price = form_data.get('price')
    product.stock = form_data.get('stock')
    product.description = form_data.get('description')
    product.isbn = form_data.get('isbn')
    product.year = form_data.get('year')
    product.pages = form_data.get('pages')

    if img and img.filename != '':
        product.image_file = save_product_img(img)
    else:
        product.image_file ='default.jpg'
    try:
        db.session.commit()
        return True
    except Exception as e:
        print(f"Error updating product: {e}")
        db.session.rollback()
        return False
# حذف محصول
def delete_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return False

    image_filename = product.image_file
    try:
        db.session.delete(product)
        db.session.commit()

        if image_filename and image_filename != 'default.jpg':
            image_path = os.path.join(current_app.root_path,'admin','static','uploads', image_filename)
            if os.path.exists(image_path):
                os.remove(image_path)
        return True

    except Exception as e:
        print(f"Error deleting product: {e}")
        db.session.rollback()
        return False
# ارسال محصول
def change_order_status(order_id, new_status):
    order = Order.query.get(order_id)
    if not order:
        return False, "سفارش پیدا نشد."
    try:
        order.status = new_status
        db.session.commit()
        return True, "وضعیت سفارش با موفقیت تغییر کرد."
    except Exception as e:
        db.session.rollback()
        return False, f"خطا در تغییر وضعیت: {e}"
# پر فروش
def get_best_selling_products(limit=5):
    best_sellers = db.session.query(
        Product,
        func.sum(OrderItem.quantity).label('total_sold')
    ).join(OrderItem, OrderItem.product_id == Product.id) \
        .group_by(Product.id) \
        .order_by(func.sum(OrderItem.quantity).desc()) \
        .limit(limit).all()

    products_only = [product for product, total_sold in best_sellers]
    return products_only


# --- Category Services ---
# خواندن تمام دسته‌بندی‌ها
def get_all_category():
    return Category.query.order_by(Category.name).all()
# افرودن دسته بندی
def add_new_category(name):
    try:
        new_category = Category(name=name)
        db.session.add(new_category)
        db.session.commit()
        return True
    except Exception as e:
        print(f"Error adding new category: {e}")
        db.session.rollback()
        return False
#بازگرداندن id دسته بندی
def get_category_id(category_id):
    return Category.query.get(category_id)
# اپدیت دسته بندی
def update_category(category,new_name):
    try:
        category.name = new_name
        db.session.commit()
        return True
    except Exception as e:
        print(f"Error updating category: {e}")
        db.session.rollback()
        return False
# حذف دسته بندی
def delete_category(category_id):
    category = Category.query.get(category_id)
    if not category:
        return False
    if category.products:
        return (False, "نمی‌توانید این دسته‌بندی را حذف کنید چون محصولاتی در آن وجود دارد.")
    try:
        db.session.delete(category)
        db.session.commit()
        return (True, "دسته‌بندی با موفقیت حذف شد.")
    except Exception as e:
        db.session.rollback()
        return (False, f"خطای دیتابیس: {e}")

# --- Publisher Services ---
def get_all_publisher():
    return Publisher.query.order_by(Publisher.name).all()
def add_new_publisher(form_data, logo_file):
    try:
        name = form_data.get('name')
        if not name:
            return False, "نام ناشر نمی‌تواند خالی باشد."
        logo_path = save_product_img(logo_file)
        new_publisher = Publisher(
            name=name,
            logo_file=logo_path if logo_path else 'publishers/default-logo.png'
        )
        db.session.add(new_publisher)
        db.session.commit()
        return True, "ناشر جدید با موفقیت اضافه شد."
    except IntegrityError:
        db.session.rollback()
        return False, "خطا: ناشری با این نام از قبل وجود دارد."
    except Exception as e:
        db.session.rollback()
        return False, f"یک خطای غیرمنتظره رخ داد: {e}"
def get_publisher_id(publisher_id):
    return Publisher.query.get(publisher_id)
def update_publisher(publisher, form_data, logo_file):
    try:
        new_name = form_data.get('name')
        if not new_name:
            return False, "نام ناشر نمی‌تواند خالی باشد."
        publisher.name = new_name
        if logo_file and logo_file.filename != '':
            old_logo_path = None
            if publisher.logo_file and publisher.logo_file != 'default-logo.png':
                old_logo_path = os.path.join(current_app.static_folder, 'uploads', publisher.logo_file)
            publisher.logo_file = save_product_img(logo_file)
            if old_logo_path and os.path.exists(old_logo_path):
                os.remove(old_logo_path)
        db.session.commit()
        return True, "ناشر با موفقیت به‌روزرسانی شد."
    except IntegrityError:
        db.session.rollback()
        return False, "خطا: ناشری دیگر با این نام وجود دارد."
    except Exception as e:
        db.session.rollback()
        return False, f"یک خطای غیرمنتظره رخ داد: {e}"
def delete_publisher(publisher_id):
    publisher = get_publisher_id(publisher_id)
    if not publisher:
        return False, "ناشر پیدا نشد."
    if publisher.products:
        return False, "خطا: این ناشر دارای کتاب است و قابل حذف نیست."
    try:
        logo_to_delete = publisher.logo_file
        db.session.delete(publisher)
        db.session.commit()
        if logo_to_delete and logo_to_delete != 'publishers/default-logo.png':
            logo_path = os.path.join(current_app.static_folder, 'uploads', logo_to_delete)
            if os.path.exists(logo_path):
                os.remove(logo_path)

        return True, "ناشر با موفقیت حذف شد."
    except Exception as e:
        db.session.rollback()
        return False, f"خطا در حذف ناشر: {e}"

# --- گزارش گیری ---
def get_dashboard_stats():
    total_revenue = db.session.query(func.sum(Order.total_price)).scalar() or 0
    total_order_pending = db.session.query(Order).filter(Order.status == 'Pending').count()
    total_order_posted = db.session.query(Order).filter(Order.status == 'Posted').count()
    total_products_sold = db.session.query(func.sum(OrderItem.quantity)).scalar() or 0
    best_selling_products = db.session.query(
        Product.name,
        func.sum(OrderItem.quantity).label('total_sold')
    ).join(OrderItem, OrderItem.product_id == Product.id)\
     .group_by(Product.name)\
     .order_by(func.sum(OrderItem.quantity).desc())\
     .limit(5).all()

    stats = {
        'total_revenue': total_revenue,
        'total_order_pending': total_order_pending,
        'total_order_posted':total_order_posted,
        'total_products_sold': total_products_sold,
        'best_selling_products': best_selling_products,
    }

    return stats