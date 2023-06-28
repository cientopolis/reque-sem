from src.utils.matcher import NLP
import contextualSpellCheck
from spacy.matcher import Matcher
import spacy
from textblob import Word
from requests.structures import CaseInsensitiveDict

def passive_voice_checker(texto):
    matcher = Matcher(NLP.vocab)
    pattern = [{"DEP": {"IN": ["auxpass", "aux"]}, "OP": "+"}, {"DEP": {"IN": ["neg", "advmod", "auxpass"]}, "OP": "*"}, {"DEP": {"IN": ["ROOT", "acomp"]}, "OP": "+"}]
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
        #for token in doc:
        #    print(token.text, "\t" + token.dep_, token.head.text, token.head.pos_)
        result = ""
        matches = matcher(doc)
        for match_id, start, end in matches:
            string_id = NLP.vocab.strings[match_id]
            if (string_id == "AGENT OF PASSIVE" or string_id == "AGENT OF ACTIVE"):
                span = doc[start:end]
                result = span.text
        return result

    doc = NLP(texto)
    passive = findPassives(doc)
    agent = findAgent(passive, doc)
    return (
            {
            'has_passive_voice': True if passive != "" else False,
            'passive_verb:': passive,
            'has_agent': True if agent != "" else False,
            'agent': agent
            }
        )

def null_subject(data):
    try:
        doc = NLP(data)
    except:
        return []
    subjects = [token.text for token in doc if token.dep_ == "nsubj"]
    return {
        'has_null_subject': True if subjects == [] else False, 
        'subjects': subjects
    }


def one_verb_checker(texto):
    doc = NLP(texto)
    verbs = [token.text for token in doc if token.pos_ == "VERB"] 
    return {
        'has_more_verb': False if len(verbs) == 1 else True, 
        'data': verbs
        }
    
def adjectives_and_adverbs_checker(text):
    doc = NLP(text)
    adjectives = [token.text for token in doc if token.pos_ == "ADJ"]
    adverbs = [token.text for token in doc if token.pos_ == "ADV"]
    hasAdjOrAdv = adjectives or adverbs
    return (
        {
            'hasAdjOrAdv' : hasAdjOrAdv,
            'adjectives': adjectives,
            'adverbs' : adverbs
        }
    )
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
            regla["Razon"]="Misspeling"
            z=1 #debe empezar en 1
            for i in corr:
                regla["OP"+str(z)]= ["Replace",i[0],pos,pos+len(palabra)]#Las opciones varian
                z=z+1
            regla["tipo"]= "general"
            reglas.append(regla)
        pos=pos+len(palabra)+1
    return reglas
def SepararOraciones(texto):
    fin_de_Oracion=0
    lineaActual=0
    oracion=""
    passive_voiceR=[]
    null_subjectR=[]
    one_verbR=[]
    adjectives_and_adverbsR=[]
    for i in texto:
        oracion+=i
        if i == ".":
            lineaActual=lineaActual+1
            res=null_subject(oracion)
            resVerb=one_verb_checker(oracion)
            resAdjAdv=adjectives_and_adverbs_checker(oracion)
            resPassive=passive_voice_checker(oracion)
            if res["has_null_subject"] and not resPassive["has_passive_voice"]:
                regla={}
                regla["has_null_subject"]= res["has_null_subject"]
                regla["Oracion"]=lineaActual
                null_subjectR.append(regla)
            if resVerb["has_more_verb"] and not resPassive["has_passive_voice"]:
                regla={}
                regla["has_more_verb"]= resVerb["has_more_verb"]
                regla["Oracion"]=lineaActual
                one_verbR.append(regla)
            if resAdjAdv['hasAdjOrAdv']:
                regla={}
                regla["hasAdjOrAdv"]= resAdjAdv["hasAdjOrAdv"]
                regla["Oracion"]=lineaActual
                adjectives_and_adverbsR.append(regla)
            if resPassive["has_passive_voice"]:
                regla={}
                regla["has_passive_voice"]= resPassive["has_passive_voice"]
                regla["Oracion"]=lineaActual
                passive_voiceR.append(regla)
            oracion=""
            #encontre fin de oracion
            #llamo a las funciones
            #agrego las rta al esquema de devolucion marcando la linea
            #aumento nro de line
        
    return{
        "null_subject" : null_subjectR,
        "has_more_verb" : one_verbR,
        'hasAdjOrAdv' : adjectives_and_adverbsR,
        "has_passive_voice" : passive_voiceR
    }
