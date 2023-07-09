#La idea de este archivo es mostrarles un ejemplo que funciona con la app y que lo tengan de referencia
#La app llama a una funcion principal en /reglas y esta se encarga de llamar a cada funcion regla
#para luego devolver un conjunto de cosas para marcar. Ver abajo para mas detalles!
# :D
from src.functions import *
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
import re
import json
from textblob import Word
from requests.structures import CaseInsensitiveDict
import spacy
from src.functions import passive_voice_checker as pvc
from src.functions import adjectives_and_adverbs_checker as aac
from spacy.matcher import Matcher
NLP = spacy.load("en_core_web_trf")
app= Flask(__name__)
CORS(app)
@app.route("/", methods=["GET"])
def hello_world():
    return jsonify("Hola mundo!")
@cross_origin
@app.route("/one_verb", methods=["POST"])
def one_verb_checker():
    doc = NLP(request.get_json()["data"])
    verbs = [token.text for token in doc if token.pos_ == "VERB"] 
    return jsonify(
        {'has_one_verb': True if len(verbs) == 1 else False, 
        'data': verbs
        }
    )
@cross_origin
@app.route("/adj_and_adv", methods=["POST"])
def adjectives_and_adverbs_checker():
    return aac(request.get_json()["data"])
    #doc = NLP(request.get_json()["data"])
    #adjectives = [token.text for token in doc if token.pos_ == "ADJ"]
    #adverbs = [token.text for token in doc if token.pos_ == "ADV"]
    #return jsonify({'data' : adverbs + adjectives})
@app.route("/dict", methods=["POST"])
def dicc():
    texto=request.get_json()["data"]
    reglas=diccion(texto)
    return jsonify(
        {
        'data' : reglas
        }
    )
@cross_origin
@app.route("/passive_voice", methods=["POST"])
def passive_voice():
    
    texto=request.get_json()["data"]
    return pvc(texto)
                       
def agregarElementos(arr,elem):
    #lo unico que hace es fucionar los arreglos de cosas marcadas
    #nada interesante por aca...
    if not elem:
        return arr
    for i in elem:
        arr.append(i)
    return arr
@cross_origin
@app.route("/api", methods=["POST"])
def procesar():
    texto=request.get_json()["data"]
    res=SepararOraciones(texto)
    return res

def check_word_spelling(word):
    word = Word(word)
    result = word.spellcheck()
    return result
def diccion(texto):
    #Ejemplo con multiOpcion variable
    #La idea es encontrar horrores de ortografia y dar un conjunto
    #de soluciones para corregir dicho error
    palabras= texto.split()
    palabras = [palabra.lower() for palabra in palabras]
    pos=0
    reglas=[]
    for palabra in palabras:
        corr=check_word_spelling(palabra)
        if corr[0][0] != palabra:
            regla={}
            regla["Razon"]="misspeling"
            z=1 #debe empezar en 1
            for i in corr:
                regla["OP"+str(z)]= ["Reemplazar",i[0]]#Las opciones varian
                z=z+1
            regla["tipo"]= "general"
            regla["marcar"]=palabra
            reglas.append(regla)
        pos=pos+len(palabra)+1
    return reglas
if __name__=='__main__':
    app.run()
    