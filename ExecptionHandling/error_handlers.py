from flask import jsonify


def handle_request_exception(error):
    response = jsonify(message=f"Error occurred while fetching data from TalentLMS API: {str(error)}")
    response.status_code = 500
    return response


def handle_http_exception(error):
    response = jsonify(message=f"HTTP Error occurred: {str(error)}")
    response.status_code = 500
    return response


def handle_connection_exception(error):
    response = jsonify(message=f"Connection Error occurred: {str(error)}")
    response.status_code = 500
    return response


def handle_mysql_exception(error):
    response = jsonify(message=f"MySQL Error occurred: {str(error)}")
    response.status_code = 500
    return response


def handle_unexpected_exception(error):
    response = jsonify(message=f"An unexpected error occurred: {str(error)}")
    response.status_code = 500
    return response
