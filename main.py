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
import blockchain
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

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
Blockchain_votes = blockchain.Blockchain()
Blockchain_voter = blockchain.Blockchain()
Blockchain_votes.create_genesis_block()
Blockchain_voter.create_genesis_block_set()

client = pymongo.MongoClient(
    "mongodb+srv://diwankrish17:N4lTSO9A3DJ6sRYW@cluster0.wlsbebc.mongodb.net/?retryWrites=true&w=majority")
db = client.test

admin_ids = ['ee210002041@iiti.ac.in']

start_time = datetime(2021, 4, 1, 0, 0, 0, 0)
end_time = datetime(2021, 4, 2, 0, 0, 0, 0)


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
        elif session["email"] not in admin_ids:
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
        prev = set(Blockchain_voter.last_block.transactions)
        if session["email"] in admin_ids:
            return redirect("/admin")
        elif session.get("email") in prev:
            return redirect("/already")
        else:
            return redirect("/vote")


@app.route('/vote')
@login_is_required
def vote_candidate():
    prev = set(Blockchain_voter.last_block.transactions)
    if session.get("email") in prev:
        return redirect("/already")
    positions = list(db.positions.find({}))
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
    print(data_list)
    return render_template('voting.html', data=data_list)


@app.route('/already')
def already():
    return render_template('already.html')


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


@app.route('/getchain', methods=['GET'])
def getchain():
    print(Blockchain_votes.chain[0].transactions)
    print(Blockchain_voter.chain[0].transactions)
    print(Blockchain_votes.chain[1].transactions)
    print(Blockchain_voter.chain[1].transactions)
    return redirect('/')


@app.route('/add/candidate', methods=['POST'])
def add_candidate():
    if "google_id" not in session:
        return redirect('/')
    elif session["email"] not in admin_ids:
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
    elif session["email"] not in admin_ids:
        return abort(403)
    data = request.form
    perms = data.getlist("permission")
    if "all" in perms:
        perms = ["all"]
    position_data = {"name": data["name"], "permission": perms}
    db.positions.insert_one(position_data)
    return redirect('/positions')


@app.route('/add/voter', methods=['POST'])
def add_voter():
    if "google_id" not in session:
        return redirect('/')
    elif session["email"] not in admin_ids:
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
    elif session["email"] not in admin_ids:
        return abort(403)
    positions = db.positions.find()
    pos_list = []
    for pos in positions:
        pos_list.append(pos)
    branch_list = list(db.branch.find())
    return render_template('positions.html', positions=pos_list, branch=branch_list)


@app.route('/candidates')
def get_candidates():
    if "google_id" not in session:
        return redirect('/')
    elif session["email"] not in admin_ids:
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
    elif session["email"] not in admin_ids:
        return abort(403)
    voters_list = list(db.voters.find())
    branch_list = list(db.branch.find())
    return render_template('voters.html', voters=voters_list, branch=branch_list)

@app.route('/branch', methods=['GET', 'POST'])
def branch():
    if "google_id" not in session:
        return redirect('/')
    elif session["email"] not in admin_ids:
        return abort(403)
    if request.method == 'POST':
        data = request.form
        db.branch.insert_one({"name": data["name"], "categories": []})
    print(list(db.branch.find()))
    return render_template('branch.html', branches=list(db.branch.find()))

@app.route('/category', methods=['POST'])
def category():
    if "google_id" not in session:
        return redirect('/')
    elif session["email"] not in admin_ids:
        return abort(403)
    data = request.form
    print(data)
    db.branch.update_one({"_id": ObjectId(data["branch"])}, {"$push": {"categories": data["category"]}})
    return redirect('/branch')

@app.route('/delete/position/<id>')
def delete_position(id):
    if "google_id" not in session:
        return redirect('/')
    elif session["email"] not in admin_ids:
        return abort(403)
    db.candidates.delete_many({"position": id})
    db.positions.delete_one({"_id": ObjectId(id)})
    return redirect('/positions')


@app.route('/delete/candidate/<id>')
def delete_candidate(id):
    if "google_id" not in session:
        return redirect('/')
    elif session["email"] not in admin_ids:
        return abort(403)
    db.candidates.delete_one({"_id": ObjectId(id)})
    return redirect('/candidates')


@app.route('/delete/voter/<id>')
def delete_voter(id):
    if "google_id" not in session:
        return redirect('/')
    elif session["email"] not in admin_ids:
        return abort(403)
    db.voters.delete_one({"_id": ObjectId(id)})
    return redirect('/voters')

def func(pct, allvalues):
    absolute = int(pct / 100.*np.sum(allvalues))
    return "{:.1f}%\n({:d})".format(pct, absolute)

@app.route('/visualise')
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
    # fig, axs = plt.subplots(2,2)
    # i= 0
    # j= 0
    # count= 1
    
    for pos, pos_data in plot_data.items():
        # print(pos_data)
        explode = []
        count= 0
        for i in range(0, len(pos_data.keys())):
            explode.append(count)
            count= count+ 0.05
        plt.pie(list(pos_data.values()), autopct = lambda pct: func(pct,list(pos_data.values())), labels=list(pos_data.keys()), explode= explode, shadow= True)
        plt.title(pos)
        # if(count%2==0):
        #     i=i+1
        # else:
        #     j=j+1
        # count= count+1
        plt.savefig('./fig.png')
        plt.show() 


@app.route('/result', methods=['POST'])
def result():
    if "google_id" not in session:
        return redirect('/')
    elif session["email"] not in admin_ids:
        return abort(403)
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
    return candidates_map, 200


@app.route('/timeset', methods=['POST'])
def timeset():
    if "google_id" not in session:
        return redirect('/')
    # elif session["email"] not in admin_ids:
    #     return abort(403)
    data = request.form
    print(data)
    global start_time
    global end_time
    start_time = datetime.strptime(data['start'], '%Y-%m-%dT%H:%M')
    end_time = datetime.strptime(data['end'], '%Y-%m-%dT%H:%M')
    return redirect('/dashboard')


@app.route('/dashboard')
def dashboard():
    if "google_id" not in session:
        return redirect('/')
    return render_template('dashboard.html', start=start_time, end=end_time)


if __name__ == '__main__':
    app.run(port=5000, debug=True)
