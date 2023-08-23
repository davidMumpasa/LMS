from datetime import datetime
import decimal
import requests
import mysql.connector
from static.config import API_KEY
import concurrent.futures
from database import db
import json
from flask import Flask, request, jsonify, session
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

        connection = db.get_connection()
        cursor = connection.cursor()

        for user_data in users_data:
            # Extract user information from the response
            avatar = user_data['avatar']
            bio = user_data['bio']
            created_on_str = user_data['created_on']
            created_on = datetime.strptime(created_on_str, '%d/%m/%Y, %H:%M:%S')
            credits = user_data['credits']
            deactivation_date = user_data['deactivation_date'] or None
            email = user_data['email']
            first_name = user_data['first_name']
            id = user_data['id']
            language = user_data['language']
            last_name = user_data['last_name']
            last_updated_str = user_data['last_updated']
            last_updated = datetime.strptime(last_updated_str, '%d/%m/%Y, %H:%M:%S')
            level = user_data['level']
            points = user_data['points']
            restrict_email = user_data['restrict_email']
            status = user_data['status']
            timezone = user_data['timezone']
            user_type = user_data['user_type']
            created_on_mysql = created_on.strftime('%Y-%m-%d %H:%M:%S')
            last_updated_mysql = last_updated.strftime('%Y-%m-%d %H:%M:%S')

            insert_query = """
                INSERT INTO user (
                    user_id,
                    first_name,
                    last_name,
                    email,
                    avatar,
                    bio,
                    createdAt,
                    credits,
                    deactivation_date,
                    language,
                    updatedAt,
                    level,
                    points,
                    restrict_email,
                    status,
                    timezone,
                    user_type
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    first_name = VALUES(first_name),
                    last_name = VALUES(last_name),
                    email = VALUES(email),
                    avatar = VALUES(avatar),
                    bio = VALUES(bio),
                    createdAt = VALUES(createdAt),
                    credits = VALUES(credits),
                    deactivation_date = VALUES(deactivation_date),
                    language = VALUES(language),
                    updatedAt = VALUES(updatedAt),
                    level = VALUES(level),
                    points = VALUES(points),
                    restrict_email = VALUES(restrict_email),
                    status = VALUES(status),
                    timezone = VALUES(timezone),
                    user_type = VALUES(user_type)
            """

            values = (
                id, first_name, last_name, email, avatar, bio, created_on_mysql, credits, deactivation_date,
                language, last_updated_mysql, level, points, restrict_email, status, timezone, user_type
            )

            cursor.execute(insert_query, values)
            connection.commit()

        # Close the cursor and the connection
        cursor.close()
        connection.close()

        return "Users stored successfully!"
    except Exception as exception:
        print(f" {str(exception)}")
        raise exception


@app.route('/user_has_course', methods=['GET'])
def store_user_has_coures():
    try:
        url = 'https://fluid.talentlms.com/api/v1/users'

        auth = requests.auth.HTTPBasicAuth(API_KEY, '')

        response = requests.get(url, auth=auth)
        response.raise_for_status()  # Raise an HTTPError if the response status code is not 2xx

        users_data = response.json()

        connection = db.get_connection()
        cursor = connection.cursor()

        for user_data in users_data:
            # Extract user information from the response
            user_id = user_data['id']

            url2 = f'https://fluid.talentlms.com/api/v1/users/id:{user_id}'
            auth = requests.auth.HTTPBasicAuth(API_KEY, '')
            # Add a timeout value (e.g., 10 seconds)
            timeout = 10

            response = requests.get(url2, auth=auth, timeout=timeout)
            user_data2 = response.json()

            # Get the array of courses
            courses = user_data2['courses']

            for course in courses:
                # Extract course information from the response
                course_id = course['id']

                # Execute an SQL INSERT statement to insert the data into the table
                insert_query = """
                    INSERT INTO user_has_course (
                        user_id,
                        Course_id
                    )
                    VALUES (%s, %s)
                    ON DUPLICATE KEY UPDATE
                    Course_id = VALUES(Course_id),
                    user_id = VALUES(user_id)
                """

                values = (user_id, course_id)

                cursor.execute(insert_query, values)
                connection.commit()

        # Close the cursor and the connection
        cursor.close()
        connection.close()

        return "User_has_courses stored successfully!"
    except Exception as exception:
        print(f" {str(exception)}")
        raise exception


