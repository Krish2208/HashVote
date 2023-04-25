from flask import Flask, abort, flash, redirect, render_template, request, session
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
import blockchain
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
from os.path import join, dirname
from dotenv import load_dotenv

# Initializes a flask app
app = Flask(__name__)

# Set .env file to store the secrets
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
app.secret_key = os.environ.get("SECRET_KEY")
client_secret = os.path.join(pathlib.Path(
    __file__).parent, "client_secret.json")
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
flow = flow.Flow.from_client_secrets_file(
    client_secrets_file=client_secret,
    scopes=['https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/userinfo.profile', 'openid'],
    redirect_uri=os.environ.get("REDIRECT_URI")
)

# Initializes the Blockchain of Voters and Votes
Blockchain_votes = blockchain.Blockchain()
Blockchain_voter = blockchain.Blockchain()
Blockchain_votes.create_genesis_block()
Blockchain_voter.create_genesis_block_set()

# Connect to MongoDB
client = pymongo.MongoClient(os.environ.get("MONGO_URI"))
db = client.test

# Set the Admin IDs
admin_ids = ['ee210002065@iiti.ac.in', 'ee210002041@iiti.ac.in',
             'cse210001083@iiti.ac.in']

# Default start and end time of the elections
start_time = datetime(2021, 4, 1, 0, 0, 0, 0)
end_time = datetime(2023, 4, 2, 0, 0, 0, 0)


# Schema Rules for MongoDB
if "voters" not in db.list_collection_names():
    db.create_collection("voters")
if "positions" not in db.list_collection_names():
    db.create_collection("positions")
if "candidates" not in db.list_collection_names():
    db.create_collection("candidates")
if "branch" not in db.list_collection_names():
    db.create_collection("branch")

voter_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["email", "name", "branch"],
        "properties": {
            "email": {
                "bsonType": "string",
                "description": "must be a string and is required"
            },
            "name": {
                "bsonType": "string",
                "description": "must be a string and is required"
            },
            "branch": {
                "bsonType": "string",
                "description": "must be a string and is required"
            }
        }
    }
}
db.command("collMod", "voters", validator=voter_validator)

position_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["name", "permission"],
        "properties": {
            "name": {
                "bsonType": "string",
                "description": "must be a string and is required"
            },
            "permission": {
                "bsonType": "array",
                "description": "must be an array and is required",
                "items": {
                    "bsonType": "string",
                    "description": "must be a string and is required"
                }
            }
        }
    }
}
db.command("collMod", "positions", validator=position_validator)

candidate_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["name", "position", "uid"],
        "properties": {
            "name": {
                "bsonType": "string",
                "description": "must be a string and is required"
            },
            "position": {
                "bsonType": "string",
                "description": "must be a string and is required"
            },
            "uid": {
                "bsonType": "string",
                "description": "must be a string and is required"
            },
            "votes": {
                "bsonType": "int",
                "description": "must be an int"
            }
        }
    }
}
db.command("collMod", "candidates", validator=candidate_validator)

branch_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["name", "categories"],
        "properties": {
            "name": {
                "bsonType": "string",
                "description": "must be a string and is required"
            },
            "categories": {
                "bsonType": "array",
                "description": "must be an array and is required",
                "items": {
                    "bsonType": "string",
                    "description": "must be a string and is required"
                }
            }
        }
    }
}
db.command("collMod", "branch", validator=branch_validator)


# Function to generate random UID for the candidates
# of the given input size
def unique_id(size):
    chars = list(set(string.ascii_uppercase +
                 string.digits).difference('LIO01'))
    return ''.join(random.choices(chars, k=size))


# Wrapper function for checking if user is logged in
def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return redirect("/")
        else:
            return function()
    wrapper.__name__ = function.__name__
    return wrapper


# Wrapper function for checking if user is admin
def admin_is_required(function):
    def admin_wrap(*args, **kwargs):
        if "google_id" not in session:
            return redirect("/")
        elif session["email"] not in admin_ids:
            return redirect("/")
        else:
            return function()
    admin_wrap.__name__ = function.__name__
    return admin_wrap


