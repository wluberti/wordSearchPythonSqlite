# loosly based on
# https://tutorial-academy.com/uwsgi-nginx-flask-python-sqlite-docker-example/

from database import DatabaseManager
from generateSql import generateSql, determineValue
import unidecode
import json
import os
import re
from flask import Flask, request, redirect, url_for, render_template

app = Flask(__name__)
app.db = DatabaseManager('words.db')
# app.db = DatabaseManager(':memory:')
app.dictionary = 'wordlist.txt'


@app.route("/", methods=["GET", "POST"])
def search():
    # Check if the form is filled
    if request.form:
        numberOfBlancos = 0
        result = list()

        # Get input from form in /templates/index.html, lowelcase them and strip spaces
        letterinput = request.form['letterinput'].lower().strip()
        wordinput = request.form['wordinput'].lower().strip()

        # Check input for blanco's (any non alpha character)
        for letter in letterinput:
            if not letter.isalpha():
                numberOfBlancos += 1

        # Search the database
        for databaseword in searchDatabase(letterinput, wordinput, numberOfBlancos):
            matchingLetters = checkInputAgainstDatabaseWords(letterinput, wordinput, databaseword, numberOfBlancos)

            for letter in databaseword:
                if letter not in matchingLetters:
                    break

            result.append((databaseword, determineValue(matchingLetters)))

        return render_template(
            'index.html',
            result = result,
            lettervalue = letterinput,
            wordvalue = wordinput,
        )

    return render_template('index.html')

def searchDatabase(letterinput, wordinput = '', numberOfBlancos = 0):
    """
        Returns a set (unique list) of ALL words containing ANY of the characters in {letterinput}
        If {wordinput} is set it will check the presence of that word before adding to the set
    """
    chars = set(re.findall('[a-z]', letterinput))

    if numberOfBlancos > 0:
        chars.add('_')

    likeClause = "%' OR word LIKE '%".join(chars)
    if wordinput != '':
        wordinputForSql = re.sub(r'[^a-z]', '_', wordinput)
        wordClause = f"AND word LIKE '%{wordinputForSql}%'"
    else:
        wordClause = ''

    sql = f"""
        SELECT DISTINCT word
        FROM words
        WHERE LENGTH(word) <= {len(letterinput) + len(wordinput)}
            {wordClause}
            AND (word LIKE '%{likeClause}%')
        ORDER BY LENGTH(word) DESC
    """

    app.db.check_database(app.logger)
    unfilteredWordList = app.db.execute(sql)

    results = [word[0] for word in unfilteredWordList if \
                checkInputAgainstDatabaseWords(letterinput, wordinput, word[0], numberOfBlancos) != None]

    return results

def checkInputAgainstDatabaseWords(letterinput, wordinput, databaseword, numberOfBlancos):
    combinedletters = list(letterinput) + list(wordinput)

    pattern = re.sub(r'[^a-z]', '.', wordinput)
    match = re.search(f'{pattern}', databaseword)
    if match.string not in databaseword:
        return None

    for letter in databaseword:
        if letter not in combinedletters and numberOfBlancos == 0:
            return None
        elif numberOfBlancos > 0:
            numberOfBlancos -= 1
            continue
        else:
            combinedletters.remove(letter)

    return databaseword


def populate_database():
    sql = generateSql(app.dictionary)

    status = []
    try:
        status.append(app.db.execute(sql))
    except Exception as e:
        status.append(f'Error: {e}')

    return status

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/prepare", methods=["GET"])
def prepare():
    if app.db.check_database(app.logger) and app.db.count_words() < 100:
        populate_database()
        app.logger.info('Populated database.')
        status = 'Populated database.'
    else:
        status = 'Database already prepared.'

    return render_template('index.html', status = status)

@app.route("/check", methods=["GET"])
def check():
    status = ''
    try:
        if app.db.check_database(app.logger):
            numberOfWords = app.db.count_words()
            status = f'Found {numberOfWords} records.'
    except Exception as e:
        app.logger.error(f'Error: {e}')

    return render_template('index.html', status = status)


if __name__ == "__main__":
    # Port 80 configuration to run via docker-compose up
    app.run(host="0.0.0.0", port=80, debug=True)
