import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category
from random import randrange

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
    """
    Return a list of question objects corresponding to the 
    specified page in the request argument.
    """
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


def create_app(test_config=None):
    app = Flask(__name__)
    setup_db(app)

    @app.after_request
    def after_request(response):
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add(
            'Access-Control-Allow-Methods', 'GET, POST, DELETE')
        return response

    @app.route('/categories')
    def get_categories():
        """
        Return a list of containing all the available categories and
        a success value that determines whether the request was
        successful.
        """
        categories_query = Category.query.order_by(Category.id).all()

        if len(categories_query) == 0:
            abort(404)

        categories = []

        for category in categories_query:
            categories.append(category.type)

        return jsonify({
            'success': True,
            'categories': categories,
        })

    @app.route('/questions')
    def retrieve_questions():
        """
        Return a list of question objects paginated in group of
        10 items per page, the total of questions, the list of
        all categories, and the success value.
        """
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)

        if len(current_questions) == 0:
            abort(404)

        categories_query = Category.query.all()
        categories = []

        for category in categories_query:
            categories.append(category.type)

        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(selection),
            'current_category': None,
            'categories': categories
        })

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        """
        Permanently delete the question with the provided
        id and return a success value indicating whether 
        the request was succesful.Return True if successfuly 
        deleted.
        """
        try:
            question = Question.query.filter(
                Question.id == question_id).one_or_none()

            if question is None:
                abort(404)

            question.delete()

            return jsonify({
                'success': True,
                'deleted': question_id,
            })

        except:
            abort(422)

    @app.route('/questions', methods=['POST'])
    def submit_question():
        """
        Add a new question with answer, difficulty and category
        provided in Json format. Return True if succesfully
        added.
        """
        body = request.get_json()

        question = body.get('question', None)
        answer = body.get('answer', None)
        difficulty = body.get('difficulty', None)
        category = body.get('category', None)

        try:

            new_question = Question(
                question=question,
                answer=answer,
                difficulty=difficulty,
                category=category
            )

            new_question.insert()

            return jsonify({
                'success': True
            })

        except:
            abort(422)

    @app.route('/search', methods=['POST'])
    def search_question():
        """
        Fetches all the questions that matches exactly or partially
        the search term provided. Returns the list of questions, the total
        of questions and the current category.
        """
        body = request.get_json()
        search = body.get('searchTerm', '')

        try:
            selection = Question.query.order_by(Question.id).filter(
                Question.question.ilike('%{}%'.format(search))).all()

            questions = []

            for question in selection:
                questions.append(question.format())

            return jsonify({
                'success': True,
                'questions': questions,
                'total_questions': len(questions),
                'current_category': None
            })

        except:
            abort(422)

    @app.route('/categories/<int:category_id>/questions')
    def retrieve_questions_by_category(category_id):
        """
        Retrieve a list of question objects that belong to
        the category id provided along with the total
        of questions and the current category. 
        """
        try:
            selection = Question.query.filter(
                Question.category == category_id).order_by(Question.id).all()

            if len(selection) == 0:
                abort(404)

            questions = []

            for question in selection:
                questions.append(question.format())

            return jsonify({
                'success': True,
                'questions': questions,
                'total_questions': len(questions),
                'current_category': Category.query.filter(Category.id == category_id).first().type,
            })

        except:
            abort(422)

    @app.route('/quizzes', methods=['POST'])
    def play_quizz():
        """
        Return a random question that belong to the category
        provided and that is not any of the previous
        questions.
        """
        body = request.get_json()

        previous_questions = body.get('previous_questions', [])
        quiz_category = body.get('quiz_category', None)

        try:
            quiz_category['id'] = int(quiz_category['id'])
        except:
            abort(405)

        selection = []
        ALL_CATEGORIES = 0

        if quiz_category['id'] == ALL_CATEGORIES:
            selection = Question.query.filter(~Question.id.in_(
                previous_questions)).order_by(Question.id).all()
        else:
            selection = Question.query.filter(~Question.id.in_(previous_questions)).filter(
                Question.category == quiz_category['id']).all()

        if len(selection) == 0:
            abort(404)

        STEP = 1
        index = randrange(0, len(selection), STEP)

        return jsonify({
            'success': True,
            'question': selection[index].format()
        })

    ''' 4xx - Client Error Handlers '''
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "Error: A bad request was made"
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Error: The requested resource was not found"
        }), 404

    @app.errorhandler(405)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "Error: Forbidden method used"
        }), 405

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Error: Cannot proccess request"
        }), 422

    ''' 5xx - Internal Server Error Handler '''
    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "Error: Internal Server Error ocurred"
        }), 500

    return app