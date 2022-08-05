from flask import Flask, jsonify, request
from functions import *

app = Flask(__name__)

@app.route("/spelling", methods=["POST"])
def spelling():
    return jsonify(
        spelling_checker(request.get_json()["data"])
    )

@app.route("/passive_voice", methods=["POST"])
def passive_voice_checker():
    return jsonify(
        passive_voice(request.get_json()["data"])
    )

@app.route("/null_subject", methods=["POST"])
def null_subject_checker():
    return jsonify(
        null_subject(request.get_json()["data"])
    )

@app.route("/one_verb", methods=["POST"])
def one_verb_checker():
    return jsonify(
        one_verb(request.get_json()["data"])
    )

@app.route("/adj_and_adv", methods=["POST"])
def adjectives_and_adverbs_checker():
    return jsonify(
        adjectives_and_adverbs(request.get_json()["data"])
    )

@app.route("/check_all", methods=["POST"])
def check_all_checker():
    return jsonify(
        check_all(request.get_json()["data"])
    )

if __name__ == '__main__':
    app.run()
    
