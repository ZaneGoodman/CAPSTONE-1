from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Length


class AuthenticateUserForm(FlaskForm):
    """Log in or Sign up a User"""

    username = StringField("Username", validators=[DataRequired()])

    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])