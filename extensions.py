from flask_login import LoginManager




#پایگاه داده
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

#userlogin
login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    from models import User
    return db.session.get(User, int(user_id))


