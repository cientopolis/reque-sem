from flask import Flask, jsonify, request
from src.utils.matcher import NLP
import contextualSpellCheck
from spacy.matcher import Matcher

app= Flask(__name__)

@app.route("/", methods=["GET"])
def hello_world():
    return jsonify("Hola mundo!")

@app.route("/spelling", methods=["POST"])
def spelling_checker():
    contextualSpellCheck.add_to_pipe(NLP)
    doc = NLP(request.get_json()["data"])
    NLP.remove_pipe("contextual spellchecker")
    return jsonify(
        {
            "performed_spell_check": doc._.performed_spellCheck,
            "result": doc._.outcome_spellCheck,
            "errors": str(doc._.suggestions_spellCheck)
        }
    )

@app.route("/passive_voice", methods=["POST"])
def passive_voice_checker():
    matcher = Matcher(NLP.vocab)
    pattern = [{"DEP": "auxpass"}, {"DEP": {"IN": ["neg", "advmod"]}, "OP": "*"}, {"DEP": "ROOT"}]
    matcher.add("PASSIVE VOICE", [pattern])
    pattern = [{"DEP": "agent"}, {"DEP": {"IN": ["det", "amod", "compound"]}, "OP": "*"}, {"DEP": "pobj"}]
    matcher.add("AGENT OF PASSIVE", [pattern])
    pattern = [{"DEP": {"IN": ["det", "amod", "compound"]}, "OP": "*"}, {"DEP": "nsubj"}]
    matcher.add("AGENT OF ACTIVE", [pattern])

    def findPassives(doc):
        result = ""
        if len([token.text for token in doc if token.dep_ == "auxpass"]) >= 1:
            matches = matcher(doc)
            for match_id, start, end in matches:
                string_id = NLP.vocab.strings[match_id]
                if (string_id == "PASSIVE VOICE"):
                    span = doc[start:end]
                    result = span.text
        return result

    def findAgent(passive, doc):
        result = ""
        matches = matcher(doc)
        for match_id, start, end in matches:
            string_id = NLP.vocab.strings[match_id]
            if (string_id == "AGENT OF PASSIVE" or string_id == "AGENT OF ACTIVE"):
                span = doc[start:end]
                result = span.text
        return result

    doc = NLP(request.get_json()["data"])
    passive = findPassives(doc)
    agent = findAgent(passive, doc)
    return jsonify(
            {
            'has_passive_voice': True if passive != "" else False,
            'passive_verb:': passive,
            'has_agent': True if agent != "" else False,
            'agent': agent
            }
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
    
