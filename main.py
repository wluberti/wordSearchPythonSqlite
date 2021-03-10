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


@app.route("/")
def main(**args):
    return render_template('index.html', args = args)

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

@app.route("/word/", methods=["GET", "POST"])
def search():
    searchString = request.form['textinput'].lower()

    regexResult = searchRegex(searchString)
    charResult = searchChars(searchString)

    return render_template(
        'index.html',
        regexResult = regexResult,
        charResult = charResult,
        value = searchString
    )

def searchRegex(searchString):
    sql = f"SELECT word FROM words WHERE word LIKE '{searchString}' ORDER BY LENGTH(word), word"

    app.db.check_database(app.logger)
    resultset = app.db.execute(sql)

    results = []
    for result in resultset:
        tmp = result[0].replace(searchString, f"{searchString}")
        results.append(tmp)
    # app.logger.info(sql)
    # app.logger.info(results)

    return results

def searchChars(searchString):
    chars = re.findall('[a-z]', searchString)

    likeClause = "%' OR word LIKE '%".join(chars)
    # likeClause = "%' AND word LIKE '%".join(chars)
    sql = f"""
            SELECT word
            FROM words
            WHERE word LIKE '%{likeClause}%'
              AND LENGTH(word) > 1
              AND LENGTH(word) < 10
            ORDER BY LENGTH(word) ASC, points DESC, word ASC
            LIMIT 250
    """

    app.db.check_database(app.logger)
    resultset = app.db.execute(sql)

    results = []
    for result in resultset:
        tmp = result[0].replace(searchString, f"{searchString}")
        results.append(determineValue(tmp))

    # app.logger.info(sql)
    # app.logger.info(results)

    return results

def populate_database():
    sql = generateSql(app.dictionary)

    status = []
    try:
        status.append(app.db.execute(sql))
    except Exception as e:
        status.append(f'Error: {e}')

    return status


if __name__ == "__main__":
    # Port 80 configuration to run via docker-compose up
    app.run(host="0.0.0.0", port=80, debug=True)
