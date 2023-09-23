from datetime import datetime
from decimal import Decimal
from flask import jsonify
from database.Entities import db, User, UserCourse, Course, Badge, Category, Certification, Group, GroupCourse, \
    QuizzUser, Quizz
from static.config import API_KEY
from sqlalchemy.orm import Session
from base64 import b64encode
from database import databseConnection
from sqlalchemy import func
import requests


def store_user(json_data):
    for user_data in json_data:
        # Extract user information from the response
        id = user_data.get('id')
        if not id:
            continue  # Skip this user if 'id' is missing

        existing_user = User.query.filter_by(user_id=id).first()
        if existing_user:
            return jsonify({'message': 'User with the same id already exists'}), 400

        avatar = user_data.get('avatar')
        bio = user_data.get('bio')
        created_on_str = user_data.get('created_on')
        created_on = datetime.strptime(created_on_str, '%d/%m/%Y, %H:%M:%S') if created_on_str else None
        credits = user_data.get('credits')
        deactivation_date = user_data.get('deactivation_date')
        email = user_data.get('email')
        first_name = user_data.get('first_name')
        language = user_data.get('language')
        last_name = user_data.get('last_name')
        last_updated_str = user_data.get('last_updated')
        last_updated = datetime.strptime(last_updated_str, '%d/%m/%Y, %H:%M:%S') if last_updated_str else None
        level = user_data.get('level')
        points = user_data.get('points')
        restrict_email = user_data.get('restrict_email')
        status = user_data.get('status')
        timezone = user_data.get('timezone')
        user_type = user_data.get('user_type')

        # Create the User object
        user = User(
            user_id=id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            avatar=avatar,
            bio=bio,
            createdAt=created_on,
            credits=credits,
            deactivation_date=deactivation_date,
            language=language,
            updatedAt=last_updated,
            level=level,
            points=points,
            restrict_email=restrict_email,
            status=status,
            timezone=timezone,
            user_type=user_type
        )

        # Create a list of UserCourse objects for each course associated with the user
        user_courses_data = user_data.get('courses', [])
        user_courses = []
        for course_data in user_courses_data:
            # Extract course information and create UserCourse objects
            # Make sure to adjust these fields based on your data structure
            course_id = course_data.get('course_id')
            course_start_date_str = course_data.get('start_date')
            course_start_date = datetime.strptime(course_start_date_str, '%d/%m/%Y') if course_start_date_str else None

            user_course = UserCourse(
                User_id=user.id,
                Course_id=course_id,
                start_date=course_start_date
            )

            user_courses.append(user_course)

        # Assign the user_courses list to the User object
        user.user_courses = user_courses

        # Add the User object and associated UserCourse objects to the database session
        db.session.add(user)

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': 'Error while committing to the database'}), 500


def store_user_has_courses():
    try:
        url = 'https://fluid.talentlms.com/api/v1/users'
        auth = requests.auth.HTTPBasicAuth(API_KEY, '')
        response = requests.get(url, auth=auth)
        response.raise_for_status()  # Raise an HTTPError if the response status code is not 2xx
        users_data = response.json()

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

                # Check if the user-course association already exists
                user_course = UserCourse.query.filter_by(User_id=user_id, Course_id=course_id).first()

                if not user_course:
                    # Create a new UserCourse object and add it to the database
                    user_course = UserCourse(User_id=user_id, Course_id=course_id)
                    db.session.add(user_course)

        # Commit the changes to the database
        db.session.commit()

        return "User_has_courses stored successfully!"
    except Exception as exception:
        print(f" {str(exception)}")
        raise exception


