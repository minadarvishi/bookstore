from flask import Blueprint, render_template,request , abort
from models import Product, Publisher, Category
from admin import services as services
from sqlalchemy import or_ , func
main_bp = Blueprint('main', __name__)
@main_bp.route('/')
def home():

    products = Product.query.filter(Product.stock > 0).order_by(Product.id.desc()).all()
    newest_products = Product.query.filter(Product.stock > 0).order_by(Product.id.desc()).limit(8).all()
    best_selling = services.get_best_selling_products(limit=5)
    publishers = Publisher.query.limit(6).all()
    categories = Category.query.all()
    return render_template("index.html", products=products, publishers=publishers
                           , categories=categories , newest_products=newest_products , best_selling=best_selling)
@main_bp.route('/search')
def search():
    search_query = request.args.get('query', '')
    sort_by = request.args.get('sort', 'newest')
    results = []
    if search_query:
        lower_query = search_query.lower()
        search_pattern = f"%{lower_query}%"
        query = Product.query.join(Publisher).join(Category).filter(
            or_(
                func.lower(Product.name).like(search_pattern),
                func.lower(Product.author).like(search_pattern),
                func.lower(Publisher.name).like(search_pattern),
                func.lower(Category.name).like(search_pattern)
            )
        ).filter(Product.stock > 0)

        if sort_by == 'price_asc':
            query = query.order_by(Product.price.asc())
        elif sort_by == 'price_desc':
            query = query.order_by(Product.price.desc())
        else:
            query = query.order_by(Product.id.desc())
        results = query.all()
    return render_template('search-results.html',
                           products=results,
                           query=search_query,
                           current_sort=sort_by,
                           page_title=f"نتایج جستجو برای: '{search_query}'")
@main_bp.route('/product/<int:product_id>')
def product_detail(product_id):
    product=Product.query.get(product_id)
    if not product:
        abort(404)
    return render_template('product-detail.html', product=product)
@main_bp.route('/shop')
def shop():
    sort_by = request.args.get('sort', 'newest')
    query = Product.query.filter(Product.stock > 0)

    if sort_by == 'price_asc':
        query = query.order_by(Product.price.asc())
    elif sort_by == 'price_desc':
        query = query.order_by(Product.price.desc())
    else:  # 'newest'
        query = query.order_by(Product.id.desc())

    all_products = query.all()
    return render_template("shop.html", products=all_products, current_sort=sort_by,page_title="فروشگاه")
@main_bp.route('/contact')
def contact():
    return render_template("contact.html")
@main_bp.route('/about')
def about():
    return render_template("about.html")
@main_bp.route('/category/<int:category_id>')
def view_by_category(category_id):
    sort_by = request.args.get('sort', 'newest')
    category = Category.query.get_or_404(category_id)
    query = Product.query.with_parent(category).filter(Product.stock > 0)
    if sort_by == 'price_asc':
        query = query.order_by(Product.price.asc())
    elif sort_by == 'price_desc':
        query = query.order_by(Product.price.desc())
    else:
        query = query.order_by(Product.id.desc())
    products = query.all()
    return render_template('search-results.html',
                           products=products,
                           page_title=f"دسته‌بندی: {category.name}",
                           current_sort=sort_by,
                           category_id=category_id,
                           query=None, publisher_id=None)
@main_bp.route('/publisher/<int:publisher_id>')
def view_by_publisher(publisher_id):
    publisher = Publisher.query.get(publisher_id)
    if not publisher:
        abort(404)
    products =[]
    for p in publisher.products:
        if p.stock > 0:
            products.append(p)
    return render_template('shop.html',
                           products=products,
                           page_title=f"نشریه: {publisher.name}")