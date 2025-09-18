from flask import Blueprint, session, redirect, url_for, flash, request
from . import services
from flask import render_template

cart_bp = Blueprint('cart', __name__)

@cart_bp.route('/add-to-cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
        cart=session.get('cart',{})
        product_id_str = str(product_id)
        if product_id_str in cart:
            cart[product_id_str] += 1
        else:
            cart[product_id_str] = 1
        session['cart'] = cart
        flash(f'محصول با موفقیت به سبد خرید اضافه شد!', 'success')
        return redirect(request.referrer or url_for('main.home'))

@cart_bp.route('/cart')
def view_cart():
    cart_items, total_price = services.get_cart_data()
    return render_template('cart.html', cart_items=cart_items, total_price=total_price)

@cart_bp.route('/remove-from-cart-form/<int:product_id>')
def remove_from_cart_form(product_id):
    return remove_from_cart(product_id)

@cart_bp.route('/remove-from-cart/<int:product_id>', methods=['GET','POST'])
def remove_from_cart(product_id):
    cart=session.get('cart',{})
    product_id_str = str(product_id)
    if product_id_str in cart:
        del cart[product_id_str]
        session['cart'] = cart
        flash('محصول از سبد خرید شما حذف شد.', 'success')
    else:
        flash('خطا: این محصول در سبد خرید شما نبود.', 'warning')
    return redirect(url_for('cart.view_cart'))

@cart_bp.route('/update-cart', methods=['POST'])
def update_cart():
    success=services.update_cart_quantity(request.form)
    if success:
        flash('سبد خرید شما با موفقیت به‌روزرسانی شد.', 'success')
    else:
        flash('خطایی در به‌روزرسانی سبد خرید رخ داد یا تغییری ایجاد نشد.', 'info')
    return redirect(url_for('cart.view_cart'))

@cart_bp.route('/checkout')
def checkout():
    cart_items, total_price = services.get_cart_data()
    if not cart_items:
        flash("سبد خرید شما خالی است و نمی‌توانید تسویه حساب کنید.", "warning")
        return redirect(url_for('cart.view_cart'))
    return render_template('checkout.html', cart_items=cart_items, total_price=total_price)

@cart_bp.route('/place-order', methods=['POST'])
def place_order():
    customer_info=request.form
    order, error_message = services.create_order(customer_info)
    if order:
        flash('سفارش شما با موفقیت ثبت شد!', 'success')
        return render_template('order-confirmation.html', order=order)
    else:
        flash(error_message or 'خطا در ثبت سفارش.', 'danger')
        return redirect(url_for('cart.view_cart'))

