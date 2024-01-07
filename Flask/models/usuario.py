from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin):

    def __init__(self, usuario, password):
        self.id=usuario
        self.usuario = usuario
        self.password = password #generate_password_hash(password)
    def set_password(self, password):
        self.password = generate_password_hash(password)

    def get_id(self):
        return str(self.id)
      
    @classmethod
    def check_password(self, hashed_password, password):
        return check_password_hash(hashed_password, password)


'''hashed_password=generate_password_hash("aprov1")
print(hashed_password)'''