# Home Page of the App
@ app.route('/')
def index():
    if "google_id" in session:
        return redirect("/role")
    return render_template('login.html')


# Route to assign the role to the user after login
@ app.route('/role')
@ login_is_required
def role():
    prev = set(Blockchain_voter.last_block.transactions)
    cur_time = datetime.now()
    voters = list(db.voters.find({}, {"_id": 0, "email": 1}))
    voter = {"email": session["email"]}
    if session["email"] in admin_ids:
        return redirect("/dashboard")
    elif voter not in voters:
        return redirect("/notvoter")
    elif cur_time < start_time or cur_time > end_time:
        return redirect("/notime")
    elif session.get("email") in prev:
        return redirect("/already")
    else:
        return redirect("/vote")


# Google Login Route
@ app.route('/login/google')
def login_google():
    authorization_url, state = flow.authorization_url()
    session['state'] = state
    x = session['state']
    session.modified = True
    return redirect(authorization_url)


# Logout the user
@ app.route("/logout")
@ login_is_required
def logout():
    session.clear()
    return redirect("/")


# Callback URL after the user is logged in from the google oauth
@ app.route('/callback')
def callback():
    flow.fetch_token(authorization_response=request.url)
    if session['state'] != request.args["state"]:
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
    return redirect("/role")


# Check if the voting is still going on or not
@ app.route('/notime')
def notime():
    cur_time = datetime.now()
    if cur_time > start_time and cur_time < end_time:
        return redirect("/")
    return render_template('notime.html')


# Check if the user is not added to the voter list
@ app.route('/notvoter')
@ login_is_required
def notvoter():
    return render_template('notvoter.html')


# Main Voting route which will check if the authenticated user has already voted or not
# After checking it will render the frontend page with all the candidates and respective positions
@ app.route('/vote')
@ login_is_required
def vote_candidate():
    prev = set(Blockchain_voter.last_block.transactions)
    if session.get("email") in prev:
        return redirect("/already")
    permission = db.voters.find_one({"email": session["email"]})['branch']
    positions = list(db.positions.find(
        {"$or": [{"permission": "all"}, {"permission": permission}]}))
    data_list = []
    for position in positions:
        pos_dict = {}
        pos_dict["id"] = position["_id"]
        pos_dict["name"] = position["name"]
        pos_dict["candidates"] = []
        candidates = list(db.candidates.find(
            {"position": str(position["_id"])}))
        for candidate in candidates:
            candidate_dict = {}
            candidate_dict["id"] = candidate["uid"]
            candidate_dict["name"] = candidate["name"]
            pos_dict["candidates"].append(candidate_dict)
        data_list.append(pos_dict)
    return render_template('voting.html', data=data_list)


# If the user has already voted they will be redirected to this URL, with an easter egg
@ app.route('/already')
@ login_is_required
def already():
    return render_template('already.html')


# After the user has voted, this page will be rendered to thank the user
@ app.route('/thanks')
@ login_is_required
def thanks():
    return render_template('thanks.html')


# Voting POST method gets the user votes and adds it into the chain and mine a new block
@ app.route('/voting', methods=['POST'])
@ login_is_required
def voting():
    prev = set(Blockchain_voter.last_block.transactions)
    data = request.form
    if session.get("email") in prev:
        return redirect('/already')
    else:
        prev.add(session.get("email"))
        Blockchain_voter.add_new_transaction(prev)
        Blockchain_voter.mine()
        votes = ""
        for key, value in data.items():
            votes += value + ","
        Blockchain_votes.add_new_transaction(
            {"mail": session.get("email"), "votes": votes})
        Blockchain_votes.mine()
    return redirect('/thanks')


# Admin homepage route
@ app.route('/dashboard')
@ admin_is_required
def dashboard():
    return render_template('dashboard.html', start=start_time, end=end_time)


