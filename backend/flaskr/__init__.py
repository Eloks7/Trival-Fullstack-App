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
    
    formatted_questions = [question.format() for question in selection]
    current_questions = formatted_questions[start:end]
    
    return current_questions

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app)

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization,true")
        response.headers.add("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS")
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route("/categories", methods=["GET"])
    def get_all_categories():
        try:
            categories = Category.query.order_by(Category.type).all()
        
        #if len(categories) == 0:
        #    abort(404)
            
            return jsonify({
                "success": True,
                "categories": {
                    category.id: category.type for category in categories
                }
            })
        except:
            abort(422)


    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route("/questions", methods=["GET"])
    def get_all_questions():
        selection = Question.query.order_by(Question.id).all()
        categories = Category.query.order_by(Category.type).all()
        current_questions = paginate_questions(request, selection)
        formatted_questions = [question.format() for question in selection]
        try:
            
            if len(current_questions) == 0:
                abort(404)
            
            return jsonify({
                "success": True,
                "questions": current_questions,
                "total_questions": len(formatted_questions),
                "current_category": None,
                "categories": {
                    category.id: category.type for category in categories
                }
            
            })
        except:
            abort(422)

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route("/questions/<int:question_id>", methods=['DELETE'])
    def delete_question(question_id):
        '''try:
            question = Question.query.get(question_id)
        except:
            abort(500)
        if not question:
            return abort(404)
        else:
            try:
                question.delete()
            except:
                abort(500)
        return jsonify({
            'success': True,
            'question_id': question.id
        })
        '''
        try:
            question = Question.query.get(question_id)
        except:
            abort(500)

        try:
            if not question:
                abort(404)
                
            question.delete()
            
            return jsonify({
                "success": True,
                "deleted": question_id
            })
        except:
            abort(422)

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route("/questions", methods=["POST"])
    def create_new_question():
        body = request.get_json()
        if (body.get('searchTerm')):
            search = body.get("searchTerm", None)
        
            try:
                selection = Question.query.filter(Question.question.ilike('%{}%'.format(search))).all()
                current_questions = paginate_questions(request, selection)
                formatted_questions = [question.format() for question in selection]
                if len(formatted_questions) == 0:
                    abort(404)
            
                return jsonify({
                    "success": True,
                    "questions": current_questions,
                    "current_category": None,
                    "total_questions": len(formatted_questions)
                })
            except:
                abort(404)
        else:    

            new_question = body.get("question", None)
            new_answer = body.get("answer", None)
            new_category = body.get("category", None)
            new_difficulty = body.get("difficulty", None)
        
            try:
                question = Question(question=new_question, 
                                    answer=new_answer,
                                    category=new_category,
                                    difficulty=new_difficulty
                               )
                question.insert()
            
                return jsonify({
                    "success": True
                })
        
            except:
                abort(422)

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route("/categories/<int:id>/questions", methods=["GET"])
    def questions_per_category(id):
        category = Category.query.filter_by(id=id).one_or_none()

        # abort 400 for bad request if category isn't found
        if (category is None):
            abort(400)

        # get the matching questions
        selection = Question.query.filter_by(category=category.id).all()

        # paginate the selection
        category_questions = paginate_questions(request, selection)

        # return the results
        return jsonify({
            'success': True,
            'questions': category_questions,
            'total_questions': len(Question.query.all()),
            'current_category': category.type
        })

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route("/quizzes", methods=["POST"])
    def play_quiz():
        
        body = request.get_json()
        questions_category = body.get('quiz_category')
        previous_questions = body.get('previous_questions')
        
        if ((previous_questions == None) or (questions_category == None)):
            abort(400)

        # for a general quiz with a particular category
        if (questions_category['id'] == 0):
            quiz_questions = Question.query.all()
        # for a quiz with a specified category
        else:
            quiz_questions = Question.query.filter_by(category=questions_category['id']).all()

        # a function to check if question has been shown
        def confirm_question_status(question):
            shown = False
            for each_question in previous_questions:
                if (each_question == question.id):
                    shown = True
            return shown

        question = quiz_questions[random.randrange(0, len(quiz_questions), 1)]

        # check if used, execute until unused question found
        while (confirm_question_status(question)):
            question = quiz_questions[random.randrange(0, len(quiz_questions), 1)]

        return jsonify({
            'success': True,
            'question': question.format()
        })
        '''data = request.get_json()
        if not (data['quiz_category']['id']):
            abort(400)
        category_id = data['quiz_category']['id']
        previous_questions = data['previous_questions'] if data[
            'previous_questions'] else []
        if category_id != 0 and not Category.query.get(category_id):
            abort(404)
        try:
            question_data = Question.query.all(
            )if category_id == 0 else Question.query.filter_by(
                category=category_id).all()
        except:
            abort(500)
        questions = [question.format() for question in question_data]
        questions = list(
            filter(lambda x: x['id'] not in previous_questions, questions))
        if len(questions) == 0:
            abort(422)
        question = random.choice(questions)
        return jsonify({
            'success': True,
            'question': question
        })'''
        '''if (len(previous_questions) == len(quiz_questions)):
                return jsonify({
                    'success': True})'''

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
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
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "method not allowed"
        }), 405
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400
    
    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "internal server error"
        }), 500

    return app

