import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_books(request, selection):
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

    '''
    @TODO: Set up CORS. Allow '*' for origins.
    Delete the sample route after completing the TODOs
    '''
    CORS(app)
    '''
    @TODO: Use the after_request decorator to set Access-Control-Allow
    '''
    @app.after_request
    def after_request(response):
        response.headers.add(
            'Access-Control-Allow-Headers',
            'Content-Type, Authorization'
        )
        response.headers.add(
            'Access-Control-Allow-Methods',
            'GET,POST,PUT,PATCH,DELETE,OPTIONS'
        )
        return response
    '''
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    '''
    # a get request that will return all available categories
    @app.route('/categories')
    def get_categories():
        # queries all available categories
        categories = Category.query.all()
        formate_categories = {}
        # change the formate of categories to be dictionary of dictionaries
        # to be compatibale with frontend
        for category in categories:
            formate_categories.update({category.id: category.type})
        return jsonify({'success': True, 'categories': formate_categories})
    '''
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of
    the screen for three pages.
    Clicking on the page numbers should update the questions.
    '''
    # get request that will return all available questions
    @app.route('/questions')
    def get_question():
        # queries all questions
        selection = Question.query.order_by(Question.id).all()
        # reformate the question so that it will be only 10 questions per page
        current_questions = paginate_books(request, selection)
        # in case of no question, an error will be returned
        if len(current_questions) == 0:
            abort(404)
        categories = Category.query.all()
        formate_categories = {}
        # change the formate of categories to be dictionary
        # of dictionaries to be compatibale with frontend
        for category in categories:
            formate_categories.update({category.id: category.type})
        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(selection),
            'categories': formate_categories,
            'current_category': None
        })
    '''
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question,
    the question will be removed.
    This removal will persist in the database and when you refresh the page.
    '''
    # a delete request that will delete one questiona a time
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            # Select the question
            QID = question_id
            question = Question.query.filter(Question.id == QID).one_or_none()
            # in case the question does not exist, return a error
            if question is None:
                abort(400)
            # delete the question
            question.delete()
            # queries all questions
            selection = Question.query.order_by(Question.id).all()
            # reformate the question so that
            # it will be only 10 questions per page
            current_questions = paginate_books(request, selection)
            return jsonify({
                'success': True,
                'deleted_question': question_id,
                'questions': current_questions,
                'total_questions': len(selection)
                })
        except Exception:
            abort(422)
    '''
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at
    the end of the last page
    of the questions list in the "List" tab.
    '''

    # Create request that handel a creation of one question a time
    @app.route('/questions', methods=['POST'])
    def create_question():
        # Parse data as JSON
        body = request.get_json()
        # add each data in a proper variable
        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        new_category = body.get('category', None)
        new_difficulty = body.get('difficulty', None)
        try:
            # Create the question
            question = Question(
                                question=new_question,
                                answer=new_answer,
                                category=new_category,
                                difficulty=new_difficulty
                                )
            # Call the insert function to add and commit
            question.insert()
            # queries all questions
            selection = Question.query.order_by(Question.id).all()
            # reformate the question so that
            # it will be only 10 questions per page
            current_questions = paginate_books(request, selection)
            return jsonify({
                'success': True,
                'created_question': question.id,
                'questions': current_questions,
                'total_questions': len(selection)
            })
        except Exception:
            abort(422)
    '''
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    '''
    # search request that return a list of
    # questions based on the given search term
    @app.route('/questions/search', methods=['POST'])
    def search_question():
        # Parse data as JSON
        body = request.get_json()
        # assign the search term to a variable
        searchTerm = body.get('searchTerm', None)
        try:
            # Select the questions that matches the search term
            selection = Question.query.filter(
                                Question.question.ilike('%'+searchTerm+'%')
                                ).all()
            # reformate the question so that
            # it will be only 10 questions per page
            current_questions = paginate_books(request, selection)
            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': len(selection),
                'currentCategory': None
            })
        except Exception:
            abort(422)
    '''
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    '''
    # a get request that return a list of
    # questions based on a selected category
    @app.route('/categories/<int:id>/questions')
    def get_question_by_category(id):
        # queries the questions based on the category
        selection = Question.query.filter(
                            Question.category == id
                            ).order_by(Question.id).all()
        # reformate the question so that it will be only 10 questions per page
        current_questions = paginate_books(request, selection)
        # in case of no question, an error will be returned
        if len(current_questions) == 0:
            abort(404)
        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(selection),
            'current_category': None
        })
    '''
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    '''
    #  an end point that serve a quizz request where return
    # questons to start the quizz. if the quizz has reach
    # the limit of 5 questions or the category has less than
    # than 5 question, it will return a flag that end the quizz
    @app.route('/quizzes', methods=['POST'])
    def get_quizz():
        # Parse data as JSON
        body = request.get_json()
        # assign data to a variables
        p_questions = body.get('previous_questions', None)
        quiz_category = body.get('quiz_category', None)
        try:
            # an condtion in case of category was other than ALL
            if quiz_category['id'] != 0:
                # Queries the question of the selected category
                questions = Question.query.filter(
                                Question.category == quiz_category['id']
                                ).order_by(Question.id).all()
            # in case category selection was ALL
            else:
                # queries all questions
                questions = Question.query.order_by(Question.id).all()
            # in case of no question, an error will be returned
            if len(questions) == 0:
                abort(404)
            # if the quizz reached 5 questions
            # or there is less than 5 question
            # in the selected category and it was played, Quizz to be ended
            if len(p_questions) == 5 or len(p_questions) == len(questions):
                random_question = None
            else:
                # check if it is the first round of the quizz or
                # there was already previous rounds played
                if len(p_questions) > 0:
                    for previous in p_questions:
                        for question in questions:
                            # a condtion check if the question was
                            # already played and remove it
                            # from the list of available questions
                            if question.id == previous:
                                questions.remove(question)
                                break
                # Select a question randomlly
                random_question = random.choice(questions).format()
            return jsonify({
                'success': True,
                'question': random_question
            })
        except Exception:
            abort(422)
    '''
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    '''
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "Bad request"
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(405)
    def not_allowed(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "method not allowed"
        }), 405

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    return app
