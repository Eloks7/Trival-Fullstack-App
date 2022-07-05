DOCUMENTATION

GETTING STARTED

Base URL: The API does not have a base URL as it hasn't been hosted. It can only be run locally at the default address https://localhost:5000 (https//127.0.0.1:5000)

Authentication: No authentication required.

ERROR HANDLING

Errors are returned as JSON objects in this format:
{
    "success": False,
    "error": 422,
    "message": "unprocessable"
}
Errors to expect:
400 - Bad Request
404 - Resource not found
405 - method not allowed
422 - unprocessable
500 - internal server error

ENDPOINTS

GET "/categories"

- General:
  - Fetches a dictionary of categories in which the keys are the ids and the value is the corresponding string of the category
  - Request Arguments: None
  - Returns: An object with a single key, categories, that contains an object of id: category_string key:value pairs.
  
- Sample: curl http://localhost:5000/categories
- Expected Response:
   {
    'success': True
    'categories': { '1' : "Science",
    '2' : "Art",
    '3' : "Geography",
    '4' : "History",
    '5' : "Entertainment",
    '6' : "Sports" }
   }
   
GET "/questions"

- General:
  - Fetches a paginated set of questions, a total number of questions, all categories and current category string
  - Request Arguments: page - integer
  - Returns: An object with 10 paginated questions, total questions, object including all categories, and current category         string
  
- Sample: curl http://localhost:5000/questions?page=1
- Expected Response:
{
    'questions': [
        {
         "answer": "Mona Lisa", 
         "category": 2, 
         "difficulty": 3, 
         "id": 17, 
         "question": "La Giaconda is better known as what?"
        }, 
        {
         "answer": "One", 
         "category": 2, 
         "difficulty": 4, 
         "id": 18, 
         "question": "How many paintings did Van Gogh sell in his lifetime?"
        }, 
        {
         "answer": "Jackson Pollock",
         "category": 2,
         "difficulty": 2,
         "id": 19,
         "question": "Which American artist was a pioneer of Abstract Expressionism, and a leading exponent of action painting?"
        },
        
        .
        .
        .
        
        {
         "answer": "Lionel Messi",
         "category": 6,
         "difficulty": 2,
         "id": 26,
         "question": "Who is the greatest player of all time?"
        }
    ],
    'totalQuestions': 20,
    'categories': { '1' : "Science",
    '2' : "Art",
    '3' : "Geography",
    '4' : "History",
    '5' : "Entertainment",
    '6' : "Sports" },
}

GET "/categories/{category_id}/questions"

- General:
  - Fetches questions for a cateogry specified by id request argument
  - Request Arguments: id - integer
  - Returns: An object with questions for the specified category, total questions, and current category string
  
- Sample: curl http://localhost:5000/categories/2/questions
- Expected Response:
{
  "current_category": "Art", 
  "questions": [
    {
      "answer": "Escher", 
      "category": 2, 
      "difficulty": 1, 
      "id": 16, 
      "question": "Which Dutch graphic artist\u2013initials M C was a creator of optical illusions?"
    }, 
    {
      "answer": "Mona Lisa", 
      "category": 2, 
      "difficulty": 3, 
      "id": 17, 
      "question": "La Giaconda is better known as what?"
    }
  ], 
  "success": True, 
  "total_questions": 2
}

DELETE "/questions/{question_id}"

- General:
  - Deletes a specified question using the id of the question
  - Request Arguments: id - integer
  
- Sample: curl -X DELETE 'http://localhost:5000/questions/5'
- Expected Response:
{
  "success": True,
  "deleted": 5
}

POST "/quizzes"

- General:
  - Sends a post request in order to get the next question
  - Request Body:
    {
        'previous_questions': [1, 4, 20, 15]
        'quiz_category': current_category
    }
- Sample: curl -X POST 'http://localhost:5000/quizzes'
- Expected Response: 
{
 "question": {
  "answer": "Escher", 
  "category": 2, 
  "difficulty": 1, 
  "id": 16, 
  "question": "Which Dutch graphic artist\u2013initials M C was a creator of optical illusions?"
 }
 "success": True
}

POST "/question"

- General:
  - Sends a post request in order to add a new question
  - Request Body:
  {
    'question':  'Heres a new question string',
    'answer':  'Heres a new answer string',
    'difficulty': 1,
    'category': 3,
  }
  
- Sample: curl -X POST -H "Content-Type: application/json" -d '{"answer": "Water", "question": "What is H2O?", "difficulty": 5, "category": 1}' http://localhost:5000/questions

- Example Response: 
{
 "success": True
}

POST "/questions/search"
- General:
  - Sends a post request in order to search for a specific question by search term
  - Request Body:
  {
    'searchTerm': 'this is the term the user is looking for'
  }
- Sample: curl -X POST -H "Content-Type: application/json" -d '{"searchTerm": "title"}' http://localhost:5000/questions/search
- Expected Response:
     {
        "questions": [
          {
            "answer": "Edward Scissorhands",
            "category": 5,
            "difficulty": 3,
            "id": 6,
            "question": "What was the title of the 1990 fantasy directed by Tim Burton about a young man with multi-bladed appendages?"
          }
        ],
        "success": true,
        "total_questions": 1
      }