@app.route('/courses', methods=['GET'])
def store_courses():
    try:
        url = 'https://fluid.talentlms.com/api/v1/courses'

        auth = requests.auth.HTTPBasicAuth(API_KEY, '')

        response = requests.get(url, auth=auth)
        response.raise_for_status()  # Raise an HTTPError if the response status code is not 2xx

        courses_data = response.json()

        connection = db.get_connection()
        cursor = connection.cursor()

        for course_data in courses_data:
            # Extract course information from the response
            course_id = course_data['id']

            # Check if the course already exists in the database
            cursor.execute("SELECT id FROM course WHERE id = %s", (course_id,))
            existing_course = cursor.fetchone()
            if existing_course:
                continue  # Skip the duplicate entry

            avatar = course_data['avatar']
            big_avatar = course_data['big_avatar']
            creation_date = datetime.strptime(course_data['creation_date'], '%d/%m/%Y, %H:%M:%S').strftime(
                '%Y-%m-%d %H:%M:%S')
            creator_id = course_data['creator_id']
            description = course_data['description']
            expiration_datetime = None
            if course_data['expiration_datetime'] is not None:
                expiration_datetime = datetime.fromtimestamp(int(course_data['expiration_datetime'])).strftime(
                    '%Y-%m-%d %H:%M:%S')
            hide_from_catalog = course_data['hide_from_catalog']
            last_update_on = datetime.strptime(course_data['last_update_on'], '%d/%m/%Y, %H:%M:%S').strftime(
                '%Y-%m-%d %H:%M:%S')
            level = course_data['level']
            name = course_data['name']
            price = course_data['price'].replace('&#36;', '')
            shared = course_data['shared']
            shared_url = course_data['shared_url']
            start_datetime = None
            if course_data['start_datetime'] is not None:
                start_datetime = datetime.fromtimestamp(int(course_data['start_datetime'])).strftime(
                    '%Y-%m-%d %H:%M:%S')
            status = course_data['status']

            if course_data['time_limit'] is not None:
                time_limit = datetime.fromtimestamp(int(course_data['time_limit'])).strftime('%Y-%m-%d %H:%M:%S')
            Survey_id = None
            course_code = None

            insert_query = """
                INSERT INTO course (
                    id,
                    name,
                    avatar,
                    big_avatar,
                    course_code,
                    creation_date,
                    creator_id,
                    description,
                    expiration_datetime,
                    hide_from_catalog,
                    last_update_on,
                    level,
                    price,
                    shared,
                    shared_url,
                    start_datetime,
                    status,
                    time_limit
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    id = VALUES(id),
                    name = VALUES(name),
                    avatar = VALUES(avatar),
                    big_avatar = VALUES(big_avatar),
                    creation_date = VALUES(creation_date),
                    creator_id = VALUES(creator_id),
                    description = VALUES(description),
                    expiration_datetime = VALUES(expiration_datetime),
                    hide_from_catalog = VALUES(hide_from_catalog),
                    last_update_on = VALUES(last_update_on),
                    level = VALUES(level),
                    price = VALUES(price),
                    shared = VALUES(shared),
                    shared_url = VALUES(shared_url),
                    start_datetime = VALUES(start_datetime),
                    status = VALUES(status),
                    time_limit = VALUES(time_limit)
            """

            values = (
                course_id, name, avatar, big_avatar, course_code, creation_date, creator_id, description,
                expiration_datetime,
                hide_from_catalog, last_update_on, level, price, shared, shared_url, start_datetime, status, time_limit
            )

            cursor.execute(insert_query, values)
            connection.commit()

        # Close the cursor and the connection
        cursor.close()
        connection.close()

        return courses_data
    except Exception as exception:
        print(f" {str(exception)}")
        raise exception


