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
    
    return redirect(f'/start_test/{new_test.test_id}')


@app.route('/start_test/<int:test_id>')
def start_test(test_id):
    test_questions = (db.session.query(SavedQuestionsAndAnswers.question, SavedQuestionsAndAnswers.answer, UserTestQuestions.correct)
     .filter(UserTestQuestions.test_id == test_id)
     .join(UserTestQuestions).all())
    # test question format : 
    # [('I\'ve been referred to as "America\'s Home Improvement Guru" & "America\'s Handyman"','Bob Vila', None), etc, etc]

    session["questions"] = test_questions
    return redirect(f"/test/0")


@app.route('/test/<int:question_index>')
def populate_each_test_question(question_index):
    questions = session["questions"]
    if questions[question_index][2] == None:
        next_question = SavedQuestionsAndAnswers.query.filter(SavedQuestionsAndAnswers.question == questions[question_index][0]).first()
        return render_template("/test/test.html", question=next_question)
    
@app.route('/test/answers/<int:question_id>')
def check_test_answer(question_id):
    answer = request.form["answer"]
    question = SavedQuestionsAndAnswers.query.get(question_id)
    for curr_question in session["question"]:
        if curr_question[0] == question.question:
            if answer == question.answer:
                test_question = UserTestQuestions.query.filter(UserTestQuestions.question_answer_id == question_id).first()
                test_question.correct = True

# As of now I am checking if the question from the question id passed from the form mathces that question in session, then checking if the answer is correct and then changing the test question "correct" table name to True. Becuase of this I will have to empty the session and re-initialize the session to update the questions "correct" attribute. I cannot mannually change that in the session becuase the session is an sqlachemy object and it wont allow me. This is a lot. I Have it this way to keep querying to a minimum. The question at hand is would it be better to try something different by using my table relationships(if that would work), which causes a hell of a lot of querying. Or keep it this way and re-initialize the session every time a question is answered. Or figure out a way to keep the session seperate from being an sqlalchemy object so I can simply check that the answer is correct and then update the database. I dont know. must think.

    return redirect('/test/<int:question_idex>')
     
    
# q = (db.session.query(SavedQuestionsAndAnswers.question, SavedQuestionsAndAnswers.answer).join(UserTestQuestions).all())


# def phone_dir_join():
#     """Show employees with a join."""

#     emps = (db.session.query(Employee.name,
#                              Department.dept_name,
#                              Department.phone)
#             .join(Department).all())

#     for name, dept, phone in emps:  # [(n, d, p), (n, d, p)]
#         print(name, dept, phone)


# def phone_dir_join_class():
#     """Show employees with a join.

#     This second version doesn't just get a list of data tuples,
#     but a list of tuples of classes.
#     """

#     emps = (db.session.query(Employee, Department)
#             .join(Department).all())

#     for emp, dept in emps:  # [(<E>, <D>), (<E>, <D>)]
#         print(emp.name, dept.dept_name, dept.phone)