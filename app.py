# "Triva App"
from flask import Flask, request, render_template, redirect
from models import db, connect_db, User, SavedQuestionsAndAnswers, UserTestQuestions, UserTest
from flask_debugtoolbar import DebugToolbarExtension

app = Flask(__name__)


app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///Trivia"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True


from flask_debugtoolbar import DebugToolbarExtension

app.config["SECRET_KEY"] = "SECRET!"
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False
debug = DebugToolbarExtension(app)

connect_db(app)



# @app.route('/')
# def test_api_routes():
#     random_url = f"{API_BASE_URL}/api/random"
    

#     random_resp = requests.get(random_url)


#     rr = random_resp.json()
#     question = rr[0]['question']
#     answer = rr[0]['answer']
   

#     return render_template('index.html', question=question, answer=answer)
# API_BASE_URL = "https://jservice.io"