@app.route('/badges', methods=['GET'])
def store_badges():
    try:
        url = 'https://fluid.talentlms.com/api/v1/users'
        auth = requests.auth.HTTPBasicAuth(API_KEY, '')

        response = requests.get(url, auth=auth)
        users_data = response.json()

        connection = db.get_connection()
        cursor = connection.cursor()

        badges_results = []

        for user_data in users_data:
            # Extract user information from the response
            user_id = user_data['id']

            url2 = f'https://fluid.talentlms.com/api/v1/users/id:{user_id}'
            auth = requests.auth.HTTPBasicAuth(API_KEY, '')
            response = requests.get(url2, auth=auth)
            user_data2 = response.json()

            # Get the array of badges
            badges = user_data2['badges']

            for badge in badges:
                # Extract badge information from the response
                badge_id = badge['badge_set_id']

                criteria = badge['criteria']
                image_url = badge['image_url']
                issued_on = badge['issued_on']
                issued_on_timestamp = badge['issued_on_timestamp']
                name = badge['name']
                badge_type = badge['type']

                # Execute an SQL INSERT statement to insert the data into the table
                insert_query = """
                    INSERT INTO badge (
                        user_id,
                        criteria,
                        image_url,
                        issued_on,
                        issued_on_timestamp,
                        name,
                        type
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        user_id = VALUES(user_id),
                        criteria = VALUES(criteria),
                        image_url = VALUES(image_url),
                        issued_on = VALUES(issued_on),
                        issued_on_timestamp = VALUES(issued_on_timestamp),
                        name = VALUES(name),
                        type = VALUES(type)
                """

                values = (user_id, criteria, image_url, issued_on, issued_on_timestamp, name, badge_type)
                badges_result = {
                    "badge_id": badge_id,
                    "user_id": user_id,
                    "criteria": criteria,
                    "image_url": image_url,
                    "issued_on": issued_on,
                    "issued_on_timestamp": issued_on_timestamp,
                    "name": name,
                    "badge_type": badge_type
                }
                badges_results.append(badges_result)
                cursor.execute(insert_query, values)
                connection.commit()

        cursor.close()
        connection.close()

        return json.dumps(badges_results)

    except Exception as exception:
        print(f"An exception occurred: {str(exception)}")
        raise exception


@app.route('/category', methods=['GET'])
def store_categories():
    try:
        url = 'https://fluid.talentlms.com/api/v1/categories'

        auth = requests.auth.HTTPBasicAuth(API_KEY, '')

        response = requests.get(url, auth=auth)
        categories_data = response.json()

        connection = db.get_connection()
        cursor = connection.cursor()

        for category_data in categories_data:
            # Extract category information from the response
            id = category_data['id']
            name = category_data['name']
            parent_category_id = category_data['parent_category_id']
            price = category_data['price'].replace('&#36;', '')  # Remove HTML entity and keep the decimal value

            # Convert the price to a decimal format
            price_decimal = decimal.Decimal(price)

            # Execute an SQL INSERT statement to insert the data into the table
            insert_query = """
                INSERT INTO category (
                    id,
                    name,
                    parent_category_id,
                    price
                )
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    id = VALUES(id),
                    name = VALUES(name),
                    parent_category_id = VALUES(parent_category_id),
                    price = VALUES(price)
            """

            values = (id, name, parent_category_id, price_decimal)

            cursor.execute(insert_query, values)
            connection.commit()

        # Close the cursor and the connection
        cursor.close()
        connection.close()

        return "Categories stored successfully!"
    except Exception as exception:
        print(f"An exception occurred: {str(exception)}")
        raise exception