# Admin positions page route, it render the frontend with all currently added positions
# It also defines a POST method which takes in the admin input for new position to add
@ app.route('/positions', methods=['GET', 'POST'])
@ admin_is_required
def get_positions():
    if request.method == 'POST':
        data = request.form
        perms = data.getlist("permission")
        if "all" in perms:
            perms = ["all"]
        position_data = {"name": data["name"], "permission": perms}
        position = db.positions.insert_one(position_data)
        uid = unique_id(6)
        db.candidates.insert_one(
            {"position": str(position.inserted_id), "name": "NOTA", "uid": uid})
        return redirect('/positions')
    positions = db.positions.find()
    pos_list = []
    for pos in positions:
        pos_list.append(pos)
    branch_list = list(db.branch.find())
    return render_template('positions.html', positions=pos_list, branch=branch_list)


# Admin candidates page route, it render the frontend with all currently added candidates
# It also defines a POST method which takes in the admin input for new candidates to add
@ app.route('/candidates', methods=['GET', 'POST'])
@ admin_is_required
def get_candidates():
    if request.method == 'POST':
        data = request.form
        uid = unique_id(6)
        candidate_data = {
            "position": data["position"], "name": data["name"], "uid": uid}
        db.candidates.insert_one(candidate_data)
        return redirect('/candidates')
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


# Admin voters page route, it render the frontend with all currently added voters
# It also defines a POST method which takes in the admin input for new voter to add
@ app.route('/voters', methods=['GET', 'POST'])
@ admin_is_required
def get_voters():
    if request.method == 'POST':
        data = request.form
        voter_data = {"name": data["name"], "email": data["email"],
                      "branch": data["branch"]}
        db.voters.insert_one(voter_data)
        return redirect('/voters')
    voters_list = list(db.voters.find())
    branch_list = list(db.branch.find())
    return render_template('voters.html', voters=voters_list, branch=branch_list)


# Admin branch page route, it render the frontend with all currently added branch and categories in each
# It also defines a POST method which takes in the admin input for new branch to add
@ app.route('/branch', methods=['GET', 'POST'])
@ admin_is_required
def branch():
    if request.method == 'POST':
        data = request.form
        db.branch.insert_one({"name": data["name"], "categories": []})
    return render_template('branch.html', branches=list(db.branch.find()))


# It defines a POST method which takes in the admin input for new category to add
@ app.route('/category', methods=['POST'])
@ admin_is_required
def category():
    data = request.form
    db.branch.update_one({"_id": ObjectId(data["branch"])}, {
                         "$push": {"categories": data["category"]}})
    return redirect('/branch')


# It also defines a POST method which takes in the admin input for deleting an already added position
@ app.route('/delete/position/<id>', methods=['post'])
def delete_position(id):
    if "google_id" not in session:
        return redirect('/')
    elif session["email"] not in admin_ids:
        return abort(403)
    db.candidates.delete_many({"position": id})
    db.positions.delete_one({"_id": ObjectId(id)})
    return redirect('/positions')


# It also defines a POST method which takes in the admin input for deleting an already added candidate
@ app.route('/delete/candidate/<id>', methods=['post'])
def delete_candidate(id):
    if "google_id" not in session:
        return redirect('/')
    elif session["email"] not in admin_ids:
        return abort(403)
    db.candidates.delete_one({"_id": ObjectId(id)})
    return redirect('/candidates')


# It also defines a POST method which takes in the admin input for deleting an already added voter
@ app.route('/delete/voter/<id>', methods=['post'])
def delete_voter(id):
    if "google_id" not in session:
        return redirect('/')
    elif session["email"] not in admin_ids:
        return abort(403)
    db.voters.delete_one({"_id": ObjectId(id)})
    return redirect('/voters')


# It also defines a POST method which takes in the admin input for deleting an already added category
@ app.route('/delete/category/<id>/<category>', methods=['post'])
def delete_category(id, category):
    if "google_id" not in session:
        return redirect('/')
    elif session["email"] not in admin_ids:
        return abort(403)
    db.branch.update_one({"_id": ObjectId(id)}, {
                         "$pull": {"categories": category}})
    return redirect('/branch')


