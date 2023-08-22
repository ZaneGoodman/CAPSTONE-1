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

        



class SavedQuestionsAndAnswers(db.Model):

    __tablename__ = "saved_questions_and_answers"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"))

    question = db.Column(db.Text, unique=True, nullable=False)

    answer = db.Column(db.Text, unique=True, nullable=False)

    


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

    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"))

    score = db.Column(db.Integer)
    # Possible Problem: I need to make sure that the backref for userTestQuestions wors for this table. I want to be able to call UserTest.test_questions and get all of the questions for this test instance.