"""Random Question Views tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User, Follows, Likes

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

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)
        self.testuser_id = 10
        self.testuser.id = self.testuser_id

        self.testuser2 = User.signup(username="testuser2",
                                    email="test2@test.com",
                                    password="testuser2",
                                    image_url=None)
        self.testuser2_id = 20
        self.testuser2.id = self.testuser2_id
       
        db.session.commit()
       

    def tearDown(self):
        db.session.rollback()

    def setup_questions(self):
       SavedQuestionsAndAnswers(user_id=self.testuser_id,
       question="How many licks does it take to get the the center of a tootsy pop?", answer="12")