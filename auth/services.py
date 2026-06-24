from models import User, db , Order , Address

class AuthService :
    # ثبت نام کاربر
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
    #ورود کاربر
    @staticmethod  
    def authenticate_user(email , password):

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            return user
        
        return None

    @staticmethod
    def get_user_orders(user_id):
        return Order.query.filter_by(user_id = user_id).order_by(Order.order_date.desc()).all()
   
    @staticmethod
    def update_profile(user, name, phone, address):
        user.name = name
        user.phone = phone
        user.address = address
        
        db.session.add(user)
        db.session.commit()
        return user



class AddressService:
    @staticmethod
    def get_user_addresses(user_id):
        return Address.query.filter_by(user_id=user_id).all()

    @staticmethod
    def add_address(user_id, title, recipient_name, phone, address_line, is_default=False):
        
        has_addresses = Address.query.filter_by(user_id=user_id).first()
        if not has_addresses:
            is_default = True

        
        if is_default:
            AddressService.clear_defaults(user_id)

        new_address = Address(
            user_id=user_id,
            title=title,
            recipient_name=recipient_name,
            phone=phone,
            address_line=address_line,
            is_default=is_default
        )
        db.session.add(new_address)
        db.session.commit()
        return new_address

    @staticmethod
    def delete_address(user_id, address_id):
        address = Address.query.filter_by(id=address_id, user_id=user_id).first()
        if address:
            was_default = address.is_default
            db.session.delete(address)
            db.session.commit()
            
            if was_default:
                remaining = Address.query.filter_by(user_id=user_id).first()
                if remaining:
                    remaining.is_default = True
                    db.session.commit()
            return True
        return False
    # انتخاب ادرس پیش فرض
    @staticmethod
    def set_default(user_id, address_id):
        AddressService.clear_defaults(user_id)
        address = Address.query.filter_by(id=address_id, user_id=user_id).first()
        if address:
            address.is_default = True
            db.session.commit()
            return True
        return False

    @staticmethod
    def clear_defaults(user_id):
        Address.query.filter_by(user_id=user_id).update({Address.is_default: False})
        db.session.commit()