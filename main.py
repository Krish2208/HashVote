from flask import Flask, abort, redirect, render_template, request, session
import os
from google.oauth2 import id_token
import pathlib
from google_auth_oauthlib import flow
from pip._vendor import cachecontrol
import google.auth.transport.requests
import requests
import pymongo
from bson import ObjectId
import string
import random

app = Flask(__name__)
app.secret_key = "hashvote"
client_secret = os.path.join(pathlib.Path(
    __file__).parent, "client_secret.json")
GOOGLE_CLIENT_ID = "659786496565-bman97c446r9loq8m36f9ju3kmnfa3g7.apps.googleusercontent.com"
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
flow = flow.Flow.from_client_secrets_file(
    client_secrets_file=client_secret,
    scopes=['https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/userinfo.profile', 'openid'],
    redirect_uri='http://localhost:5000/callback'
)

data = [
    {
        "id": "pres",
        "name": "President",
        "candidates": [
            {
              "id": "pres-1",
              "name": "Candidate 1",
            },
            {
                "id": "pres-2",
                "name": "Candidate 2",
            },
            {
                "id": "pres-3",
                "name": "Candidate 3",
            },
            {
                "id": "nota",
                "name": "NOTA",
            }
        ]
    },
    {
        "id": "vpres",
        "name": "Vice President",
        "candidates": [
            {
              "id": "vpres-1",
              "name": "Candidate 1",
            },
            {
                "id": "vpres-2",
                "name": "Candidate 2",
            },
            {
                "id": "vpres-3",
                "name": "Candidate 3",
            },
            {
                "id": "nota",
                "name": "NOTA",
            }
        ]
    },
]

client = pymongo.MongoClient(
    "mongodb+srv://diwankrish17:N4lTSO9A3DJ6sRYW@cluster0.wlsbebc.mongodb.net/?retryWrites=true&w=majority")
db = client.test


def unique_id(size):
    chars = list(set(string.ascii_uppercase +
                 string.digits).difference('LIO01'))
    return ''.join(random.choices(chars, k=size))


def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return redirect("/")
        else:
            return function()
    return wrapper


def admin_is_required(function):
    def admin_wrap(*args, **kwargs):
        if "google_id" not in session:
            return redirect("/")
        elif session["email"] not in ["cse210001034@iiti.ac.in"]:
            return redirect("/")
        else:
            return function()
    return admin_wrap


@app.route('/')
def index():
    if "google_id" in session:
        return redirect("/role")
    return render_template('login.html')


@app.route('/role')
def role():
    if "google_id" not in session:
        return redirect("/")
    else:
        if session["email"] in ["cse210001034@iiti.ac.in"]:
            return redirect("/admin")
        else:
            return redirect("/vote")


@app.route('/vote')
@login_is_required
def login():
    return render_template('voting.html', data=data)


@app.route('/login/google')
def login_google():
    authorization_url, state = flow.authorization_url()
    session['state'] = state
    session.modified = True
    return redirect(authorization_url)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route('/callback')
def callback():
    flow.fetch_token(authorization_response=request.url)
    if session["state"] != request.args["state"]:
        abort(500)  # State does not match!

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(
        session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )

    session["google_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")
    session["email"] = id_info.get("email")
    session["picture"] = id_info.get("picture")
    return redirect("/role")


@app.route('/admin')
@admin_is_required
def admin():
    return render_template('admin-template.html')


@app.route('/thanks')
def thanks():
    return render_template('thanks.html')


@app.route('/voting', methods=['POST'])
def voting():
    print(request.form)
    return redirect('/thanks')


@app.route('/add/candidate', methods=['POST'])
def add_candidate():
    if "google_id" not in session:
        return redirect('/')
    elif session["email"] not in ["cse210001034@iiti.ac.in"]:
        return abort(403)
    data = request.form
    uid = unique_id(6)
    candidate_data = {
        "position": data["position"], "name": data["name"], "uid": uid}
    db.candidates.insert_one(candidate_data)
    return redirect('/candidates')


@app.route('/add/position', methods=['POST'])
def add_position():
    if "google_id" not in session:
        return redirect('/')
    elif session["email"] not in ["cse210001034@iiti.ac.in"]:
        return abort(403)
    data = request.form
    position_data = {"name": data["name"]}
    db.positions.insert_one(position_data)
    return redirect('/positions')


@app.route('/add/voter', methods=['POST'])
def add_voter():
    if "google_id" not in session:
        return redirect('/')
    elif session["email"] not in ["cse210001034@iiti.ac.in"]:
        return abort(403)
    data = request.form
    voter_data = {"name": data["name"], "email": data["email"],
                  "branch": data["branch"], "voted": "false"}
    db.voters.insert_one(voter_data)
    return redirect('/voters')


@app.route('/positions')
def get_positions():
    if "google_id" not in session:
        return redirect('/')
    elif session["email"] not in ["cse210001034@iiti.ac.in"]:
        return abort(403)
    positions = db.positions.find()
    pos_list = []
    for pos in positions:
        pos_list.append(pos)
    return render_template('positions.html', positions=pos_list)


@app.route('/candidates')
def get_candidates():
    if "google_id" not in session:
        return redirect('/')
    elif session["email"] not in ["cse210001034@iiti.ac.in"]:
        return abort(403)
    positions = db.positions.find()
    candidates = db.candidates.find()
    pos_list = []
    for pos in positions:
        pos_list.append(pos)
    candidates_list = []
    for candidate in candidates:
        candidate['position'] = db.positions.find_one(
            {"_id": ObjectId(candidate['position'])})['name']
        candidates_list.append(candidate)
    return render_template('candidates.html', positions=pos_list, candidates=candidates_list)


@app.route('/voters')
def get_voters():
    if "google_id" not in session:
        return redirect('/')
    elif session["email"] not in ["cse210001034@iiti.ac.in"]:
        return abort(403)
    voters = db.voters.find()
    voters_list = []
    for voter in voters:
        voters_list.append(voter)
    return render_template('voters.html', voters=voters_list)


@app.route('/delete/position/<id>')
def delete_position(id):
    if "google_id" not in session:
        return redirect('/')
    elif session["email"] not in ["cse210001034@iiti.ac.in"]:
        return abort(403)
    db.candidates.delete_many({"position": id})
    db.positions.delete_one({"_id": ObjectId(id)})
    return redirect('/positions')


@app.route('/delete/candidate/<id>')
def delete_candidate(id):
    if "google_id" not in session:
        return redirect('/')
    elif session["email"] not in ["cse210001034@iiti.ac.in"]:
        return abort(403)
    db.candidates.delete_one({"_id": ObjectId(id)})
    return redirect('/candidates')


@app.route('/delete/voter/<id>')
def delete_voter(id):
    if "google_id" not in session:
        return redirect('/')
    elif session["email"] not in ["cse210001034@iiti.ac.in"]:
        return abort(403)
    db.voters.delete_one({"_id": ObjectId(id)})
    return redirect('/voters')


if __name__ == '__main__':
    app.run(port=5000, debug=True)
