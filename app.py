from flask import Flask, request, jsonify, render_template, redirect, url_for
import json
import os

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    def load_dotenv():
        return False

import pymongo

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, 'data.json')

app = Flask(__name__)

# --- MongoDB Atlas connection (used by Task 2) ---
MONGO_URI = os.getenv("MONGO_URI")
_collection = None


# Connect lazily so a bad/missing URI surfaces as a form error instead of a crash at startup.
def get_collection():
    global _collection
    if _collection is None:
        if not MONGO_URI or "<" in MONGO_URI:
            raise RuntimeError(
                "MONGO_URI is not set to a real Atlas connection string. "
                "Edit the .env file in this folder."
            )
        client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        _collection = client.test['Flask']
    return _collection


# ----------------------------------------------------------------------
# Task 1: JSON API route
# Reads the list stored in the backend file (data.json) and returns it.
# ----------------------------------------------------------------------
@app.route('/api')
def api():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return jsonify(data)


# ----------------------------------------------------------------------
# Task 2: Frontend form backed by MongoDB Atlas
# GET  -> show the form
# POST -> insert into Atlas; redirect on success, show error on the same page
# ----------------------------------------------------------------------
@app.route('/', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        try:
            form_data = dict(request.form)
            get_collection().insert_one(form_data)
            return redirect(url_for('success'))
        except Exception as e:
            return render_template('form.html', error=str(e))
    return render_template('form.html')


@app.route('/success')
def success():
    return render_template('success.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
