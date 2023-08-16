"""Testing Views tests."""



import os
from unittest import TestCase
from flask import session
from models import db, SavedQuestionsAndAnswers, UserTest, UserTestQuestions, User

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
        UserTest.query.delete()
        UserTestQuestions.query.delete()

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

    def setup_questions(self):
       q1 = SavedQuestionsAndAnswers(id=1, user_id=self.testuser_id, question="How many licks does it take to get the the center of a tootsy pop?", answer="12")
       q2 = SavedQuestionsAndAnswers(id=2, user_id=self.testuser_id, question="How tall is the empire state building?", answer="7ft")
       db.session.add_all([q1,q2])
       db.session.commit()

    def setup_test(self):
        q1 = SavedQuestionsAndAnswers(id=2, user_id=self.testuser_id, question="How tall is the empire state building?", answer="7ft")
        q2 = SavedQuestionsAndAnswers(id=3, user_id=self.testuser_id, question="2+2", answer="5")
        db.session.add_all([q1,q2])
        db.session.commit()
        test1 = UserTest(test_id=15, user_id=self.testuser_id)
        db.session.add(test1)
        db.session.commit()
        test_question1 = UserTestQuestions(id=25, user_id=self.testuser_id, test_id=test1.test_id, question_answer_id=q1.id)
        test_question2 = UserTestQuestions(id=30, user_id=self.testuser_id, test_id=test1.test_id, question_answer_id=q2.id)
        db.session.add_all([test_question1, test_question2])
        db.session.commit()

    def setup_completed_test(self):
        q1 = SavedQuestionsAndAnswers(id=2, user_id=self.testuser_id, question="How tall is the empire state building?", answer="7ft")
        q2 = SavedQuestionsAndAnswers(id=3, user_id=self.testuser_id, question="2+2", answer="5")
        db.session.add_all([q1,q2])
        db.session.commit()
        test1 = UserTest(test_id=15, user_id=self.testuser_id)
        db.session.add(test1)
        db.session.commit()
        test_question1 = UserTestQuestions(id=25, user_id=self.testuser_id, test_id=test1.test_id, question_answer_id=q1.id, correct=True)
        test_question2 = UserTestQuestions(id=30, user_id=self.testuser_id, test_id=test1.test_id, question_answer_id=q2.id, correct=False)
        db.session.add_all([test_question1, test_question2])
        db.session.commit()
    

    def test_list_pickable_test_questions(self):
        """List saved questions from user to be picked for a test"""
        self.setup_questions()
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id
            
            resp = c.get("/new_test_questions")
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<label for="question">How many licks does it take to get the the center of a tootsy pop?</label>', html)
              
    def test_create_new_test_with_picked_questions(self):
        """Test if a new test instance is created with the questions the user picked"""
        self.setup_questions()
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

        resp = c.post("/create_new_test", data={"question": ["How many licks does it take to get the the center of a tootsy pop?", "How tall is the empire state building?"]})
        

        test_questions = UserTestQuestions.query.filter(UserTestQuestions.user_id == sess[CURR_USER_KEY]).all()
        q1 =  UserTestQuestions.query.filter(UserTestQuestions.question_answer_id == 1).first()
        test_instance = UserTest.query.filter(UserTest.user_id == sess[CURR_USER_KEY]).first()

        self.assertEqual(resp.status_code, 302)
        self.assertIn(q1, test_questions)
        self.assertEqual(q1.test_id, test_instance.test_id)


    def test_start_test_and_add_questions_to_session(self):
        """On start of test, confirm test question info is added to session, and that that info is correct"""
        self.setup_test()
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            resp = c.get("/start_test/15")
                
            self.assertEqual(resp.status_code, 302)
            self.assertEqual(len(session["questions"]), 2)
            self.assertEqual(session["questions"][0]["question"], "How tall is the empire state building?")
            self.assertEqual(session["questions"][0]["test_id"], 15)
            self.assertEqual(session["questions"][0]["correct"], None)
            
           
    def test_test_question_count_greater_than_session_index(self):
        """Test error handling that will complete the test if all questions are answered using session index"""
        self.setup_test()
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

                
            c.get("/start_test/15")
            
            resp = c.get('/test/2', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<form action="/"><button>Go Home</button></form>', html)

    def test_test_shows_next_question(self):
        """Test if the next question in a test instance will populate once the previous question has been answered"""
        self.setup_test()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

                
            c.get("/start_test/15")
            
            resp = c.get('/test/1', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1>2+2</h1>', html)

    def test_check_true_test_answer(self):
        """Check if the db and session update to "true" when user answers test question corrrectly"""
        self.setup_test()
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

                
            c.get("/start_test/15")
            
            resp = c.post('/test/answers/2',  data={"answer": "7ft"} )
            test_question = UserTestQuestions.query.filter(UserTestQuestions.question_answer_id == 2, UserTestQuestions.test_id == 15).first()
           
            self.assertEqual(resp.status_code, 302)
            self.assertEqual(test_question.correct, True)
            self.assertEqual(session["questions"][0]["correct"], True)

    
    def test_check_true_test_answer(self):
        """Check if the db and session update to "False" when user answers test question incorrectly"""
        self.setup_test()
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

                
            c.get("/start_test/15")
            
            resp = c.post('/test/answers/2',  data={"answer": "10ft"} )
            test_question = UserTestQuestions.query.filter(UserTestQuestions.question_answer_id == 2, UserTestQuestions.test_id == 15).first()
           
            self.assertEqual(resp.status_code, 302)
            self.assertEqual(test_question.correct, False)
            self.assertEqual(session["questions"][0]["correct"], False)



    def test_check_scoring(self):
        """Check that the scoring function properly populates the correct score to the user"""
        self.setup_completed_test()
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id
            c.get("/start_test/15")
            
            resp = c.get("/completed")
            html = resp.get_data(as_text=True)
      

        
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(UserTest.query.get(15).score, 50.0)
            self.assertIn("<h1>You scored 50.0!</h1>", html)
    

    def test_list_user_test(self):
        """Check that the users completed test are listed at this route"""
        self.setup_completed_test()
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id
            c.get("/start_test/15")
            c.get("/completed")
            resp = c.get("/my_test")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn( 'score = 50', html)
            
    def test_list_questions_from_completed_test(self):
        """Check that the user can see the questions and if they were correct/incorrect for their completed test """
        self.setup_completed_test()
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id
            c.get("/start_test/15")
            c.get("/completed")
            resp = c.get("/completed_test/15")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn( '<p>How tall is the empire state building?</p>', html)
            self.assertIn( '<p>correct</p>', html)
            self.assertIn( '<p>2+2</p>', html)
            self.assertIn( '<p>incorrect</p>', html)

    

