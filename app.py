# "Triva App"
import os
from flask import Flask, request, render_template, redirect, session, g , flash, jsonify
from models import db, connect_db, User, SavedQuestionsAndAnswers, UserTestQuestions, UserTest
from forms import AuthenticateUserForm
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from helpers import api_call_random_question, get_three_fake_answers, add_saved_question_to_db, create_new_test_with_user_questions, convert_data_to_list, check_answer_and_return_index, get_test_score, get_questions_for_test, login_user, logout_user
import requests
import random
from json.decoder import JSONDecodeError

API_BASE_URL = "https://jservice.io"
CURR_USER_KEY = "curr_user"

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///Trivia'))
# app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///Trivia"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True


from flask_debugtoolbar import DebugToolbarExtension

app.config["SECRET_KEY"] = "SECRET!"
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False
debug = DebugToolbarExtension(app)

connect_db(app)

db.create_all()

# authentification

@app.before_request
def add_user_to_g():
    """If logged in, add current user to global object"""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None



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
        


# Welcome & random question routes
@app.route('/')
def welcome_page():
    """Welcome page"""
    return render_template('welcome.html')




@app.route('/random_questions', methods=["GET", "POST"])
def show_random_questions():
    """Show user a random question and answer"""
    # if not g.user:
    #     flash("Access unauthorized.", "danger")
    #     return redirect("/")

    trivia_response = api_call_random_question()
    return render_template("random_question.html", trivia_response=trivia_response)



    
@app.route('/save_question', methods=["POST"])
def add_question_to_db():
    """add saved question to the db"""
    add_saved_question_to_db()
    return redirect('/random_questions')



# Test routes
@app.route('/new_test_questions')
def user_picks_test_questions():
    """Display questions from users saved questions. User picks which to test on"""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    saved_questions = SavedQuestionsAndAnswers.query.filter(SavedQuestionsAndAnswers.user_id == g.user.id).all()
    return render_template("test/select_test_questions.html", saved_questions=saved_questions)
    




@app.route('/create_new_test', methods=["POST"])
def create_new_test():
    """create new test"""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    test_id = create_new_test_with_user_questions()
    return redirect(f'/start_test/{test_id}')




@app.route('/start_test/<int:test_id>')
def start_test(test_id): 
    """get question data from test_id and add to session for index mapping"""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    test_questions = get_questions_for_test(test_id)
    session["questions"] = test_questions
    return redirect(f"/test/0")




@app.route('/test/<int:question_index>')
def populate_each_test_question(question_index):
    """Check if current question is the last question, if not, get next question and answer"""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    questions = session["questions"]
    if (question_index) > (len(questions) -1):
        
        return redirect("/completed")
    else:
        next_question = SavedQuestionsAndAnswers.query.filter(SavedQuestionsAndAnswers.question == questions[question_index]["question"]).first()
        answer = next_question.answer
        """Add correct answer with three fake answers for multiple choice"""
        possible_answers = get_three_fake_answers()
        possible_answers.append(answer)
        random.shuffle(possible_answers)

        return render_template("/test/test.html", question=next_question, index=question_index, possible_answers=possible_answers)
    


@app.route('/test/answers/<int:question_id>', methods=["POST"])
def check_test_answer(question_id):
    """redirect to next question using session index"""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    try:
        index = check_answer_and_return_index(question_id)
        return redirect(f'/test/{index + 1}')
    except TypeError:
        flash("This question was already submitted", "error")
        return redirect("/new_test_questions")
        
                



@app.route('/completed')
def test_completed():
    """Completed test page, return score"""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    test_id = session["questions"][0]["test_id"]
    score = get_test_score(test_id)
    return render_template("test/completed_test.html", score=score)

 


@app.route('/my_test')
def list_users_test():
    """List all test the user has taken"""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    all_user_test = UserTest.query.filter(UserTest.user_id == g.user.id).all()
    return render_template("test/list_test.html", all_user_test=all_user_test)

    


@app.route('/completed-test/<int:test_id>')
def show_users_completed_test_instance(test_id):
    """"List questions from a users test instance"""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    questions = UserTestQuestions.query.filter(UserTestQuestions.test_id == test_id).all()
    return render_template("test/show_old_test.html", questions=questions)