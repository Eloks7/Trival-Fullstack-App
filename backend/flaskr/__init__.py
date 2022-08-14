import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
    #Using Argument object to get the value of page parameter
    page = request.args.get('page', 1, type=int) #Defaults to 1 without page argument
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    
    # List interpolation to format each question
    formatted_questions = [question.format() for question in selection]
    # 
    current_questions = formatted_questions[start:end]
    
    return current_questions

# Application factory function
def create_app(test_config=None):
    # create and configure the app (current flask instance)
    app = Flask(__name__) # "__name__" is the name of current Python module"
    setup_db(app)
    #allowed CORS
    CORS(app)

    # Runs after a request is received and takes response as a parameter
    @app.after_request
    def after_request(response):
        response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization,true")
        response.headers.add("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS")
        return response


    @app.route("/categories", methods=["GET"])
    def get_all_categories():
        try:
            categories = Category.query.order_by(Category.type).all()
          
            return jsonify({
                "success": True,
                "categories": {
                    category.id: category.type for category in categories
                }
            })
        except:
            abort(422)


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


    @app.route("/questions/<int:question_id>", methods=['DELETE'])
    def delete_question(question_id):

        # Try to get the question to be deleted
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


    @app.route("/questions", methods=["POST"])
    def create_new_question():
        body = request.get_json()
        if (body.get('searchTerm')):
            search = body.get("searchTerm", None)
        
            try:
                selection = Question.query.filter(Question.question.ilike('%{}%'.format(search))).all()
                current_questions = paginate_questions(request, selection)
                formatted_questions = [question.format() for question in selection]
                #if len(formatted_questions) == 0:
                #    abort(404)
            
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


    @app.route("/categories/<int:id>/questions", methods=["GET"])
    def questions_per_category(id):
        category = Category.query.filter_by(id=id).one_or_none()

        # abort 404 if category isn't found
        if (category is None):
            abort(404)

        # get the matching questions
        selection = Question.query.filter_by(category=category.id).all()

        # paginate the selection
        category_questions = paginate_questions(request, selection)
        formatted_questions = [question.format() for question in selection]

        # return the results
        return jsonify({
            'success': True,
            'questions': category_questions,
            'total_questions': len(formatted_questions),
            'current_category': category.type
        })


    @app.route("/quizzes", methods=["POST"])
    def play_quiz():
        
        body = request.get_json()
        questions_category = body.get('quiz_category')
        previous_questions = body.get('previous_questions')
        
        if ((previous_questions == None) or (questions_category == None)):
            abort(400)

        # for a general quiz without a particular category
        if (questions_category == 0):
            quiz_questions = Question.query.all()
        # for a quiz with a specified category
        else:
            quiz_questions = Question.query.filter_by(category=questions_category).all()

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
            if len(previous_questions) == len(quiz_questions):
                return jsonify({
                    'success': True
                })

        return jsonify({
            'success': True,
            'question': question.format()
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

