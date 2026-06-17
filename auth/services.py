from models import User, db , Order


class AuthService :

    @staticmethod
    def register_user (name, email, password):

        existing_user = User.query.filter_by(email = email).first()
        if existing_user:
            return None ,  "این ایمیل قبلاً ثبت شده است."

        new_user = User(name = name , email = email)
        new_user.set_password(password)

        try:
            db.session.add(new_user)
            db.session.commit()
            return new_user , None
        except Exception as e:
            print(f"Error : {e}")
            db.session.rollback()
            return None, "خطایی در ثبت اطلاعات رخ داد."

    @staticmethod  
    def authenticate_user(email , password):

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            return user
        
        return None

    @staticmethod
    def get_user_orders(user_id):
        return Order.query.filter_by(user_id = user_id).order_by(Order.order_date.desc()).all()