@app.route('/certifications', methods=['GET'])
def store_certifications():
    try:
        url = 'https://fluid.talentlms.com/api/v1/users'

        auth = requests.auth.HTTPBasicAuth(API_KEY, '')

        response = requests.get(url, auth=auth)
        users_data = response.json()

        connection = db.get_connection()
        cursor = connection.cursor()

        for user_data in users_data:
            # Extract user information from the response
            user_id = user_data['id']
            url2 = f'https://fluid.talentlms.com/api/v1/users/id:{user_id}'
            auth = requests.auth.HTTPBasicAuth(API_KEY, '')
            # Add a timeout value (e.g., 10 seconds)
            timeout = 10

            response = requests.get(url2, auth=auth, timeout=timeout)
            user_data2 = response.json()

            # Get the array of badges
            certifications = user_data2['certifications']

            for certification in certifications:
                # Extract badge information from the response
                course_id = certification['course_id']
                course_name = certification['course_name']
                download_url = certification['download_url']
                public_url = certification['public_url']
                certification_id = certification['unique_id']

                try:
                    expiration_date = datetime.fromtimestamp(int(certification['expiration_date'])).strftime(
                        '%Y-%m-%d %H:%M:%S')
                    expiration_date_timestamp = datetime.fromtimestamp(
                        int(certification['expiration_date_timestamp'])).strftime('%Y-%m-%d %H:%M:%S')
                    issued_date = datetime.fromtimestamp(int(certification['issued_date'])).strftime(
                        '%Y-%m-%d %H:%M:%S')
                    issued_date_timestamp = datetime.fromtimestamp(
                        int(certification['issued_date_timestamp'])).strftime('%Y-%m-%d %H:%M:%S')
                except ValueError:
                    expiration_date = None
                    expiration_date_timestamp = None
                    issued_date = None

                    # Execute an SQL INSERT statement to insert the data into the table
                insert_query = """
                    INSERT INTO certification (
                        id,
                        course_name,
                        download_url,
                        expiration_date,
                        expiration_date_timestamp,
                        issued_date,
                        public_url,
                        Course_id
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                            id = VALUES(id),
                            course_name = VALUES(course_name),
                            download_url = VALUES(download_url),
                            expiration_date = VALUES(expiration_date),
                            expiration_date_timestamp = VALUES(expiration_date_timestamp),
                            issued_date = VALUES(issued_date),
                            public_url = VALUES(public_url),
                            course_id = VALUES(course_id)
                """

                values = (
                certification_id, course_name, download_url, expiration_date, expiration_date_timestamp, issued_date,
                public_url, course_id)

                cursor.execute(insert_query, values)
                connection.commit()

        # Close the cursor and the connection
        cursor.close()
        connection.close()

        return "Certifications stored successfully!"

    except Exception as exception:
        print(f"An exception occurred: {str(exception)}")
        raise exception


@app.route('/courseCat', methods=['GET'])
def store_courseCategory():
    try:
        url = 'https://fluid.talentlms.com/api/v1/courses'

        auth = requests.auth.HTTPBasicAuth(API_KEY, '')

        response = requests.get(url, auth=auth)
        response.raise_for_status()  # Raise an HTTPError if the response status code is not 2xx

        courses_data = response.json()

        connection = db.get_connection()
        cursor = connection.cursor()

        for course_data in courses_data:
            # Extract course information from the response
            course_id = course_data['id']
            category_id = course_data['category_id']

            # Execute an SQL INSERT statement to insert the data into the table
            insert_query = """
                INSERT INTO course_category (
                    course_id,
                    category_id
                )
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE
                    course_id = VALUES(course_id),
                    category_id = VALUES(category_id)
            """

            values = (course_id, category_id)

            cursor.execute(insert_query, values)
            connection.commit()

        # Close the cursor and the connection
        cursor.close()
        connection.close()

        return "course_category stored successfully!"
    except Exception as exception:
        print(f" {str(exception)}")
        raise exception


@app.route('/group', methods=['GET'])
def store_group():
    try:
        url = 'https://fluid.talentlms.com/api/v1/groups'
        auth = requests.auth.HTTPBasicAuth(API_KEY, '')

        response = requests.get(url, auth=auth)

        # Raise an HTTPError if the response status code is not 2xx
        response.raise_for_status()

        groups_data = response.json()

        connection = db.get_connection()
        cursor = connection.cursor()

        for group_data in groups_data:
            # Extract group information from the response
            group_id = group_data['id']
            belongs_to_branch = group_data['belongs_to_branch']
            description = group_data['description']
            key_column = group_data['key']
            name = group_data['name']
            max_redemptions = group_data['max_redemptions']
            price = group_data['price'].replace('&#36;', '')
            redemptions_sofar = group_data['redemptions_sofar']

            # Assuming you have the data you want to insert in a tuple called `data`
            insert_query = """
                INSERT INTO `group` (
                    id,
                    name,
                    description,
                    price,
                    key_column,
                    max_redemptions,
                    redemptions_sofar,
                    belongs_to_branch 
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    id = VALUES(id),
                    name = VALUES(name),
                    description = VALUES(description),
                    price = VALUES(price),
                    key_column = VALUES(key_column),
                    max_redemptions = VALUES(key_column),
                    redemptions_sofar = VALUES(redemptions_sofar),
                    belongs_to_branch = VALUES(belongs_to_branch)
            """

            values = (
            group_id, name, description, price, key_column, max_redemptions, redemptions_sofar, belongs_to_branch)

            cursor.execute(insert_query, values)
            connection.commit()

        # Close the cursor and the connection
        cursor.close()
        connection.close()

        return "Group stored successfully!"
    except Exception as exception:
        print(f" {str(exception)}")
        raise exception


