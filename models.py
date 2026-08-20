from database import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__='users'

    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(80),unique=True,nullable=False)
    email=db.Column(db.String(120),unique=True,nullable=False)
    phone=db.Column(db.String(20),nullable=False)
    password_hash=db.Column(db.String(256),nullable=False)

    def set_password(self, password):
        self.password_hash=generate_password_hash(password)

    def check_password(self,password):
        return check_password_hash(self.password_hash,password)
    
    def to_dict(self):
        return {
            "id":self.id,
            "username":self.username,
            "email":self.email,
            "phone":self.phone
        }
    
class Products(db.Model):
    __tablename__='products'

    id=db.Column(db.Integer,primary_key=True,nullable=False)
    name=db.Column(db.String(120),nullable=False)
    description=db.Column(db.Text)
    cost=db.Column(db.Float,nullable=False)
    category=db.Column(db.String(50),nullable=False)
    image_url=db.Column(db.String(255))

    def to_dict(self):
        return{
            "id":self.id,
            "name":self.name,
            "description":self.description,
            "cost":self.cost,
            "category":self.category,
            "image_url":self.image_url
        }


        