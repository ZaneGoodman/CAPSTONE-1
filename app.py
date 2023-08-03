# "Triva App"
from flask import Flask, request, render_template, redirect, session, g
from models import db, connect_db, User, SavedQuestionsAndAnswers, UserTestQuestions, UserTest
from flask_debugtoolbar import DebugToolbarExtension
import requests

CURR_USER_KEY = "curr_user"

app = Flask(__name__)


app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///Trivia"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True


from flask_debugtoolbar import DebugToolbarExtension

app.config["SECRET_KEY"] = "SECRET!"
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False
debug = DebugToolbarExtension(app)

connect_db(app)

@app.before_request
def add_user_to_g():
    """If logged in, add current user to global object"""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None

def login_user(user):
    """Log in the user"""

    session[CURR_USER_KEY] = user.id

def logout_user(user):
    """Logout user"""
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route('/login')
def login():
    



@app.route('/')
def test_api_routes():
    random_url = f"{API_BASE_URL}/api/random"
    

    random_resp = requests.get(random_url)


    rr = random_resp.json()
    question = rr[0]['question']
    answer = rr[0]['answer']
   

    return render_template('welcome.html', question=question, answer=answer)
API_BASE_URL = "https://jservice.io"