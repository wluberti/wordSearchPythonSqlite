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
    if request.form:
        # Prepare result dictionary
        result = list()

        # Get input from form in /templates/index.html
        letterinput = request.form['letterinput'].lower()
        wordinput = request.form['wordinput'].lower()

        # Search the database
        for word in searchDatabase(letterinput, wordinput):
            # Return all the matching letters between {letterinput} and {word}
            matchingLetters = checkInputAgainstDatabase(letterinput, wordinput, word)

            # app.logger.info(word)
            for letter in word:
                if letter not in matchingLetters:
                    break

            # Populate the result
            result.append((word, determineValue(matchingLetters)))

        # app.logger.info(result)

        return render_template(
            'index.html',
            result = result,
            lettervalue = letterinput,
            wordvalue = wordinput,
        )

    return render_template('index.html')

def searchDatabase(letterinput, wordinput = ''):
    """
        Returns a set (unique list) of ALL words containing ANY of the characters in {letterinput}
        If {wordinput} is set it will check the presence of that word before adding to the set
    """
    chars = re.findall('[a-z]', letterinput)

    likeClause = "%' OR word LIKE '%".join(set(chars))
    if wordinput != '':
        wordClause = f"AND word LIKE '%{wordinput}%'"
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
                checkInputAgainstDatabase(letterinput, wordinput, word[0]) != None]

    return results

def checkInputAgainstDatabase(letterinput, wordinput, databaseword):
    letterinput = list(letterinput) + list(wordinput)

    if wordinput not in databaseword:
        return None

    for letter in databaseword:
        if letter not in letterinput:
            return None
        else:
            letterinput.remove(letter)

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