@app.route('/groupCourse', methods=['GET'])
def store_groupCourse():
    try:
        url = 'https://fluid.talentlms.com/api/v1/groups'

        auth = requests.auth.HTTPBasicAuth(API_KEY, '')

        response = requests.get(url, auth=auth)

        # Raise an HTTPError if the response status code is not 2xx
        response.raise_for_status()

        groups_data = response.json()

        connection = db.get_connection()
        cursor = connection.cursor()

        for group_info in groups_data:
            # Extract group information from the response
            group_id = group_info['id']

            url2 = f'https://fluid.talentlms.com/api/v1/groups/id:{group_id}'
            auth = requests.auth.HTTPBasicAuth(API_KEY, '')
            # Add a timeout value (e.g., 10 seconds)
            timeout = 10

            response = requests.get(url2, auth=auth, timeout=timeout)
            groupe_data2 = response.json()

            courses = groupe_data2['courses']  # Access 'courses' from groupe_data2, not group_info2

            if not courses:  # Check if the courses array is empty
                course_id = None
                # Execute an SQL INSERT statement to insert the data into the table
                insert_query = """
                    INSERT INTO group_has_course (
                        group_id,
                        course_id
                    )
                    VALUES (%s, %s)
                    ON DUPLICATE KEY UPDATE
                        group_id = VALUES(group_id),
                        course_id = VALUES(course_id)
                """
                values = (group_id, course_id)
                cursor.execute(insert_query, values)
                connection.commit()
            else:
                for course in courses:
                    course_id = course['id']
                    # Execute an SQL INSERT statement to insert the data into the table
                    insert_query = """
                        INSERT INTO group_has_course (
                            group_id,
                            course_id
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                            group_id = VALUES(group_id),
                            course_id = VALUES(course_id)
                    """
                    values = (group_id, course_id)
                    cursor.execute(insert_query, values)
                    connection.commit()

        # Close the cursor and the connection
        cursor.close()
        connection.close()

        return "group_has_courses stored successfully!"
    except Exception as exception:
        print(f" {str(exception)}")
        raise exception


@app.route('/survey', methods=['GET'])
def store_servey():
    try:
        course = session.get('course')
        users = course['users']
        course_id = course['id']
        units = course['units']

        for unit in units:
            unit_name = unit['name']
            unit_type = unit['type']

            for user in users:
                user_id = user['id']

                if unit_name == "Survey" and unit_type == "SCORM | xAPI | cmi5":
                    unit_id = unit['id']
                    url = f'https://fluid.talentlms.com/api/v1/getusersprogressinunits/unit_id:{unit_id},user_id:{user_id}'
                    auth = requests.auth.HTTPBasicAuth(API_KEY, '')

                    response = requests.get(url, auth=auth)

                    # Raise an HTTPError if the response status code is not 2xx
                    response.raise_for_status()

                    survey_data = response.json()

                    connection = db.get_connection()
                    cursor = connection.cursor()

                    score = survey_data['score']
                    status = survey_data['status']

                    # Execute an SQL INSERT statement to insert the data into the table
                    insert_query = """
                        INSERT INTO survey (
                            id
                        )
                        VALUES (%s)
                        ON DUPLICATE KEY UPDATE
                            id = VALUES(id)
                    """
                    values = (unit_id,)
                    cursor.execute(insert_query, values)
                    connection.commit()

                    # Execute an SQL INSERT statement to insert the data into the table
                    insert_query = """
                        INSERT INTO survey_has_user (
                            survey_id,
                            user_id,
                            score,
                            status

                        )
                        VALUES (%s, %s,%s,%s)
                        ON DUPLICATE KEY UPDATE
                            survey_id = VALUES(survey_id),
                            user_id = VALUES(user_id),
                            score = VALUES(score),
                            status = VALUES(status)
                    """
                    values = (unit_id, user_id, score, status,)
                    cursor.execute(insert_query, values)
                    connection.commit()

                    insert_query = """
                            INSERT INTO course (
                                id,
                                Survey_id
                            )
                            VALUES (%s,%s)
                            ON DUPLICATE KEY UPDATE
                                id = VALUES(id),
                                Survey_id = VALUES(Survey_id)
                    """
                    course_values = (course_id, unit_id,)
                    cursor.execute(insert_query, course_values)
                    connection.commit()

        # Close the cursor and the connection
        cursor.close()
        connection.close()

        return "Survey stored successfully"
    except Exception as exception:
        print(f" {str(exception)}")
        raise exception


