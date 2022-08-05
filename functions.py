from src.utils.matcher import NLP
import contextualSpellCheck
from spacy.matcher import Matcher

def spelling_checker(data):
    contextualSpellCheck.add_to_pipe(NLP)
    doc = NLP(data)
    NLP.remove_pipe("contextual spellchecker")
    return {
        "performed_spell_check": doc._.performed_spellCheck,
        "result": doc._.outcome_spellCheck,
        "errors": str(doc._.suggestions_spellCheck)
    }

def passive_voice(data):
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

    doc = NLP(data)
    passive = findPassives(doc)
    agent = findAgent(passive, doc)
    return {
        'has_passive_voice': True if passive != "" else False,
        'passive_verb:': passive,
        'has_agent': True if agent != "" else False,
        'agent': agent
    }

def null_subject(data):
    doc = NLP(data)
    subjects = [token.text for token in doc if token.dep_ == "nsubj"]
    return {
        'has_null_subject': True if subjects == [] else False, 
        'subjects': subjects
    }

def one_verb(data):
    doc = NLP(data)
    verbs = [token.text for token in doc if token.pos_ == "VERB"] 
    return {
        'has_one_verb': True if len(verbs) == 1 else False, 
        'verbs': verbs
    }

def adjectives_and_adverbs(data):
    doc = NLP(data)
    adjectives = [token.text for token in doc if token.pos_ == "ADJ"]
    adverbs = [token.text for token in doc if token.pos_ == "ADV"]
    return {
        'adjectives': adjectives,
        'adverbs' : adverbs
    }

def check_all(data):
    return {
        'spelling_checker': spelling_checker(data),
        'passive_voice': passive_voice(data),
        'null_subject': null_subject(data),
        'one_verb': one_verb(data),
        'adjectives_and_adverbs': adjectives_and_adverbs(data)
    }
