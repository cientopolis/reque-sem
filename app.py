from flask import Flask, jsonify, request
from src.endpoints.spelling_checker import SpellingChecker
from src.utils.matcher import NLP, SimpleMatcher

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
    doc = NLP(request.get_json()["data"])
    subjects = [token.text for token in doc if token.dep_ == "nsubj"]
    return jsonify(
        {'has_null_subject': True if subjects == [] else False, 
        'subjects': subjects}
    )

if __name__=='__main__':
    app.run()
    