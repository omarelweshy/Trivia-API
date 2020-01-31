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
        self.database_path = "postgresql://{}:{}@{}/{}".format(
            'omar',
            '010',
            'localhost:5432',
            self.database_name
        )
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_paginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertEqual(len(data['questions']), 10)
        self.assertTrue(len(data['categories']))

    def test_get_questions_422(self):
        res = self.client().get('/questions?page=100')
        data = json.loads(res.data)
        self.assertFalse(data['success'])
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['message'], 'unprocessable')

    def test_post_question_200(self):
        question = {
            'question': 'Whats your hobbies ?',
            'answer': 'Any Thing',
            'category': 5,
            'difficulty': '3'
        }
        res = self.client().post('/questions', json=question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])

    def test_post_question_422(self):
        new_question = {
            'question': '',
            'answer': '',
            'category': '',
            'difficulty': ''
        }
        res = self.client().post('/questions', json=new_question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'unprocessable')

    def test_delete_question(self):
        res = self.client().delete('/questions/14')
        data = json.loads(res.data)
        self.assertTrue(data['success'])
        self.assertEqual(res.status_code, 200)

    def test_delete_quesion_422(self):
        res = self.client().delete('/questions/1')
        data = json.loads(res.data)
        self.assertFalse(data['success'])
        self.assertEqual(res.status_code, 422)

    def test_get_categories_200(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)

    def test_get_quesions_based_on_category(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])

    def test_get_quesions_based_on_category_422(self):
        res = self.client().get('/categories/100/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'unprocessable')

    def test_play(self):
        body = {
            'quiz_category': {
                'id': 1
            },
            'previous_questions': []
        }
        res = self.client().post('/play', json=body)
        data = json.loads(res.data)
        self.assertEqual((data['category']), 1, 'Category not match the quiz')

    def test_search_question(self):
        res = self.client().post('/search', json={'searchTerm': "what"})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])

    def test_search_question_404(self):
        res = self.client().post('/search', json={'searchTerm': +
                                                  "any_worng_thing"})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
