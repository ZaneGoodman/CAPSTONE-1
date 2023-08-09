# "Triva App"
from flask import Flask, request, render_template, redirect, session, g , flash, jsonify
from models import db, connect_db, User, SavedQuestionsAndAnswers, UserTestQuestions, UserTest
from forms import AuthenticateUserForm
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
import requests

API_BASE_URL = "https://jservice.io"
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

def logout_user():
    """Logout user"""
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route('/login', methods=["GET", "POST"])
def login():
    """login User"""
    form = AuthenticateUserForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,form.password.data)
        if user:
            login_user(user)
            flash(f"Welcome {user.username}", "success")
            return redirect("/")
        flash("Invalid username/password", "error")
 
    return render_template("auth/log_in.html", form=form)

@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Sign up user"""
    form = AuthenticateUserForm()
    if form.validate_on_submit():
        try:
            user = User.register(username=form.username.data, password=form.password.data)
            db.session.add(user)
            db.session.commit()

            
        except IntegrityError:
            flash("Username already taken, Try again")
            return render_template("auth/sign_up.html", form=form)
    
        login_user(user)
        flash("Welcome to Trivia Nation!", "success")
        return redirect("/")
    
    return render_template("auth/sign_up.html", form=form)
    
@app.route('/logout', methods=["GET","POST"])
def logout():
    """Log out a user"""
    logout_user()
    flash("You have been Logged Out", "success")
    return redirect('/login')
        


@app.route('/')
def welcome_page():
    return render_template('welcome.html')

@app.route('/random_questions', methods=["GET", "POST"])
def show_random_questions():
    random_url = f"{API_BASE_URL}/api/random"
    resp = requests.get(random_url)
    json_resp = resp.json()

    question = json_resp[0]['question']
    answer = json_resp[0]['answer']

    trivia_response = {
        "question" : question,
        "answer" : answer
    }
    return render_template("random_question.html", trivia_response=trivia_response)

    
@app.route('/save_question', methods=["POST"])
def add_question_to_db():
    question = request.json["question"]
    answer = request.json["answer"]
    new_saved_question = SavedQuestionsAndAnswers(user_id=g.user.id, question=question, answer=answer)
    db.session.add(new_saved_question)
    db.session.commit()
    
    return redirect('/random_questions')

@app.route('/new_test_questions')
def user_picks_test_questions():
    saved_questions = SavedQuestionsAndAnswers.query.filter(SavedQuestionsAndAnswers.user_id == g.user.id).all()
    return render_template("test/select_test_questions.html", saved_questions=saved_questions)
    

@app.route('/create_new_test', methods=["POST"])
def create_new_test():
    questions = request.form.getlist("question")
    picked_questions = [SavedQuestionsAndAnswers.query.filter(SavedQuestionsAndAnswers.question == question).first() for question in questions]
    new_test = UserTest(user_id=g.user.id)
    db.session.add(new_test)
    db.session.commit()
    for question in picked_questions:
        test_question = UserTestQuestions(user_id=g.user.id, test_id=new_test.test_id, question_answer_id=question.id)
        db.session.add(test_question)
        db.session.commit()
    
    return redirect(f'/test/{new_test.test_id}')


@app.route('/test/<int:test_id>')
def populate_each_test_question(test_id):

# @app.route('/')
# def test_api_routes():
#     random_url = f"{API_BASE_URL}/api/random"
    

#     random_resp = requests.get(random_url)


#     rr = random_resp.json()
#     question = rr[0]['question']
#     answer = rr[0]['answer']
   

#     return render_template('welcome.html', question=question, answer=answer)
# API_BASE_URL = "https://jservice.io"