import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    questions = [question.format() for question in selection]
    current_questions = questions[start:end]
    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers",
            "Content-Type,Authorization,true")
        response.headers.add(
            "Access-Control-Allow-Methods",
            "GET, PUT, POST, DELETE, OPTIONS")
        return response

    @app.route('/categories', methods=['GET'])
    def get_categories():
        try:
            categories = Category.query.all()
            formatted_category = {
                category.id: category.type for category in categories}
            if len(formatted_category) == 0:
                abort(404)
            return jsonify({
                'success': True,
                'status_code': 200,
                'categories': formatted_category
            })
        except BaseException:
            abort(405)

    @app.route('/questions', methods=['GET'])
    def get_questions():
        try:
            questions = Question.query.order_by(Question.id).all()
            categories = Category.query.order_by(Category.type).all()
            formatted_category = {
                category.id: category.type for category in categories}
            current_questions = paginate_questions(request, questions)
            if len(current_questions) == 0:
                abort(404)
            return jsonify({
                'success': True,
                'status_code': 200,
                'questions': current_questions,
                'categories': formatted_category,
                'total_questions': len(questions),
            })
        except BaseException:
            abort(422)

    @app.route('/questions', methods=['POST'])
    def post_question():
        body = request.get_json()
        question = body.get('question')
        answer = body.get('answer')
        category = body.get('category')
        difficulty = body.get('difficulty')
        if question == '' or answer == ''\
                or category == ''\
                or dificulty == '':
            abort(422)
        try:
            new_question = Question(question=question,
                                    answer=answer,
                                    category=category,
                                    difficulty=difficulty)
            new_question.insert()
            questions = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, questions)
            if len(current_questions) == 0:
                abort(404)
            return jsonify({
                "success": True,
                "status_code": 200,
            })
        except BaseException:
            abort(422)

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.filter(
                Question.id == question_id).one_or_none()
            if question is None:
                abort(404)
            else:
                question.delete()
                questions = question.query.order_by(Question.id).all()
                current_questions = paginate_questions(request, questions)
            return jsonify({
                'success': True,
                'status_code': 200,
            })
        except BaseException:
            abort(422)

    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def search_based_on_category(category_id):
        try:
            questions = Question.query.filter_by(category=category_id).all()
            formatted_questions = [question.format() for question in questions]
            if len(formatted_questions) == 0:
                abort(404)
            return jsonify({
                'success': True,
                'questions': formatted_questions,
                'total_questions': len(formatted_questions),
                'current_category': category_id
            })
        except BaseException:
            abort(422)

    @app.route('/search', methods=['POST'])
    def questions_search():
        body = request.get_json()
        phrase = '%{}%'.format(body.get('searchTerm'))
        questions = Question.query.filter(
            Question.question.ilike(phrase)).order_by(
            Question.id).all()
        current_questions = paginate_questions(request, questions)
        categories = Category.query.order_by(Category.id).all()
        formatted_category = {
            category.id: category.type for category in categories}
        if len(current_questions) == 0:
            abort(404)
        return jsonify({
            "success": True,
            'status_code': 200,
            "questions": current_questions,
            "total_questions": len(questions),
            "current_category": list(set([
                question['category'] for question in current_questions
            ])),
            "categories": formatted_category
        })

    @app.route('/play', methods=['POST'])
    def play():
        # Taking category and previous questions
        quiz_category = int(request.get_json()['quiz_category']['id'])
        previous_questions = request.get_json()['previous_questions']
        # Unique and radom Quesions
        if quiz_category not in [1, 2, 3, 4, 5, 6]:
            uniqued_questions = Question.query.all()
        else:
            uniqued_questions = Question.query.filter_by(
                category=quiz_category).filter(
                Question.id.notin_(previous_questions)).all()
        return jsonify({
            'success': True,
            'category': quiz_category,
            'question': random.choice([q.format() for q in uniqued_questions])
        })

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "Bad request"
        }), 400

    @app.errorhandler(405)
    def method_not_allow(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "Method not allow"
        }), 405
    return app