@app.route('/surveys', methods=['GET'])
def store_serveys():
    try:
        url1 = 'https://fluid.talentlms.com/api/v1/courses'

        auth = requests.auth.HTTPBasicAuth(API_KEY, '')
        response = requests.get(url1, auth=auth)
        courses = response.json()

        for course_data in courses:
            course_id = course_data['id']
            url2 = f'https://fluid.talentlms.com/api/v1/courses/id:{course_id}'
            auth = requests.auth.HTTPBasicAuth(API_KEY, '')
            response = requests.get(url2, auth=auth)
            course = response.json()

            users = course['users']
            units = course['units']

            for unit in units:
                unit_name = unit['name']
                unit_type = unit['type']

                for user in users:
                    user_id = user['id']

                    if unit_name == "Survey" and unit_type == "SCORM | xAPI | cmi5":
                        unit_id = unit['id']
                        url = f'https://fluid.talentlms.com/api/v1/getusersprogressinunits/unit_id:{unit_id},user_id:{user_id}'
                        auth = requests.auth.HTTPBasicAuth(API_KEY, '')

                        response = requests.get(url, auth=auth)

                        # Raise an HTTPError if the response status code is not 2xx
                        response.raise_for_status()

                        survey_data = response.json()

                        connection = db.get_connection()
                        cursor = connection.cursor()

                        score = survey_data['score']
                        status = survey_data['status']

                        # Execute an SQL INSERT statement to insert the data into the table
                        insert_query = """
                            INSERT INTO survey (
                                id,
                                course_id
                            )
                            VALUES (%s,%s)
                            ON DUPLICATE KEY UPDATE
                                id = VALUES(id),
                                course_id = VALUES(course_id)
                        """
                        values = (unit_id,)
                        cursor.execute(insert_query, values)
                        connection.commit()

                        # Execute an SQL INSERT statement to insert the data into the table
                        insert_query = """
                            INSERT INTO survey_has_user (
                                survey_id,
                                user_id,
                                score,
                                status

                            )
                            VALUES (%s, %s,%s,%s)
                            ON DUPLICATE KEY UPDATE
                                survey_id = VALUES(survey_id),
                                user_id = VALUES(user_id),
                                score = VALUES(score),
                                status = VALUES(status)
                        """
                        values = (unit_id, user_id, score, status,)
                        cursor.execute(insert_query, values)
                        connection.commit()

        # Close the cursor and the connection
        cursor.close()
        connection.close()

        return "Survey stored successfully"
    except Exception as exception:
        print(f" {str(exception)}")
        raise exception


@app.route('/course/<int:course_id>', methods=['GET'])
def get_course(course_id):
    API_KEY = 'aRh1ck3Zc2LaGKAqHqBTecRTfZb9pH'
    url = f'https://fluid.talentlms.com/api/v1/courses/id:{course_id}'
    auth = requests.auth.HTTPBasicAuth(API_KEY, '')

    response = requests.get(url, auth=auth)
    course_data = response.json()

    inits = course_data['units']
    users = course_data['users']

    session['inits'] = inits
    session['users'] = users

    return store_test_and_quiz(course_data)


