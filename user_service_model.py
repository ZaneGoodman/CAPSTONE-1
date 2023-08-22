from flask_bcrypt import Bcrypt
from models import db, connect_db, User
from flask import requests
bcrypt = Bcrypt()

class UserServiceModel(requests.auth.AuthBase):
    """Authentification functions for user"""
    
    def __register__(username, password):
        """Register new user with hashed pswd and return the user"""

        hashed = bcrypt.generate_password_hash(password)
        # turn bytesting into normal (unicode utf8) string
        hashed_utf8 = hashed.decode("utf8")

        # return the instace of user with their username and hased password
        return User(username=username, password=hashed_utf8)
    
    
    def __authenticate__(username, password):
        """Validate that the user exist & password is correct. 
        Return the user if valid, else return False """

        user = User.query.filter_by(username=username).first()
        
        if user and bcrypt.check_password_hash(user.password, password):
            return user
        else:
            return False