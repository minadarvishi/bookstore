from flask import Flask, render_template,session,url_for,request,redirect,flash
from extensions import db
from admin.routes import admin_bp
from main.routes import main_bp
from cart.routes import cart_bp
import os

def create_app():
    app = Flask(__name__)

    # --- پیکربندی پایگاه داده ---
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'bookstore.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # --- اتصال افزونه‌ها به اپلیکیشن ---
    db.init_app(app)
    with app.app_context():
        db.create_all()
    # --- افزودن کلید مخفی برای امنیت سشن ---
    app.config['SECRET_KEY'] = 'a-super-secret-key-that-no-one-can-guess'

    # --- ثبت کردن Blueprintها ---
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(cart_bp)

    # ساخت دیتابیس
    @app.cli.command('init-db')
    def init_db_command():
        db.create_all()
        print('Initialized the database and created all tables.')


    @app.context_processor
    def cart_count():
        cart = session.get('cart',{})
        items=sum(cart.values())
        return dict(items_count=items)

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('404.html'), 404





    return app
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)