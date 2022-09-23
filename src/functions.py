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

def buscar_dependencia(doc, dep):
    inicio = 0
    for token in doc:
        if token.dep_ != dep:
            inicio += len(token.text)
            if token.pos_ != "PUNCT":
                inicio += 1
        else:
            return inicio + 1

def passive_voice(data):
    try:
        doc = NLP(data)
    except:
        return []
    reglas = []
    
    matcher = Matcher(NLP.vocab)
    pattern = [{"DEP": "aux"}, {"DEP": "ROOT"}]
    matcher.add("PASSIVE VOICE", [pattern])
    matches = matcher(doc)
    
    if len(matches) >= 1:
        posInicio = 0
        posFin = 0
        for token in doc:
            if token.dep_ == "aux":
                posInicio = buscar_dependencia(doc, "aux")
            if token.dep_ == "ROOT":
                posFin = buscar_dependencia(doc, "ROOT") + len(token.text) - 1
        regla = {}
        regla["texto"] = o
        regla["Razon"] = "voz pasiva"
        regla["OP1"] = ["Use un verbo en voz activa", " ", posInicio, posFin]
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
    reglas=[]
    if null_subject(data)["has_null_subject"]:
        regla = {}
        regla["Razon"] = "Oracion sin sujeto"
        regla["OP1"] = ["Eliminar ", " ", 0, 0]
        regla["tipo"] = "general"
        reglas.append(regla)
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
