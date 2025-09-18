from flask import session
from extensions import db
from models import Product, Order , OrderItem


def get_cart_data():
    cart_data = session.get("cart",{})
    cart_items = []
    total_cart_price = 0

    if not cart_data:
        return [],0

    product_ids = list(cart_data.keys())
    product_from_db=Product.query.filter(Product.id.in_(product_ids)).all()
    for product in product_from_db:
        product_id_str = str(product.id)
        quantity=cart_data[product_id_str]
        sum_price = product.price * quantity
        total_cart_price += sum_price
            
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'sum_price': sum_price,
        })

    return cart_items, total_cart_price

def update_cart_quantity(form_data):
    cart=session.get("cart",{})
    for key in form_data:
        if key.startswith('quantity-'):
            parts=key.split('-')
            p_id_str=parts[1]
            if p_id_str in cart:
                new_quantity=form_data[key]
                try:
                    new_quantity_int = int(new_quantity)
                except ValueError:
                    continue
                if new_quantity_int>0:
                    cart[p_id_str]=new_quantity_int
                else:
                    del cart[p_id_str]
        session['cart'] = cart
    return True

def create_order(customer_info):
    cart_items, total_price =get_cart_data()
    if not cart_items:
        return None, "سبد خرید شما خالی است."

    #اعتبارسنجی موجودی
    for item in cart_items:
        if item['product'].stock < item['quantity']:
            error_message = f"موجودی محصول '{item['product'].name}' کافی نیست. فقط {item['product'].stock} عدد باقی مانده است."
            return None, error_message
    try:
        new_order = Order(
            customer_name=customer_info.get('customer_name'),
            customer_phone=customer_info.get('customer_phone'),
            customer_address=customer_info.get('customer_address'),
            total_price=total_price,
        )

        for item in cart_items:
            order_item = OrderItem(
                product_id=item['product'].id,
                quantity=item['quantity'],
            )
            product_to_update = item['product']
            product_to_update.stock -= item['quantity']
            new_order.items.append(order_item)

        db.session.add(new_order)
        db.session.commit()
        session.pop('cart',None)

        return new_order, None
    except Exception as e:
        db.session.rollback()
        print(f"Error creating order: {e}")
        return None, f"خطای دیتابیس: {e}"








