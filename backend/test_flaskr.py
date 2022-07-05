import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question = {
            "question": "Name of Eloka's Country",
            "answer": "Nigeria",
            "difficulty": "1",
            "category": "5"
        }
        
        self.wrong_question_format = {
            "question": "Name of Eloka's Country",
            "answer": "Nigeria",
            "difficulty": "1",
            "category": "100"
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    #Test Category Listing
    def test_listing_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        
    def test_error_listing_category(self):
        res = self.client().post('/categories')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 405)
        self.assertEqual(data['message'], 'method not allowed')
        
    #Test Questions listing
    def test_listing_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['categories'])
    
    def test_error_listing_questions(self):
        res = self.client().get('/questions?page=500')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 422)
        self.assertEqual(data['message'], 'unprocessable')

    #Test questions per category
    def test_questions_per_category_success(self):
        res = self.client().get('/categories/3/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])

    def test_questions_per_category_failure(self):
        res = self.client().get('/categories/10/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 400)
        self.assertEqual(data['message'], 'bad request')
        
        
    #Test question deletion   
    def test_successful_delete(self):
        res = self.client().delete('/questions/4')
        data = json.loads(res.data)
        question  = Question.query.filter(Question.id == 4).one_or_none()
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 4)
        self.assertEqual(question, None)
        
    def test_delete_failed(self):
        res = self.client().delete('/questions/370')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')
        
    #Test question creation
    def test_successful_question_creation(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        
        
    def test_400_question_creation_not_allowed(self):
        res = self.client().post('/questions', json=self.wrong_question_format)
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")
        
    #Test search operation
    def test_search_items_found(self):
        res = self.client().post('/questions', json={"searchTerm": "title"})
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])
        self.assertTrue(data["questions"])
         
    #Test Quiz
    def test_quiz_success(self):
        res = self.client().post('/quizzes', json={"quiz_category": {"id": 1},
                                                 "previous_questions": [2, 4]})
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["question"])
        
    def test_error_no_such_category_for_quiz(self):
        res = self.client().post('/quizzes', json={"quiz_category": 20,
                                                 "previous_questions": []})
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 500)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "internal server error")
        
    def test_quiz_not_working(self):
        res = self.client().patch('/quizzes', json={"quiz_category": 3,
                                                 "previous_questions": [1, 5]})
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "method not allowed")


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()