# It also defines a POST method which takes in the admin input for editing an already added voter
@ app.route('/edit/voter/<id>', methods=['post'])
def edit_voter(id):
    if "google_id" not in session:
        return redirect('/')
    elif session["email"] not in admin_ids:
        return abort(403)
    data = request.form
    db.voters.update_one({"_id": ObjectId(id)}, {"$set": {
                         "name": data["name"], "email": data["email"], "branch": data["branch"]}})
    return redirect('/voters')


# It defines a function to style the visualisation charts
def func(pct, allvalues):
    absolute = int(pct / 100.*np.sum(allvalues))
    return "{:.1f}%\n({:d})".format(pct, absolute)


# It defines a route for geting the visualisation charts(Currently Unintegrated)
@ app.route('/visualise')
@ admin_is_required
def visualise():
    plot_data = {}
    positions = list(db.positions.find())
    for pos in positions:
        plot_data[pos["name"]] = {}
        candidates = list(db.candidates.find({"position": str(pos["_id"])}))
        list_of_win = {}
        for candi in candidates:
            list_of_win[candi["name"]] = 5
        plot_data[pos["name"]] = list_of_win

    for pos, pos_data in plot_data.items():
        explode = []
        count = 0
        for i in range(0, len(pos_data.keys())):
            explode.append(count)
            count = count + 0.05
        plt.pie(list(pos_data.values()), autopct=lambda pct: func(pct, list(
            pos_data.values())), labels=list(pos_data.keys()), explode=explode, shadow=True)
        plt.title(pos)
        plt.savefig('./fig.png')
        plt.show()


# It defines a POST method which takes in the admin input for publishing the result
@ app.route('/publishresult', methods=['POST'])
@ admin_is_required
def publishresult():
    cur_time = datetime.now()
    if "google_id" not in session:
        return redirect('/')
    elif session["email"] not in admin_ids:
        return abort(403)
    elif cur_time > start_time and cur_time < end_time:
        flash("Voting is still going on", "danger")
        return redirect('/dashboard')
    candidates = db.candidates.find()
    candidates_map = {}
    for candidate in candidates:
        candidates_map[candidate['uid']] = 0
    Blockchain_votes.chk_result(candidates_map)
    requests = []
    for candidate_uid, votes in candidates_map.items():
        requests.append(pymongo.UpdateOne(
            {"uid": candidate_uid}, {"$set": {"votes": votes}}))
    db.candidates.bulk_write(requests)
    return redirect('/')


# It defines a method which displays result to authenticated users
@ app.route('/result')
@ login_is_required
def result():
    positions = list(db.positions.find())
    data_list = []
    for position in positions:
        candidates = list(db.candidates.find(
            {"position": str(position["_id"])}).sort("votes", -1))
        for i, candidate in enumerate(candidates):
            candidate_dict = {}
            candidate_dict["name"] = candidate["name"]
            candidate_dict["votes"] = candidate["votes"]
            candidate_dict["position"] = position["name"]
            if (i == 0):
                candidate_dict["winner"] = True
            data_list.append(candidate_dict)
    return render_template('result.html', candidates=data_list)


# It defines a POST method which takes in the admin input for defining the voting timing
@ app.route('/timeset', methods=['POST'])
@ admin_is_required
def timeset():
    if "google_id" not in session:
        return redirect('/')
    elif session["email"] not in admin_ids:
        return abort(403)
    data = request.form
    global start_time
    global end_time
    start_time = datetime.strptime(data['start'], '%Y-%m-%dT%H:%M')
    end_time = datetime.strptime(data['end'], '%Y-%m-%dT%H:%M')
    return redirect('/dashboard')


# It defines a POST method which takes in the admin input for verifing the blockchain of votes
@ app.route('/checkchain', methods=['POST'])
@ admin_is_required
def checkchain():
    verify = Blockchain_votes.check_chain()
    if verify:
        flash("Blockchain is valid", category="success")
    else:
        flash("Blockchain is invalid", category="danger")
    return redirect('/dashboard')


if __name__ == '__main__':
    app.run(port=5000, debug=True)
