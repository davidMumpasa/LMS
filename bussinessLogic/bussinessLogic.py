from flask import Flask, render_template
from flask import Flask, request
import requests

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World!'


def post_to_lrs(endpoint_url, json_statement, authkey):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'aRh1ck3Zc2LaGKAqHqBTecRTfZb9pH',
        'X-Experience-API-Version': '1.0.1'
    }

    response = requests.post(endpoint_url, headers=headers, json=json_statement)
    return response.text


# Example usage
endpoint_url = "http://yourdomain.talentlms.com/tcapi/"
json_statement = {
    "actor": {
        "mbox": "david@fluidintellect.com",
        "name": "david ebula"
    },
    "verb": {
        "id": "http://example.com/verbs/completed",
        "display": {
            "en-US": "completed"
        }
    },
    "object": {
        "id": "https://fluid.talentlms.com/plus/my/courses/201/units/3022",
        "definition": {
            "name": {
                "en-US": "Module 1"
            }
        }
    }
}
authkey = "your_auth_key"

response_text = post_to_lrs(endpoint_url, json_statement, authkey)
print(response_text)

if __name__ == '__main__':
    app.run(debug=True)
