from spellchecker import SpellChecker

class SpellingChecker:
    def __init__(self, text):
        self.text= text
        self.spell = SpellChecker()

    def check(self):
        corrections = {}
        for word in self.text.split(" "):
            print(self.spell.correction(word))
            if  self.spell.correction(word) != word:
                corrections[word]=  self.spell.correction(word)
        return corrections
        
