from src.utils.matcher import NLP
import contextualSpellCheck
from spacy.matcher import Matcher
from textblob import Word
from requests.structures import CaseInsensitiveDict
def buscar_palabra(doc, palabra):
    fin = 0
    for token in doc:
        fin += len(token.text)
        if token.text == palabra: #ACA HAY QUE CORTAR
            print(token)
            print(fin)
            break
        if token.pos_ != "PUNCT":
            fin += 1
    inicio = fin-len(palabra)
    return [inicio, fin]

def spelling_checker(data):
    contextualSpellCheck.add_to_pipe(NLP)
    try:
        doc = NLP(data)
    except:
        return []
    check = []
    pos = 1
    for token in doc:
        if token._.get_require_spellCheck:
            check.append({
                "Razon": "Misspelling "+str(token),
                #"Palabra": str(token),
                "OP1": [
                    "Reemplazar",
                    str(token._.get_suggestion_spellCheck),
                    pos,
                    pos + len(str(token))
                ],
                "tipo" : "general"
            })
        pos += len(str(token)) + 1
    NLP.remove_pipe("contextual spellchecker")
    return check

def passive_voice(data):
    matcher = Matcher(NLP.vocab)
    pattern = [{"DEP": "auxpass"}, {"DEP": {"IN": ["neg", "advmod"]}, "OP": "*"}, {"DEP": "ROOT"}]
    matcher.add("PASSIVE VOICE", [pattern])
    pattern = [{"DEP": "agent"}, {"DEP": {"IN": ["det", "amod", "compound"]}, "OP": "*"}, {"DEP": "pobj"}]
    matcher.add("AGENT OF PASSIVE", [pattern])

    try:
        doc = NLP(data)
    except:
        return []
    reglas = []
    if len([token.text for token in doc if token.dep_ == "auxpass"]) >= 1:
        matches = matcher(doc)
        for match_id, start, end in matches:
            string_id = NLP.vocab.strings[match_id]
            if (string_id == "PASSIVE VOICE"):
                regla = {}
                regla["Razon"] = "Passive voice"
                regla["OP1"] = ["Convert verb to active voice"," ", start, end-1]
                regla["tipo"] = "general"
                reglas.append(regla)
                if len([token.text for token in doc if token.dep_ == "agent"]) == 0:
                    regla = {}
                    regla["Razon"] = "Passive voice with null agent"
                    regla["OP1"] = ["Add an agent as subject of active clause"," ", start, end-1]
                    regla["tipo"] = "general"
                    reglas.append(regla)
            elif (string_id == "AGENT OF PASSIVE"):
                regla = {}
                regla["Razon"] = "Passive voice"
                regla["OP1"] = ["Use by-complement as subject of active clause"," ", start, end-1]
                regla["tipo"] = "general"
                reglas.append(regla)
    return reglas

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
def null_subjectOracion(data):
    inicio=0
    fin=-1
    oracion=""
    pos=0
    reglas=[]
    print("ORACION: Joa desafia las normas. No tiene sujeto? RTA: "+str(null_subject("Joa desafia las normas.")))
    for i in data:
        if i == ".":
            fin=pos
            if null_subject(oracion)["has_null_subject"]:
                regla = {}
                regla["Razon"] = "Oracion sin sujeto"
                regla["OP1"] = ["Eliminar ", " ", inicio, fin - 5]
                regla["tipo"] = "general"
                reglas.append(regla)
            oracion=""
            inicio=fin + 1 
        pos+=1
        oracion+=i
    return reglas

def one_verb(data):
    try:
        doc = NLP(data)
    except:
        return []
    verbs = [token.text for token in doc if token.pos_ == "VERB"]
    reglas = []

    for elem in verbs:
        pos = buscar_palabra(doc, elem)  # pos es una lista que tiene el caracter de inicio y de final
        if len(verbs) > 1:
            regla = {}
            regla["Razon"] = "Exceso de verbos"
            regla["OP1"] = ["Eliminar ", " ", pos[0], pos[1]]
            regla["tipo"] = "general"
            reglas.append(regla)

    return reglas


def adjectives_and_adverbs(data):
    try:
        doc = NLP(data)
    except:
        return []
    adjectives = [token.text for token in doc if token.pos_ == "ADJ"]
    adverbs = [token.text for token in doc if token.pos_ == "ADV"]
    reglas = []
    ambos = adjectives + adverbs  # ponemos adjetivos y verbos en una lista
    for elem in ambos:
        regla = {}
        pos = buscar_palabra(doc, elem)  # pos es una lista que tiene el caracter de inicio y de final
        if elem in adjectives:
            regla["Razon"] = "Es un adjetivo"
            regla["OP1"] = ["Eliminar", " ", pos[0], pos[1]] #MIRAR COMENTARIO DE BUSCAR_PALABRA
            regla["tipo"] = "general"
        else:
            regla["Razon"] = "Es un adverbio"
            regla["OP1"] = ["Eliminar", " ", pos[0], pos[1]]
            regla["tipo"] = "general"
        reglas.append(regla)

    return reglas
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

def check_all(data):
    return {
        'spelling_checker': spelling_checker(data),
        'passive_voice': passive_voice(data),
        'null_subject': null_subject(data),
        'one_verb': one_verb(data),
        'adjectives_and_adverbs': adjectives_and_adverbs(data)
    }