@app.route('/quizz', methods=['GET'])
def store_test_and_quiz(course):
    try:
        course_id = course['id']
        users = course['users']
        units = course['units']

        quiz_results = []

        connection = db.get_connection()  # Use the get_connection() function from your db module
        cursor = connection.cursor()

        for unit in units:
            unit_name = unit['name']
            unit_type = unit['type']

            if unit_type == "SCORM | xAPI | cmi5" and unit_name != "Survey":
                quizz_id = unit['id']

                for user in users:
                    user_id = user['id']
                    url = f'https://fluid.talentlms.com/api/v1/getusersprogressinunits/unit_id:{quizz_id},user_id:{user_id}'
                    auth = requests.auth.HTTPBasicAuth(API_KEY, '')

                    response = requests.get(url, auth=auth)
                    response.raise_for_status()
                    quiz_data = response.json()

                    score = quiz_data['score']
                    status = quiz_data['status']

                    # Insert quiz data into the appropriate table
                    insert_quiz_query = """
                        INSERT INTO quizz (
                            quizz_id,
                            quizz_name
                        )
                        VALUES (%s, %s)
                        ON DUPLICATE KEY UPDATE
                            quizz_id = VALUES(quizz_id),
                            quizz_name = VALUES(quizz_name)
                    """
                    quiz_values = (quizz_id, unit_name)

                    cursor.execute(insert_quiz_query, quiz_values)
                    connection.commit()

                    # Insert quiz data into the appropriate table
                    insert_quiz_query2 = """
                        INSERT INTO quizz_has_user (
                            quizz_id,
                            user_id,
                            score,
                            status
                        )
                        VALUES (%s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                            quizz_id = VALUES(quizz_id),
                            user_id = VALUES(user_id),
                            score = VALUES(score),
                            status = VALUES(status)
                    """
                    quiz_values2 = (quizz_id, user_id, score, status)

                    cursor.execute(insert_quiz_query2, quiz_values2)
                    connection.commit()

                    # Insert quiz data into the appropriate table
                    insert_quiz_query3 = """
                        INSERT INTO course (
                            id,
                            quizz_id
                        )
                        VALUES (%s,%s)
                        ON DUPLICATE KEY UPDATE
                            id = VALUES(id),
                            quizz_id = VALUES(quizz_id)
                    """
                    quiz_values3 = (course_id, quizz_id,)
                    cursor.execute(insert_quiz_query3, quiz_values3)
                    connection.commit()

                    quiz_result = {
                        "user_id": user_id,
                        "unit_name": unit_name,
                        "score": score,
                        "status": status
                    }
                    quiz_results.append(quiz_result)

        # Close the cursor and the connection
        cursor.close()
        connection.close()

        return json.dumps(quiz_results)

    except Exception as exception:
        print(f" {str(exception)}")
        raise exception

    return jsonify({"message": "Success"})


