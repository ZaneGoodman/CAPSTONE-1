from flask import Flask, render_template, request
import requests

API_BASE_URL = "https://jservice.io"

app = Flask(__name__)



@app.route('/')
def test_api_routes():
    random_url = f"{API_BASE_URL}/api/random"
    

    random_resp = requests.get(random_url)


    rr = random_resp.json()
    question = rr[0]['question']
    answer = rr[0]['answer']
   

    return render_template('index.html', question=question, answer=answer)
