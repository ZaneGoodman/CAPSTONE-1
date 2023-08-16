"""Random Question Views tests."""



import os
from unittest import TestCase
from flask import session
from models import db, User, SavedQuestionsAndAnswers

# setup test database

os.environ['DATABASE_URL'] = "postgresql:///Trivia-test"

# import app 

from app import app, CURR_USER_KEY


db.create_all()


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
        db.session.add_all([self.testuser, self.testuser2])
        db.session.commit()
       

    def tearDown(self):
        db.session.rollback()

    def test_welcome_page(self):
        """While user is logged in, does welcome page work and show proper selections"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            resp = c.get('/')
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn("<button>Start!</button>", html)

    def test_welcome_page_without_auth(self):
        """When user is not logged in, does welcome page work and hide correct selections"""
        with self.client as c:
          
            resp = c.get('/')
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertNotIn("<button>Start!</button>", html)
            

    def test_random_question(self):
        """Test if a logged in user can use random question functionallity"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

        resp = c.get('/random_questions', follow_redirects=True)
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('<button id="answer-btn">Show Answer</button>', html)


    def test_random_question_without_auth(self):
        """Test that a unauth user cannot see random questions"""
        with self.client as c:
          
            resp = c.get('/random_questions', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertNotIn('<button id="answer-btn">Show Answer</button>', html)


    def test_save_question(self):
        """Test if a user can save a question """
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id
        
        resp = c.post('/save_question', json={"question":"how are you", "answer":"good"})
        all_questions = SavedQuestionsAndAnswers.query.filter(SavedQuestionsAndAnswers.user_id == sess[CURR_USER_KEY]).all()

        self.assertEqual(resp.status_code, 302)
        self.assertEqual(len(all_questions), 1)
        self.assertEqual(all_questions[0].question, "how are you" )
        
        
 