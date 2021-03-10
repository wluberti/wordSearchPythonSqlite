#! /usr/bin/env python3

import unidecode
from collections import Counter

def generateSql(dictionaryFile):
    """
        Generates the SQL needed to populate database.
        Retuns string with SQL
    """
    wordset = set()

    with open(dictionaryFile) as dictionary:
        data = dictionary.readlines()
        for word in data:
            # Remove any special characters and spaces
            word = unidecode.unidecode(word).strip()

            # Hack for plural words ending with _'s
            if "'s" in word: word.replace("'s", "s")

            # Skip all words that are not allowed in Scrabble
            if ' ' in word: continue
            if '.' in word: continue
            if '-' in word: continue
            if "'" in word: continue
            if "/" in word: continue
            if any(letter.isupper() for letter in word): continue
            if any(letter.isdigit() for letter in word): continue

            # Add word to set
            word, value = determineValue(word)
            if word != None:
                wordset.add((word, value))

    sql = "INSERT INTO words (word, points) VALUES "
    for word, value in wordset:
        sql += f'("{word}", {value}), '
    sql = sql.rstrip(', ')

    return sql

def determineValue(word):
    letterValues = {
        'a': {'value': 1, 'amount': 7},
        'b': {'value': 4, 'amount': 2},
        'c': {'value': 5, 'amount': 2},
        'd': {'value': 2, 'amount': 5},
        'e': {'value': 1, 'amount': 18},
        'f': {'value': 4, 'amount': 2},
        'g': {'value': 3, 'amount': 3},
        'h': {'value': 4, 'amount': 2},
        'i': {'value': 2, 'amount': 4},
        'j': {'value': 4, 'amount': 2},
        'k': {'value': 3, 'amount': 3},
        'l': {'value': 3, 'amount': 3},
        'm': {'value': 3, 'amount': 3},
        'n': {'value': 1, 'amount': 11},
        'o': {'value': 1, 'amount': 6},
        'p': {'value': 4, 'amount': 2},
        'q': {'value': 10, 'amount': 1},
        'r': {'value': 2, 'amount': 5},
        's': {'value': 2, 'amount': 5},
        't': {'value': 2, 'amount': 5},
        'u': {'value': 2, 'amount': 3},
        'v': {'value': 4, 'amount': 2},
        'w': {'value': 5, 'amount': 2},
        'x': {'value': 8, 'amount': 1},
        'y': {'value': 8, 'amount': 1},
        'z': {'value': 5, 'amount': 2},
        '?': {'value': 0, 'amount': 2},
    }

    count = Counter(word)
    value = 0
    for letter in word:
        # Ignore words containing more letters than possible
        if count[letter] > letterValues[letter]['amount']:
            return (None, 0)

        value += letterValues[letter]['value']

    return (word, value)

if __name__ == "__main__":
    dictionaryFile = 'wordlist.txt'

    print(generateSql(dictionaryFile))
