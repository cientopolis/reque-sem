from flask import Flask, jsonify, request
from src.functions import *
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app)
@app.route("/spelling", methods=["POST"])
def spelling():
    return jsonify(
        diccion(request.get_json()["texto"])
    )

@app.route("/passive_voice", methods=["POST"])
def passive_voice_checker():
    return jsonify(
        passive_voice(request.get_json()["data"])
    )

@app.route("/null_subject", methods=["POST"])
def null_subject_checker():
    return jsonify(
        null_subjectOracion(request.get_json()["data"])
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

def agregarElementos(arr,elem):
    #lo unico que hace es fucionar los arreglos de cosas marcadas
    #nada interesante por aca...
    if not elem:
        return arr
    for i in elem:
        arr.append(i)
    return arr
@app.route("/check_all", methods=["POST"])
def check_all_checker():
    obtenido=check_all(request.get_json()["texto"])
    reglas=[]
    #reglas=agregarElementos(reglas,obtenido["spelling_checker"])
    reglas=agregarElementos(reglas,obtenido["adjectives_and_adverbs"])
    reglas=agregarElementos(reglas,obtenido["one_verb"])
    #reglas=agregarElementos(reglas,obtenido["passive_voice"])
    return jsonify(
        reglas,
    )

if __name__ == '__main__':
    app.run()
    
