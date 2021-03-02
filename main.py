# loosly based on
# https://tutorial-academy.com/uwsgi-nginx-flask-python-sqlite-docker-example/

from database import DatabaseManager
import unidecode
import json
import os
from flask import Flask, request, redirect, url_for, render_template

app = Flask(__name__)
app.db = DatabaseManager('words.db')
# app.db = DatabaseManager(':memory:')
app.dictionary = 'wordlist.txt'


@app.route("/")
def main(**args):
    return render_template('index.html', args = args)

@app.route('/favicon.ico')
def favicon():
    return redirect(url_for('static', filename='favicon.ico'))

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

@app.route("/close", methods=["GET"])
def close():
    try:
        app.db.close_connection()
        status = 'ok'
    except Exception as e:
        app.logger.error(f'Error: {e}')

    return render_template('index.html', status = status)

@app.route("/word/", methods=["GET", "POST"])
def search():
    searchString = request.form['textinput']
    # sql = f"SELECT word FROM words WHERE word LIKE '%{searchString}%' ORDER BY 1"
    sql = f"SELECT word FROM words WHERE word LIKE '{searchString}' ORDER BY LENGTH(word), word"

    app.db.check_database(app.logger)
    resultset = app.db.execute(sql)

    results = []
    for result in resultset:
        tmp = result[0].replace(searchString, f"{searchString}")
        results.append(tmp)
    app.logger.info(sql)

    return render_template('index.html', results = results, value = searchString)

def populate_database():
    with open(app.dictionary) as wl:
        wordset = set() # Use use to create a unique list
        data = wl.readlines()
        for word in data:
            # Remove any special characters
            word = unidecode.unidecode(word).strip()

            # Hack for plural words ending with _'s_
            if "'s" in word: word.replace("'s", "s")

            # Skip all words that are not allowed in Scrabble
            if ' ' in word: continue
            if '-' in word: continue
            if "'" in word: continue
            if any(l.isupper() for l in word): continue
            if any(l.isdigit() for l in word): continue

            # Add word to set
            wordset.add(word)

    words = "'), ('".join(wordset)
    sql = f"INSERT OR IGNORE INTO words VALUES ('{words}')"

    status = []
    try:
        status.append(app.db.execute(sql))
        # status = 'ok'
    except Exception as e:
        status.append(f'Error: {e}')

    return status


if __name__ == "__main__":
    # Port 80 configuration to run via docker-compose up
    app.run(host="0.0.0.0", port=80, debug=True)
