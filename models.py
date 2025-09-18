# مدل‌های پایگاه داده
from extensions import db

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    #دسته بندی
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'),nullable=False)
    category = db.relationship('Category', backref=db.backref('products', lazy=True))

    #نشریه
    publisher_id = db.Column(db.Integer, db.ForeignKey('publisher.id'),nullable=True)
    publisher=db.relationship('Publisher', backref=db.backref('products', lazy=True))


    name = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    stock = db.Column(db.Integer, default=1)
    description = db.Column(db.Text, nullable=True)
    isbn = db.Column(db.String(13), unique=True, nullable=True)
    year = db.Column(db.Integer, nullable=True)
    pages = db.Column(db.Integer, nullable=True)
    image_file = db.Column(db.String(100), nullable=False, default='default.jpg')


    def __repr__(self):
        return f"Product('{self.name}', '{self.author}')"

class Publisher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    logo_file = db.Column(db.String(100), nullable=True, default='default-logo.png')

    def __repr__(self):
        return f"Publisher('{self.name}')"

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

    def __repr__(self):
        return f"Category('{self.name}')"

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    customer_phone = db.Column(db.String(20), nullable=False)
    customer_address = db.Column(db.Text, nullable=False)
    total_price = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Pending')
    order_date = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())


    items = db.relationship('OrderItem', backref='order', lazy=True)

    def __repr__(self):
        return f"Order('{self.id}', '{self.customer_name}')"

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

    product=db.relationship('Product', backref=db.backref('products', lazy=True))

    def __repr__(self):
        return f"OrderItem('Order: {self.order_id}', 'Product: {self.product_id}', 'Qty: {self.quantity}')"