def store_courses(json_data):
    for course_data in json_data:
        # Extract course information from the response
        course_id = course_data.get('id')
        if not course_id:
            continue  # Skip this course if 'id' is missing

        existing_course = Course.query.get(course_id)
        if existing_course:
            return jsonify({'message': 'Course with the same id already exists'}), 400

        avatar = course_data.get('avatar')
        big_avatar = course_data.get('big_avatar')
        creation_date_str = course_data.get('creation_date')
        creation_date = datetime.strptime(creation_date_str, '%d/%m/%Y, %H:%M:%S') if creation_date_str else None
        creator_id = course_data.get('creator_id')
        description = course_data.get('description')
        expiration_datetime_str = course_data.get('expiration_datetime')
        expiration_datetime = datetime.strptime(expiration_datetime_str,
                                                '%d/%m/%Y, %H:%M:%S') if expiration_datetime_str else None
        hide_from_catalog = course_data.get('hide_from_catalog')
        last_update_on_str = course_data.get('last_update_on')
        last_update_on = datetime.strptime(last_update_on_str, '%d/%m/%Y, %H:%M:%S') if last_update_on_str else None
        level = course_data.get('level')
        name = course_data.get('name')
        price = course_data.get('price')
        shared = course_data.get('shared')
        shared_url = course_data.get('shared_url')
        start_datetime_str = course_data.get('start_datetime')
        start_datetime = datetime.strptime(start_datetime_str, '%d/%m/%Y, %H:%M:%S') if start_datetime_str else None
        status = course_data.get('status')
        time_limit_str = course_data.get('time_limit')
        time_limit = datetime.strptime(time_limit_str, '%d/%m/%Y, %H:%M:%S') if time_limit_str else None
        Survey_id = None
        course_code = None

        # Create the Course object
        course = Course(
            id=course_id,
            name=name,
            avatar=avatar,
            big_avatar=big_avatar,
            course_code=course_code,
            creation_date=creation_date,
            creator_id=creator_id,
            description=description,
            expiration_datetime=expiration_datetime,
            hide_from_catalog=hide_from_catalog,
            last_update_on=last_update_on,
            level=level,
            price=price,
            shared=shared,
            shared_url=shared_url,
            start_datetime=start_datetime,
            status=status,
            time_limit=time_limit
        )

        # Add the Course object to the database session
        db.session.add(course)

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': 'Error while committing to the database'}), 500


def store_badges(json_data):
    badges_results = []

    for user_data in json_data:
        # Extract user information from the response
        user_id = user_data.get('id')
        if not user_id:
            continue  # Skip this user if 'id' is missing

        # Get the array of badges
        badges = user_data.get('badges', [])

        for badge in badges:
            # Extract badge information from the response
            badge_id = badge.get('badge_set_id')
            if not badge_id:
                continue  # Skip this badge if 'badge_set_id' is missing

            criteria = badge.get('criteria')
            image_url = badge.get('image_url')
            issued_on = badge.get('issued_on')
            issued_on_timestamp = badge.get('issued_on_timestamp')
            name = badge.get('name')
            badge_type = badge.get('type')

            # Check if the badge already exists in the database
            existing_badge = Badge.query.get(badge_id)

            if existing_badge:
                continue  # Skip the duplicate entry

            # Execute an SQL INSERT statement to insert the data into the table
            badge = Badge(
                badge_id=badge_id,
                user_id=user_id,
                criteria=criteria,
                image_url=image_url,
                issued_on=issued_on,
                issued_on_timestamp=issued_on_timestamp,
                name=name,
                badge_type=badge_type
            )

            db.session.add(badge)

            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                return jsonify({'message': 'Error while committing to the database'}), 500

            badge_result = {
                "badge_id": badge_id,
                "user_id": user_id,
                "criteria": criteria,
                "image_url": image_url,
                "issued_on": issued_on,
                "issued_on_timestamp": issued_on_timestamp,
                "name": name,
                "badge_type": badge_type
            }
            badges_results.append(badge_result)

    return badges_results


def store_categories(json_data):
    try:
        for category_data in json_data:
            # Extract category information from the response
            category_id = category_data.get('id')
            if not category_id:
                continue  # Skip this category if 'id' is missing

            # Check if the category already exists in the database
            existing_category = Category.query.get(category_id)

            if existing_category:
                continue  # Skip the duplicate entry

            name = category_data.get('name')
            parent_category_id = category_data.get('parent_category_id')
            price_str = category_data.get('price')

            # Ensure that 'price_str' is a valid numeric string before converting to Decimal
            try:
                price_decimal = Decimal(price_str)
            except (ValueError, TypeError, decimal.InvalidOperation):
                # Handle the case where 'price_str' is not a valid numeric string
                price_decimal = None

            # Create the Category object and add it to the session
            category = Category(
                id=category_id,
                name=name,
                parent_category_id=parent_category_id,
                price=price_decimal  # Assign the Decimal value or None if conversion fails
            )

            db.session.add(category)

            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                return jsonify({'message': 'Error while committing to the database'}), 500

        return "Categories stored successfully!"
    except Exception as exception:
        print(f"An exception occurred: {str(exception)}")
        raise exception


