import requests
import mysql.connector
from static.config import API_KEY
from database.Entities import db
from bussinessLogic.logic import store_user, store_user_has_courses, store_courses, store_badges, store_categories, \
    store_certifications, store_course_category, store_groups, store_group_courses, retrieve_and_store_quiz_results, retrieve_and_store_tests
import json
from flask import Flask,jsonify
from flask_cors import CORS
import secrets
from requests.exceptions import RequestException, HTTPError, ConnectionError
from ExecptionHandling.error_handlers import (
    handle_request_exception,
    handle_http_exception,
    handle_connection_exception,
    handle_mysql_exception,
    handle_unexpected_exception,
)

app = Flask(__name__)
CORS(app)
strong_secret_key = secrets.token_hex(32)
app.secret_key = strong_secret_key

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:DavidEbula1999@localhost:3306/testdatabase'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

# Register the error handling functions using the @app.errorhandler decorator

app.errorhandler(RequestException)(handle_request_exception)
app.errorhandler(HTTPError)(handle_http_exception)
app.errorhandler(ConnectionError)(handle_connection_exception)
app.errorhandler(mysql.connector.Error)(handle_mysql_exception)
app.errorhandler(Exception)(handle_unexpected_exception)


@app.route('/users', methods=['GET'])
def update_users():
    try:
        url = 'https://fluid.talentlms.com/api/v1/users'
        auth = requests.auth.HTTPBasicAuth(API_KEY, '')
        response = requests.get(url, auth=auth)
        response.raise_for_status()  # Raise an HTTPError if the response status code is not 2xx
        users_data = response.json()
        store_user(users_data)

        return jsonify(users_data)
    except Exception as exception:
        print(f" {str(exception)}")
        raise exception


@app.route('/user_has_course', methods=['GET'])
def store_user_has_coures():
    try:
        result = store_user_has_courses()
        return result
    except Exception as exception:
        print(f" {str(exception)}")
        raise exception


@app.route('/courses', methods=['GET'])
def update_courses():
    try:
        url = 'https://fluid.talentlms.com/api/v1/courses'
        auth = requests.auth.HTTPBasicAuth(API_KEY, '')
        response = requests.get(url, auth=auth)
        response.raise_for_status()  # Raise an HTTPError if the response status code is not 2xx
        courses_data = response.json()

        store_courses(courses_data)  # Call the store_courses function

        return jsonify(courses_data)
    except Exception as exception:
        print(f" {str(exception)}")
        raise exception


@app.route('/badges', methods=['GET'])
def update_badges():
    try:
        url = 'https://fluid.talentlms.com/api/v1/users'
        auth = requests.auth.HTTPBasicAuth(API_KEY, '')

        response = requests.get(url, auth=auth)
        users_data = response.json()

        badges_results = store_badges(users_data)  # Call the store_badges function

        return json.dumps(badges_results)

    except Exception as exception:
        print(f"An exception occurred: {str(exception)}")
        raise exception


@app.route('/categories', methods=['GET'])
def update_categories():
    try:
        url = 'https://fluid.talentlms.com/api/v1/categories'
        auth = requests.auth.HTTPBasicAuth(API_KEY, '')

        response = requests.get(url, auth=auth)
        categories_data = response.json()

        result_message = store_categories(categories_data)  # Call the store_categories function

        return result_message

    except Exception as exception:
        print(f"An exception occurred: {str(exception)}")
        raise exception


@app.route('/certifications', methods=['GET'])
def certifications_route():
    result_message = store_certifications()
    return result_message


@app.route('/courseCat', methods=['GET'])
def store_courseCategory_route():
    try:
        result = store_course_category()
        return result
    except Exception as exception:
        return str(exception)


@app.route('/store_groups', methods=['GET'])
def store_groups_route():
    result = store_groups(API_KEY)
    return result


@app.route('/store_group_courses', methods=['GET'])
def store_group_courses_route():
    result = store_group_courses(API_KEY)
    return result


@app.route('/getQuizResults', methods=['GET'])
def get_quiz_results():
    retrieve_and_store_quiz_results()
    return "Quiz results retrieved and stored successfully."


@app.route('/tests/<int:course_id>', methods=['GET'])
def store_tests(course_id):
    try:
        quiz_results = retrieve_and_store_tests(course_id, API_KEY, db)
        return json.dumps(quiz_results)

    except Exception as exception:
        print(f"Exception: {str(exception)}")
        return jsonify({"message": "Error occurred"})


if __name__ == '__main__':
    app.run(debug=True)
