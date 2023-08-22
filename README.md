# Trivia Nation
## API : https://jservice.io
## Application Link : https://trivia-nation-capstone.onrender.com


### About:
Trivia Nation offers it's users the ability to test their knowledge using Trivia questions. They have the option to learn from randomly populated questions and answers as well as,  save any questions they like and create a personal test using
these questions. 

### Features:

1. Random Questions
   - Populate random questions to the user. The user has the option to show the answer, save the question, or skip to the next question.
     - This allows the user to cover a wide range of topics and gather as much knowledge as they would like. The ability to save a question they like gives a user the oppurtunity to come back to the question later to obtain a good grasp on the topic.
       
2. Testing
   - Populate the questions the user has saved, allowing them to pick which questions they would like to test their knowledge on. The app will build them a personal test, showing one question at a time with multiple choice answers. The user will then be shown their score at the end of the test.
  
3. Previous Test Cases
   - Once the user has completed a test they have curated that test will be saved to their profile for future critiquing. Each test instance is listed with the score for each.
     - The user can click on each test instace and look at what the questions for that test are, what the answer is, and if they answered correctly or incorrectly. This opens the door for further study and increase in knowledge, giving the user the option to test on those questions again until they answer correctly. As well as, based on past test, see how and where they've improved.
  

### Basic User Flow:
- The user is met with the base welcome page where they must Sign Up/Log In, Afterwards the following options will appear: 
   - Start! - Sends user to random questioning.
     
   - My Test - Shows a list of the test instances the user has completed.
       - Click on a test instance to see all of that tests questions, answers, and status of correct/incorrect.
       - Deleting the test instance will take the user back to their list of completed test instances.
         
   - New Test - Sends user to their own list of questions to create a new test with.
       - Once the user has picked the questions they would like, clicking "Start Test!" will take them to a question by question multiple choice test.
       - Once completed the user can see their score and go home or go back to the above "My Test" feature.
         
   - Across each page there will always be a navbar giving easy access to : Going home, Logging out, and Logging in.
 
### Api Information
The jservice api gives access to hundreds of trivia questions and answers. One issue that arrises with this api is that the json response containing the question information sometimes comes back empty. This initially caused the application to break. With some simple error handling that no longer happens. However,
the app will continue to request question information from the api until it gets it. Because of this the application will pause and run slow for just a few moments before coming back to life. Though unavoidable with this api it does not greatly impact the user experience. 


### Technology used: 
This app was built with Python/Flask, PostgreSQL, SQLAlchemy, Render, Jinja, RESTful APIs, JavaScript, HTML, CSS, and WTForms. 



Thank you for taking the time to look at my application!