def store_certifications():
    try:
        url = 'https://fluid.talentlms.com/api/v1/users'
        auth = requests.auth.HTTPBasicAuth(API_KEY, '')

        response = requests.get(url, auth=auth)
        users_data = response.json()

        for user_data in users_data:
            # Extract certifications from the response
            certifications = user_data.get('certifications', [])

            for certification in certifications:
                # Extract certification information from the response
                course_id = certification['course_id']
                course_name = certification['course_name']
                download_url = certification['download_url']
                public_url = certification['public_url']
                certification_id = certification['unique_id']

                expiration_date = certification.get('expiration_date', None)
                expiration_date_timestamp = certification.get('expiration_date_timestamp', None)
                issued_date = certification.get('issued_date', None)

                # Create a Certification object
                certification_obj = Certification(
                    id=certification_id,
                    course_name=course_name,
                    download_url=download_url,
                    expiration_date=expiration_date,
                    expiration_date_timestamp=expiration_date_timestamp,
                    issued_date=issued_date,
                    public_url=public_url,
                    course_id=course_id
                )

                # Create a session and add the Certification object
                session = Session()
                session.add(certification_obj)

                try:
                    # Commit the session to insert the data
                    session.commit()
                except IntegrityError as e:
                    # Handle duplicate key errors if needed
                    session.rollback()
                finally:
                    # Close the session
                    session.close()

        # Return a success message if everything is processed successfully
        return "Certifications stored successfully!"

    except Exception as exception:
        print(f"An exception occurred: {str(exception)}")
        raise exception


def store_course_category():
    try:
        url = 'https://fluid.talentlms.com/api/v1/courses'

        auth = requests.auth.HTTPBasicAuth(API_KEY, '')

        response = requests.get(url, auth=auth)
        response.raise_for_status()  # Raise an HTTPError if the response status code is not 2xx

        courses_data = response.json()

        # Create a database connection
        connection = databseConnection.get_connection()
        cursor = connection.cursor()

        for course_data in courses_data:
            # Extract course information from the response
            course_id = course_data['id']
            category_id = course_data['category_id']

            # Create a cursor
            cursor = connection.cursor()

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

            # Commit the changes
            connection.commit()

            # Close the cursor
            cursor.close()

        # Close the database connection
        connection.close()

        return "course_category stored successfully!"
    except Exception as exception:
        print(str(exception))
        raise exception


def store_groups(API_KEY):
    try:
        url = 'https://fluid.talentlms.com/api/v1/groups'
        auth = requests.auth.HTTPBasicAuth(API_KEY, '')

        response = requests.get(url, auth=auth)

        # Raise an HTTPError if the response status code is not 2xx
        response.raise_for_status()

        groups_data = response.json()

        for group_data in groups_data:
            # Extract group information from the response
            group_id = group_data['id']
            name = group_data['name']
            description = group_data['description']
            price = float(group_data['price'].replace('&#36;', ''))  # Convert to float
            key_column = group_data['key']
            max_redemptions = group_data['max_redemptions']
            redemptions_sofar = group_data['redemptions_sofar']
            belongs_to_branch = group_data['belongs_to_branch']

            # Insert the group data into the database
            insert_group_data(
                group_id, name, description, price, key_column, max_redemptions, redemptions_sofar, belongs_to_branch)

        return "Groups stored successfully!"
    except Exception as exception:
        return str(exception)


def insert_group_data(group_id, name, description, price, key_column, max_redemptions, redemptions_sofar,
                      belongs_to_branch):
    # Create a Group object and insert it into the database
    group = Group(
        id=group_id,
        name=name,
        description=description,
        price=price,
        key_column=key_column,
        max_redemptions=max_redemptions,
        redemptions_sofar=redemptions_sofar,
        belongs_to_branch=belongs_to_branch
    )

    db.session.merge(group)  # Use merge to handle duplicate keys
    db.session.commit()


def store_group_courses(API_KEY):
    try:
        url = 'https://fluid.talentlms.com/api/v1/groups'
        auth = requests.auth.HTTPBasicAuth(API_KEY, '')

        response = requests.get(url, auth=auth)

        # Raise an HTTPError if the response status code is not 2xx
        response.raise_for_status()

        groups_data = response.json()

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
                # Insert the group course data into the database
                insert_group_course_data(group_id, course_id)
            else:
                for course in courses:
                    course_id = course['id']
                    # Insert the group course data into the database
                    insert_group_course_data(group_id, course_id)

        return "group_has_courses stored successfully!"
    except Exception as exception:
        return str(exception)


