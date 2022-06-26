from flask import Flask, jsonify, request
from src.utils.matcher import NLP
import contextualSpellCheck

app= Flask(__name__)

@app.route("/", methods=["GET"])
def hello_world():
    return jsonify("Hola mundo!")

@app.route("/spelling", methods=["POST"])
def spelling_checker():
    contextualSpellCheck.add_to_pipe(NLP)
    doc = NLP(request.get_json()["data"])
    return jsonify(
        {
            "performed_spell_check": doc._.performed_spellCheck,
            "result": doc._.outcome_spellCheck
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

@app.route("/one_verb", methods=["POST"])
def one_verb_checker():
    doc = NLP(request.get_json()["data"])
    verbs = [token.text for token in doc if token.pos_ == "VERB"] 
    return jsonify(
        {'has_one_verb': True if len(verbs) == 1 else False, 
        'verbs': verbs
        }
    )

@app.route("/adj_and_adv", methods=["POST"])
def adjectives_and_adverbs_checker():
    doc = NLP(request.get_json()["data"])
    adjectives = [token.text for token in doc if token.pos_ == "ADJ"]
    adverbs = [token.text for token in doc if token.pos_ == "ADV"]
    return jsonify(
        {'adjectives': adjectives,
        'adverbs' : adverbs
        }
    )

if __name__=='__main__':
    app.run()
    