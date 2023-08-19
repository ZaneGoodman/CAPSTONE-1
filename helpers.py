from flask import Flask, request, session, g, flash, redirect
from models import db,  SavedQuestionsAndAnswers, UserTestQuestions, UserTest

import requests
from json.decoder import JSONDecodeError


API_BASE_URL = "https://jservice.io"
CURR_USER_KEY = "curr_user"



def login_user(user):
    """Log in the user"""

    session[CURR_USER_KEY] = user.id



def logout_user():
    """Logout user"""
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

def api_call_random_question():
    """Get random trivia question/answer object from api"""
    try:
        random_url = f"{API_BASE_URL}/api/random"
        resp = requests.get(random_url)
        json_resp = resp.json()
        
        question = delete_html_elements_from_str(str(json_resp[0]['question']))
        answer = delete_html_elements_from_str(str(json_resp[0]['answer']))

        trivia_response = {
            "question" : question,
            "answer" : answer
        }
        return trivia_response
    except JSONDecodeError:
        api_call_random_question()

def get_three_fake_answers():
    """Get three answers for multiple choice testing from api"""
    random_url = f"{API_BASE_URL}/api/random"
    resp = requests.get(random_url, params={"count": 3})
    json_resp = resp.json()

    fake_answers = []
    try:
        for i in json_resp:
            a = delete_html_elements_from_str(str(i['answer']))
            fake_answers.append(a)

        return fake_answers
    
    except JSONDecodeError:
        get_three_fake_answers()

def delete_html_elements_from_str(string):
    """Delete the random html elements attached to the data from the api"""
    replacements = [("<i>", ""), ("</i>", "")]
    for char, replacement in replacements:
        if char in string:
            string = string.replace(char, replacement)
        
    return string

def add_saved_question_to_db():
    """When user saves a question, add it to the db"""
    question = delete_html_elements_from_str(str(request.json["question"]))
    
    answer = delete_html_elements_from_str(str(request.json["answer"]))
    new_saved_question = SavedQuestionsAndAnswers(user_id=g.user.id, question=question, answer=answer)
    db.session.add(new_saved_question)
    db.session.commit()

    return

def create_new_test_with_user_questions():
    """Get picked questions from user and add them to saved question, make a new test. Commit all to db"""
    questions = request.form.getlist("question")
   
    picked_questions = [SavedQuestionsAndAnswers.query.filter(SavedQuestionsAndAnswers.question == question).first() for question in questions]

    if len(picked_questions) > 0:
        new_test = UserTest(user_id=g.user.id)
        db.session.add(new_test)
        db.session.commit()
        for question in picked_questions:
            test_question = UserTestQuestions(user_id=g.user.id, test_id=new_test.test_id, question_answer_id=question.id)
            db.session.add(test_question)
            db.session.commit()
        return new_test.test_id
    else:
        return None
        
       
        

def convert_data_to_list(test_questions):
    """Convert passed in data to array of objects"""
    converted_data = []
    for question in test_questions:
        q = {"question": question[0], "correct": question[1], "test_id": question[2]}
        converted_data.append(q)
    
    return converted_data

def check_answer_and_return_index(question_id):
    """Check answer, get question index from session and return"""
    answer = request.form["answer"]
    
    question = SavedQuestionsAndAnswers.query.get(question_id)
    for curr_question in session["questions"]:
        index = session["questions"].index(curr_question)
        test_id = curr_question["test_id"]
        test_question = UserTestQuestions.query.filter(UserTestQuestions.question_answer_id == question_id, UserTestQuestions.test_id == test_id).first()
        
        if curr_question['correct'] == None:
            
            if curr_question["question"] == question.question:
                check_if_true_or_false(answer, question, curr_question, test_question)
            return index


def check_if_true_or_false(answer ,correct_question, current_question, test_question):
    """Check if users answer is correct, commit to db"""
    
    if answer == correct_question.answer:
        current_question["correct"] = True
        session.modified = True
        test_question.correct = True
        db.session.add(test_question)
        db.session.commit()
                    
    if answer != correct_question.answer:
        current_question["correct"] = False
        session.modified = True
        test_question.correct = False
        db.session.commit()

def get_test_score(test_id):
    """Get all answers from test, populate score % and commit to db"""
    true_false_answers = UserTestQuestions.query.filter(UserTestQuestions.test_id == test_id).all()
    print(true_false_answers)
    answers = [answer.correct for answer in true_false_answers]
    print(answers)
    test = UserTest.query.get(test_id)

    score = ((len([ a for a in answers if a == 'true' or a == 't' or a == True]) / len(answers))) * 100
    print(score)
    test.score = score
    db.session.commit()
    return score

def get_questions_for_test(test_id):
    """Get question data for test matching test_id"""
    db_questions = (db.session.query(SavedQuestionsAndAnswers.question, UserTestQuestions.correct, UserTestQuestions.test_id)
    .filter(UserTestQuestions.test_id == test_id)
    .join(UserTestQuestions).all())
    test_questions = convert_data_to_list(db_questions)

    return test_questions