@app.route('/quizzes', methods=['GET'])
def store_quizzes():
    try:
        url1 = 'https://fluid.talentlms.com/api/v1/courses'

        auth = requests.auth.HTTPBasicAuth(API_KEY, '')
        response = requests.get(url1, auth=auth)
        courses = response.json()
        connection = db.get_connection()
        cursor = connection.cursor()

        quiz_results = []

        for course_data in courses:
            course_id = course_data['id']
            url2 = f'https://fluid.talentlms.com/api/v1/courses/id:{course_id}'
            auth = requests.auth.HTTPBasicAuth(API_KEY, '')
            response = requests.get(url2, auth=auth)
            course = response.json()

            users = course['users']
            units = course['units']

            for unit in units:
                unit_name = unit['name']
                unit_type = unit['type']

                if unit_type == "SCORM | xAPI | cmi5" and unit_name != "Survey":
                    quizz_id = unit['id']

                    for user in users:
                        user_id = user['id']
                        url = f'https://fluid.talentlms.com/api/v1/getusersprogressinunits/unit_id:{quizz_id},user_id:{user_id}'
                        auth = requests.auth.HTTPBasicAuth(API_KEY, '')

                        response = requests.get(url, auth=auth)
                        response.raise_for_status()
                        quiz_data = response.json()

                        score = quiz_data['score']
                        status = quiz_data['status']

                        # Insert quiz data into the appropriate table
                        insert_quiz_query = """
                            INSERT INTO quizz (
                                quizz_id,
                                quizz_name,
                                course_id
                            )
                            VALUES (%s, %s, %s)
                            ON DUPLICATE KEY UPDATE
                                quizz_id = VALUES(quizz_id),
                                quizz_name = VALUES(quizz_name),
                                course_id = VALUES(course_id)
                        """
                        quiz_values = (quizz_id, unit_name, course_id)

                        cursor.execute(insert_quiz_query, quiz_values)
                        connection.commit()

                        # Insert quiz data into the appropriate table
                        insert_quiz_query2 = """
                            INSERT INTO quizz_has_user (
                                quizz_id,
                                user_id,
                                score,
                                status
                            )
                            VALUES (%s, %s, %s, %s)
                            ON DUPLICATE KEY UPDATE
                                quizz_id = VALUES(quizz_id),
                                user_id = VALUES(user_id),
                                score = VALUES(score),
                                status = VALUES(status)
                        """
                        quiz_values2 = (quizz_id, user_id, score, status)

                        cursor.execute(insert_quiz_query2, quiz_values2)
                        connection.commit()

                        quiz_result = {
                            "user_id": user_id,
                            "unit_name": unit_name,
                            "score": score,
                            "status": status
                        }
                        quiz_results.append(quiz_result)

        # Close the cursor and the connection
        cursor.close()
        connection.close()

        return json.dumps(quiz_results)

    except Exception as exception:
        print(f" {str(exception)}")
        raise exception

    return jsonify({"message": "Success"})


@app.route('/tests/<int:course_id>', methods=['GET'])
def store_tests(course_id):
    try:
        url = f'https://fluid.talentlms.com/api/v1/courses/id:{course_id}'
        auth = requests.auth.HTTPBasicAuth(API_KEY, '')

        response = requests.get(url, auth=auth)
        course_data = response.json()

        units = course_data['units']
        users = course_data['users']

        quiz_results = []

        for unit in units:
            test_id = unit['id']

            for user in users:
                user_id = user['id']

                url = f'https://fluid.talentlms.com/api/v1/gettestanswers/test_id:{test_id},user_id:{user_id}'
                auth = requests.auth.HTTPBasicAuth(API_KEY, '')
                response = requests.get(url, auth=auth)
                response.raise_for_status()
                test_datas = response.json()

                connection = db.get_connection()
                cursor = connection.cursor()

                completion_status = test_datas['completion_status']
                test_name = test_datas['test_name']
                score = test_datas['score']
                cleaned_score = score.replace('%', '').strip()

                insert_quiz_query = """
                    INSERT INTO quizz (
                        quizz_id,
                        quizz_name,
                        course_id
                    )
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        quizz_id = VALUES(quizz_id),
                        quizz_name = VALUES(quizz_name),
                        course_id = VALUES(course_id)
                """
                quiz_values = (test_id, test_name, course_id)

                cursor.execute(insert_quiz_query, quiz_values)
                connection.commit()

                insert_quiz_query2 = """
                    INSERT INTO quizz_has_user (
                        quizz_id,
                        user_id,
                        score,
                        status
                    )
                    VALUES (%s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        quizz_id = VALUES(quizz_id),
                        user_id = VALUES(user_id),
                        score = VALUES(score),
                        status = VALUES(status)
                """
                quiz_values2 = (test_id, user_id, cleaned_score, completion_status)

                cursor.execute(insert_quiz_query2, quiz_values2)
                connection.commit()

                quiz_result = {
                    "user_id": user_id,
                    "test_name": test_name,
                    "score": score,
                    "status": completion_status
                }

                quiz_results.append(quiz_result)

                cursor.close()
                connection.close()

        return json.dumps(quiz_results)

    except Exception as exception:
        print(f"Exception: {str(exception)}")
        raise exception

    return jsonify({"message": "Success"})


if __name__ == '__main__':
    app.run(debug=True)