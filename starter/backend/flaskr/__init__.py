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
  @app.route('/questions/search', methods=['POST'])
  def search_question():
    try:
      body = request.get_json()
      search = body.get('searchTerm', '')
      questions = Question.query.filter(Question.question.ilike(f'%{search}%')).all()
      formatted_question = [question.format() for question in questions]

      if len(formatted_question) == 0:
        abort(400)
    
      return jsonify({
        'success': True,
        'questions': formatted_question,
        'total_questions': len(formatted_question)
      })
    except:
      abort(422)
 
  #Create a GET endpoint to get questions based on category. 
  @app.route('/categories/<int:category_id>/questions')
  def question_by_category(category_id):
    questions = Question.query.filter(Question.category == category_id).all()

    if len(questions) == 0:
      abort(404)

    selection = paginate_questions(request,questions)

    return jsonify({
      'success': True,
      'questions': selection,
      'total_questions': len(questions),
    })

# Create a POST endpoint to get questions to play the quiz. 
  @app.route('/quizzes', methods=['POST'])
  def play_quiz():
    body = request.get_json()
    quiz_category = body.get('quiz_category', None).get('id')
    previous_questions = body.get('previous_questions', None)
  
    if quiz_category == 0:  
      all_questions = Question.query.all()
    else:
      all_questions = Question.query.filter(Question.category == category).all()

    if len(all_questions) == 0:
      abort(404)

    random_question = [question.format() for question in all_questions if question.id not in previous_questions]
    question = random.choice(random_question)
    try:
      while len(random_question) > len(previous_questions):
        if question.get(id) not in previous_questions:
          return jsonify({
            'success': True,
            'question': question
          }), 200
    except:
      abort(404)

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


