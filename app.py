from flask import Flask, jsonify, request
from src.endpoints.spelling_checker import SpellingChecker

app= Flask(__name__)

@app.route("/", methods=["GET"])
def hello_world():
    return jsonify("Hola mundo!")

@app.route("/spelling", methods=["POST"])
def spelling_checker():
    checker = SpellingChecker(request.get_json()["data"])
    return jsonify(
        {
            "result": checker.check()
        }
    )

@app.route("/passive_voice", methods=["POST"])
def passive_voice_checker():
    
    return jsonify(
        {"Warn": "impelementar"}
    )

@app.route("/null_subject", methods=["POST"])
def null_subject_checker():
    return jsonify(
        {"Warn": "impelementar"}
    )

if __name__=='__main__':
    app.run()
    