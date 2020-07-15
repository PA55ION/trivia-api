import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
# from werkzeug.exceptions import HTTPException
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, questions_list):
  page = request.args.get('page', 1, type=int)
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE
  questions = [question.format() for question in questions_list]
  paginated_questions = questions[start:end]
  return paginated_questions

def get_category_list():
  categories = {}
  for category in Category.query.all():
    categories[category.id] = category.type
  return categories

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  db = setup_db(app)
  cors = CORS(app, resources={r'/api/*': {'origins': '*'}})

# Use the after_request decorator to set Access-Control-Allow
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET, PATCH,  POST, DELETE, OPTIONS')
    return response
    
#Create an endpoint to handle GET requests for all available categories.
  @app.route('/categories', methods=['GET'])
  def get_categories():
    categories = Category.query.all()
    category_list = {
      category.id: category.type for category in categories
    }

    return jsonify({
      'success': True,
      'categories': category_list,
      'status': 200  # success
    })


# Create an endpoint to handle GET requests for questions, including pagination (every 10 questions). 
  @app.route('/questions', methods=['GET'])
  def get_questions():
        questions_list = Question.query.all()
        paginated_questions = paginate_questions(request, questions_list)
        if len(paginated_questions) == 0:
            abort(404)
        return jsonify({
            'success': True,
            'questions': paginated_questions,
            'total_questions': len(questions_list),
            'categories': get_category_list()
        })

# Create an endpoint to DELETE question using a question ID
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    question = Question.query.get(question_id)
    question.delete()
    return jsonify({
      'success': True,
      'message': 'Successfully deleted'
    })

# Create an endpoint to POST a new question
  @app.route('/questions', methods=['POST'])
  def create_question():
    body = request.get_json()

    new_question = body.get('question', None)
    new_answer = body.get('answer', None)
    new_category = body.get('category', None)
    new_difficulty = body.get('difficulty', None)

    try:
      question = Question(question=new_question, answer=new_answer, difficulty=new_difficulty, category=new_category)
      question.insert()

      selection = Question.query.order_by('id').all()

      return jsonify({
        'success': True,
        'total_questions': len(selection)
      })
    except:
      abort(422)

# Create a POST endpoint to get questions based on a search term.
  # @app.route('/question/search', methods=['POST'])
  # def search_question():
  #   search = data.get('searchTerm')
  #   questions = Question.query.filter(Question.question.ilike('%{}%'.format(search))).all()

  #   paginated_questions = paginate(request, questions)
    
  #   return jsonify({
  #     'success': True,
  #     'status': 200,
  #     'questions': paginated_questions,
  #     'total_questions': len(paginated_questions)
  #   })

  @app.route('/questions/search', methods=['POST'])
  def search_questions():
    if not request.method == 'POST':
      abort(405)
      
      data = request.get_json()
      search_term = data.get('searchTerm')
      if not search_term:
        abort(422)
        try:
          questions = Question.query.filter(
          Question.question.ilike('%{}%'.format(search_term))).all()
          if not questions:
            abort(422)
            paginated_questions = paginate(request, questions)
            return jsonify({
              'success': True,
              'status': 200,
              'questions': paginated_questions,
              'total_questions':  len(paginated_questions)
            })
        except:
            abort(422)

  










  '''
  #TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''

  '''
  #TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''


  '''
  #TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      'success': False,
      'error': 404,
      'message': ' Not Found'
    }), 404
  
  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      'success': False,
      'error': 400,
      'messgae': 'Bad Request'
    }), 400

  @app.errorhandler(405)
  def method_not_allowed(error):
    return jsonify({
      'success': False,
      'error': 405,
      'message': 'Method Not Allowed'
    }), 405

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      'success': False,
      'error': 422,
      'message': 'unprocessable'
    }), 422

  @app.errorhandler(500)
  def server_error(error):
    return jsonify({
      'success': False,
      'error': 500,
      'message': 'Internal Server Error'
    }), 500


  return app

    