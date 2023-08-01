from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt


db = SQLAlchemy()
bcrypt = Bcrypt()

def connect_db(app):
    db.app = app
    db.init_app(app)



class User(db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    username = db.Column(db.String(30), unique=True, nullable=False)

    password = db.Column(db.Text, nullable=False)

    saved_questions = db.relationship("SavedQuestionsAndAnswers", backref="user")

    tests = db.relationship("UserTest", backref="user")

    @classmethod
    def register(cls, username, password):
        """Register new user with hashed pswd and return the user"""

        hashed = bcrypt.generate_password_hash(password)
        # turn bytesting into normal (unicode utf8) string
        hashed_utf8 = hashed.decode("utf8")

        # return the instace of user with their username and hased password
        return cls(username=username, password=hashed_utf8)
    
    @classmethod
    def authenticate(cls, username, password):
        """Validate that the user exist & password is correct. 
        Return the user if valid, else return False """

        user = User.query.filter_by(username=username).first()
        
        if user and bcrypt.check_password_hash(user.password, password):
            return user
        else:
            return False
        



class SavedQuestionsAndAnswers(db.Model):

    __tablename__ = "saved_questions_and_answers"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"))

    question = db.Column(db.Text, unique=True, nullable=False)

    answer = db.Column(db.Text, unique=True, nullable=False)

    user = db.relationship("User", backref="user_questions_answers")


class UserTestQuestions(db.Model):

    __tablename__ = "user_test_questions"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"))

    test_id = db.Column(db.Integer, db.ForeignKey("user_test.test_id", ondelete="CASCADE"))

    question_answer_id =  db.Column(db.Integer, db.ForeignKey("saved_questions_and_answers.id"))
    # possible problem: I dont want the questions in the test deleted if the user deletes questions from their saved questions. 
    question_answer = db.relationship("SavedQuestionsAndAnswers", backref="test_questions")

    test = db.relationship("UserTest", backref="test_questions")

    correct = db.Column(db.Boolean)


class UserTest(db.Model):

    __tablename__ = "user_test"

    test_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    user_id: db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"))

    score = db.Column(db.Integer)
    # Possible Problem: I need to make sure that the backref for userTestQuestions wors for this table. I want to be able to call UserTest.test_questions and get all of the questions for this test instance.