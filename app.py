from flask import Flask, render_template,session
from extensions import db , migrate
from admin.routes import admin_bp
from main.routes import main_bp
from cart.routes import cart_bp
from extensions import login_manager
from auth.routes import auth_bp
import os




def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'a-super-secret-key-that-no-one-can-guess'

    # --- اتصال هوشمند به دیتابیس ---
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        basedir = os.path.abspath(os.path.dirname(__file__))
        db_url = 'sqlite:///' + os.path.join(basedir, 'bookstore.db')
        print("--- RUNNING ON LOCAL SQLITE DB ---")
    if db_url and db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    migrate.init_app(app,db,render_as_batch=True)

    # ------------------------------------
    #userlogin
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # --- ثبت کردن Blueprintها ---
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(cart_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')

    #  ساخت دیتابیس
    @app.cli.command('init-db')
    def init_db_command():
        db.create_all()
        print('Initialized the database and created all tables.')

    @app.context_processor
    def cart_count():
        cart = session.get('cart',{})
        items=sum(cart.values())
        return dict(items_count=items)


    # --- کنترل‌کننده خطای 404 ---
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('404.html'), 404
    

    # روت موقت برای ساخت ادمین روی هاست رندر
    @app.route('/make-me-admin')
    def make_me_admin():
        from models import User, db
        admin = User.query.filter_by(email="admin@bookstore.com").first()
        if not admin:
            admin = User(name="مدیر سیستم", email="admin@bookstore.com")
            admin.set_password("admin12345")
            admin.is_admin = True
            db.session.add(admin)
            db.session.commit()
            return "حساب کاربری ادمین با موفقیت ساخته شد!"
        return "حساب کاربری ادمین از قبل وجود دارد."

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
