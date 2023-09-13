import requests
from flask import Flask, json, jsonify
from base64 import b64encode
import mysql.connector
from datetime import datetime
from database import db

app = Flask(__name__)


@app.route('/getStatements', methods=['GET'])
def get_statements():
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

    passed_statements = passed_response.json()["statements"]
    failed_statements = failed_response.json()["statements"]

    all_statements = {
        "passed_statements": passed_statements,
        "failed_statements": failed_statements
    }

    return all_statements


@app.route('/getQuizResults', methods=['GET'])
def get_quiz_results():
    # Create the initial database connection and cursor
    connection = db.get_connection()
    cursor = connection.cursor()

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

    # ... (Previous code remains the same)

    if passed_response.status_code == 200 and failed_response.status_code == 200:
        # Requests were successful
        passed_statements = passed_response.json()["statements"]
        failed_statements = failed_response.json()["statements"]

        all_statements = {
            "passed_statements": passed_statements,
            "failed_statements": failed_statements
        }

        # Iterate through all statements (passed and failed)
        for statement in all_statements['passed_statements'] + all_statements['failed_statements']:
            actor = statement["actor"]
            object_js = statement["object"]
            definition = object_js["definition"]

            # Check if "name" is present in the "definition" dictionary
            if "name" in definition:
                name = definition["name"]
                # Check if "und" is present in the "name" dictionary
                if "und" in name:
                    # Remove "- Quiz" or "- Quizz" from the course name
                    course_name = name["und"].replace(" - Quiz", "").replace(" - Quizz", "")
                else:
                    course_name = "Unknown"
            else:
                course_name = "Unknown"

            user_name = actor["name"]

            # Define the SQL query to retrieve user_id based on user_name
            sql_query = "SELECT user_id FROM user WHERE first_name = %s"
            sql_query2 = "SELECT id FROM course WHERE name = %s"

            # Execute the SQL query
            cursor.execute(sql_query, (user_name,))
            # Fetch the result (user_id)
            user_id = cursor.fetchone()

            # Fetch all results of the first query before executing the second query
            cursor.fetchall()

            cursor.execute(sql_query2, (course_name,))
            # Fetch the result (course_id)
            course_id = cursor.fetchone()

            user_id = user_id[0] if user_id else None
            course_id = course_id[0] if course_id else None

            # Extract the stored value and verb from the JSON statement
            timestamp_str = statement.get("timestamp")

            # Convert the timestamp string to a datetime object
            createdAt = datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S.%fZ")
            verb = statement["verb"]["display"]["en-US"]
            score = statement.get("result", {}).get("score", {}).get("raw")
            total_max = statement.get("result", {}).get("score", {}).get("max")

            # Insert data into the quizz table
            insert_quiz_query = """
                INSERT INTO quizz (quizz_name, createdAt)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE createdAt = VALUES(createdAt)
            """
            quiz_values = (course_name, createdAt)

            cursor.execute(insert_quiz_query, quiz_values)

            select_existing_data_query3 = """
                SELECT quizz_name, user_id, course_id, score, status, total_max
                FROM quizz_has_user
                WHERE quizz_name = %s AND user_id = %s AND course_id = %s
            """

            # Execute the query to retrieve existing data
            cursor.execute(select_existing_data_query3, (course_name, user_id, course_id))
            existing_data = cursor.fetchone()

            print("-----------------------------------------------")
            print(existing_data)

            if existing_data:
                # Unpack the values
                existing_score, existing_status, existing_total_max = existing_data[-1]
                if (
                        score != existing_score
                        or verb != existing_status
                        or total_max != existing_total_max
                ):
                    # Data has changed, update the existing row
                    update_existing_data_query = """
                        UPDATE quizz_has_user
                        SET score = %s, status = %s, total_max = %s
                        WHERE quizz_name = %s AND user_id = %s AND course_id = %s
                    """
                    cursor.execute(
                        update_existing_data_query,
                        (score, verb, total_max, course_name, user_id, course_id),
                    )
            else:
                # Handle the case where existing_data doesn't have enough values
                # Insert a new row with the new data
                insert_new_data_query = """
                    INSERT INTO quizz_has_user (quizz_name, user_id, score, status, total_max, course_id)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(
                    insert_new_data_query,
                    (course_name, user_id, score, verb, total_max, course_id),
                )

            # Commit changes to the database
            connection.commit()

        # Return both sets of users
        return jsonify(all_statements)
    else:
        # Handle errors
        return jsonify({"error": "Failed to retrieve quiz results"}), max(passed_response.status_code,
                                                                          failed_response.status_code)


if __name__ == '__main__':
    app.run(debug=True)
