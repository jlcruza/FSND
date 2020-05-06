import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}@{}/{}".format('jorgecruz' , 'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
        
        self.new_valid_question = {
            'question':'Who is the best?',
            'answer':'You',
            'difficulty':1,
            'category':1
        }
        
        self.new_invalid_question = {
            'question':'Who is the best?',
            'answer':'You',
            'difficulty':1,
            'category':10
        }
        
        self.all_ids = []
        for id in range(30):
            self.all_ids.append(id)
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_categories(self):
        response = self.client().get('/categories')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))
    
    def test_get_paginated_questions(self):
        response = self.client().get('/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertEqual(data['current_category'], None)
        self.assertTrue(len(data['categories']))
    
    def test_404_requesting_beyond_valid_page(self):
        response = self.client().get('/questions?page=1000')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Error: The requested resource was not found")
    
    def test_delete_question(self):
        response = self.client().delete('/questions/11')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['deleted'])
    
    def test_422_delete_question_that_does_not_exist(self):
        response = self.client().delete('/questions/1000')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 422)
        self.assertEqual(data['message'], "Error: Cannot proccess request")

    def test_create_new_question(self):
        response = self.client().post('/questions', json=self.new_valid_question)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])

    def test_422_create_new_question(self):
        response = self.client().post('/questions', json=self.new_invalid_question)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 422)
        self.assertEqual(data['message'], "Error: Cannot proccess request")

    def test_search_question_with_result(self):
        response = self.client().post('/search', json={'searchTerm': 'What'})
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertEqual(data['current_category'], None)
    

    def test_search_question_without_result(self):
        response = self.client().post('/search', json={'searchTerm': 'abominable snowman'})
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['total_questions'], 0)
        self.assertEqual(data['current_category'], None)

    def test_get_question_by_category(self):
        response = self.client().get('/categories/1/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertEqual(data['current_category'], 'Science')
        

    def test_422_get_question_of_invalid_category(self):
        response = self.client().get('/categories/10/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 422)
        self.assertEqual(data['message'], "Error: Cannot proccess request")

    def test_get_quiz_question(self):
        response = self.client().post('/quizzes', json={'previous_questions': [], 'quiz_category':{'id':0}})
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['question']))

    def test_404_no_quiz_question_left(self):
        response = self.client().post('/quizzes', json={'previous_questions': self.all_ids, 'quiz_category':{'id':0}})
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Error: The requested resource was not found")

    def test_405_invalid_quiz_category(self):
        response = self.client().post('/quizzes', json={'previous_questions': [], 'quiz_category':'Science'})
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Error: Forbidden method used")
    
    



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()