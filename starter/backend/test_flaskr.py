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
        self.database_path = "postgres://{}/{}".format('@localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question = {
            'question': 'How many time does the heart beat per day',
            'answer': 'More than 100,000',
            'category': 'science',
            'difficulty': 5
        }

        self.questions_category = {
            'id' : 4
        }

        self.question_id = {
            'id': 5
        }
        
        self.quiz_category = {
            'previous_questions': [5, 9],
            'quiz_category': {
                'type': 'History',
                'id': 4
            }}

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_paginate_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(len(data['questions']))

    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))  

    def test_get_questions(self):
        res = self.client().get('/questions')
        data= json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])
    

    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    def test_delete_question(self):
        res = self.client().delete('/questions/12')
        data = json.loads(res.data)

        question = Question.query.get(12)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], False)
        self.assertTrue(data['deleted'], 12)
        self.assertTrue(data['message'])
        
       
    def test_404_delete_question(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
    
    def test_422_delete_question(self):
        res = self.client().get('/questions/100')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)




        
            
    def test_create_question(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)

        selection = Question.query.order_by('id').all()

        self.assertEqual(data['success'], False)

    def test_422_unprocessable(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(data['success'], False)
        self.assertEqual(res.status_code, 422)

    def test_search_question(self):
        res = self.client().post('/questions/search', json={'searchTerm': 'lake'})
        data = json.loads(res.data)

        self.assertEqual(data['success'], True)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])

    def test_422_unprocessable_request(self):
        res = self.client().post('/questions/search', json={'searchTerm': 'women'})
        data = json.loads(res.data)

        self.assertEqual(data['success'], False)
        self.assertEqual(res.status_code, 422)

    def test_question_by_category(self):
        res = self.client().get('/categories', json=self.questions_category)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_404_question_not_found(self):
        res = self.client().get('/categories/1000/questions', json=self.questions_category)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertTrue(data['message'])
        
        
    def test_quizzes(self):
        response = self.client().post('/quizzes', 
                json=self.quiz_category)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
    

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()