def insert_group_course_data(group_id, course_id):
    # Create a GroupCourse object and insert it into the database
    group_course = GroupCourse(
        Group_id=group_id,
        Course_id=course_id if course_id is not None else None  # Set to None if course_id is None
    )

    db.session.merge(group_course)  # Use merge to handle duplicate keys
    db.session.commit()


def retrieve_and_store_quiz_results():
    # Define your xAPI endpoint and authentication
    endpoint = "https://lmsvisualization.lrs.io/xapi/"
    auth = "Basic " + b64encode("binnom:jojeba".encode()).decode()

    # Define the query parameters to filter statements by verbs (passed and failed)
    passed_parameters = {
        "verb": "http://adlnet.gov/expapi/verbs/passed"
    }

    failed_parameters = {
        "verb": "http://adlnet.gov/expapi/verbs/failed"
    }

    # Send a GET request to retrieve xAPI statements with the "passed" verb
    passed_response = requests.get(endpoint + "statements", params=passed_parameters, headers={"Authorization": auth})

    # Send a GET request to retrieve xAPI statements with the "failed" verb
    failed_response = requests.get(endpoint + "statements", params=failed_parameters, headers={"Authorization": auth})

    if passed_response.status_code == 200 and failed_response.status_code == 200:
        passed_statements = passed_response.json()["statements"]
        failed_statements = failed_response.json()["statements"]

        all_statements = {
            "passed_statements": passed_statements,
            "failed_statements": failed_statements
        }

        for statement in all_statements['passed_statements'] + all_statements['failed_statements']:
            actor = statement["actor"]
            object_js = statement["object"]
            definition = object_js["definition"]

            if "name" in definition:
                name = definition["name"]
                if "und" in name:
                    course_name = name["und"].replace(" - Quiz", "").replace(" - Quizz", "")
                else:
                    course_name = "Unknown"
            else:
                course_name = "Unknown"

            user_name = actor["name"]

            # Retrieve user and course objects using SQLAlchemy
            user = User.query.filter(func.lower(User.first_name) == func.lower(user_name)).first()
            course = Course.query.filter(func.lower(Course.name) == func.lower(course_name)).first()

            if user and course:
                # Extract the stored value and verb from the JSON statement
                timestamp_str = statement.get("timestamp")
                createdAt = datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S.%fZ")
                verb = statement["verb"]["display"]["en-US"]
                score = statement.get("result", {}).get("score", {}).get("raw")
                total_max = statement.get("result", {}).get("score", {}).get("max")

                # Insert or update data into the Quizz table
                quiz = Quizz.query.filter_by(quizz_name=course_name).first()
                if quiz is None:
                    quiz = Quizz(quizz_name=course_name, createdAt=createdAt)
                    db.session.add(quiz)
                else:
                    quiz.createdAt = createdAt

                # Insert or update data into the QuizzUser table
                quiz_user = QuizzUser.query.filter_by(
                    quizz_name=course_name,
                    user_id=user.user_id,
                    course_id=course.id
                ).first()
                if quiz_user is None:
                    quiz_user = QuizzUser(
                        quizz_name=course_name,
                        user_id=user.user_id,
                        score=score,
                        status=verb,
                        total_max=total_max,
                        course_id=course.id
                    )
                    db.session.add(quiz_user)
                else:
                    quiz_user.score = score
                    quiz_user.status = verb
                    quiz_user.total_max = total_max

        # Commit changes to the database
        db.session.commit()

        return jsonify(all_statements)
    else:
        return jsonify({"error": "Failed to retrieve quiz results"}), max(passed_response.status_code,
                                                                          failed_response.status_code)


def retrieve_and_store_tests(course_id, API_KEY, db):
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

                # Create Quizz record
                quizz = Quizz(quizz_name=test_datas['test_name'], course_id=course_id, createdAt=datetime.utcnow())
                db.session.add(quizz)
                db.session.commit()

                # Create QuizzUser record
                quizz_user = QuizzUser(quizz_id=quizz.quizz_id, user_id=user_id, score=float(test_datas['score']),
                                       status=test_datas['completion_status'])
                db.session.add(quizz_user)
                db.session.commit()

                quiz_result = {
                    "user_id": user_id,
                    "test_name": test_datas['test_name'],
                    "score": test_datas['score'],
                    "status": test_datas['completion_status']
                }

                quiz_results.append(quiz_result)

        return quiz_results

    except Exception as exception:
        print(f"Exception: {str(exception)}")
        raise exception
