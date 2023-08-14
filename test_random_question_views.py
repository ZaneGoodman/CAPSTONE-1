"""Random Question Views tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, User, SavedQuestionsAndAnswers, UserTest, UserTestQuestions

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///Trivia-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class RandomQuestionViewTestCase(TestCase):
    """Test views for random questions."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        SavedQuestionsAndAnswers.query.delete()

        self.client = app.test_client()

        self.testuser = User.register(username="testuser",
                                    password="testuser",)
        self.testuser_id = 10
        self.testuser.id = self.testuser_id

        self.testuser2 = User.register(username="testuser2",
                                    password="testuser2",)
        self.testuser2_id = 20
        self.testuser2.id = self.testuser2_id
       
        db.session.commit()
       

    def tearDown(self):
        db.session.rollback()

    def setup_questions(self):
       SavedQuestionsAndAnswers(user_id=self.testuser_id,
       question="How many licks does it take to get the the center of a tootsy pop?", answer="12")

    def test_welcome_page(self):

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            resp = c.get('/')
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            
    def test_random_question(self):

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

        resp = c.get('/random_questions', follow_redirects=True)
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('<button id="answer-btn">Show Answer</button>', html)

    def test_save_question(self):

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

        resp = c.post('/save_question', data={"question":"how are you", "answer":"good"})
        
        
        
#     def welcome_page():
#     """Welcome page"""
#     return render_template('welcome.html')




# @app.route('/random_questions', methods=["GET", "POST"])
# def show_random_questions():
#     """Show user a random question and answer"""
#     if not g.user:
#         flash("Access unauthorized.", "danger")
#         return redirect("/")

#     trivia_response = api_call_random_question()
#     return render_template("random_question.html", trivia_response=trivia_response)



    
# @app.route('/save_question', methods=["POST"])
# def add_question_to_db():
#     """add saved question to the db"""
#     add_saved_question_to_db()
    # return redirect('/random_questions')
