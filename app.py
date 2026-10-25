"""
Main Flask application for the API. This file has all of the routes for
the api, and sets up CORS and rate limiting. there isn't much
to talk about here.
"""
from flask import Flask
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.middleware.proxy_fix import ProxyFix
from billgetter import apibill
from votegetter import apivote
from lobbygetter import apilobby
from debategetter import apidebate
from questiongetter import apiquestion
from compositiongetter import apicomposition
from lobbyistgetter import apilobbyist
from constituencygetter import apiconstituency
from members import apimember
from idsearch import getmember
from partygetter import apiparty
from config import RATE_LIMIT

app = Flask(__name__)

app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1)
CORS(app, origins=[
    "https://civie.ie",
    "https://www.civie.ie",
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "http://192.168.128.150:5500",
])

limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=[],
    storage_uri="memory://",
)

# shows members
@app.route("/API/sector/member")
@limiter.limit(RATE_LIMIT)
def runmembersearch():
    return apimember()

# shows bill records
@app.route("/API/sector/bill")
@limiter.limit(RATE_LIMIT)
def runbill():
    return apibill()

# shows vote records
@app.route("/API/sector/vote")
@limiter.limit(RATE_LIMIT)
def runvote():
    return apivote()

# shows lobbying records
@app.route("/API/sector/lobby")
@limiter.limit(RATE_LIMIT)
def runlobby():
    return apilobby()

# shows debate records
@app.route("/API/sector/debate")
@limiter.limit(RATE_LIMIT)
def rundebate():
    return apidebate()

# shows question records
@app.route("/API/sector/question")
@limiter.limit(RATE_LIMIT)
def runquestion():
    return apiquestion()

# gets bills, votes, debates, lobbying and questions for the memberid inserted
@app.route("/API/<id>")
@limiter.limit(RATE_LIMIT)
def runmember(id):
    return getmember(id)

#shows every party currently in the dail, if not in dail they wont be here
@app.route("/API/sector/party")
@limiter.limit(RATE_LIMIT)
def runparty():
    return apiparty()

# for constituency map
@app.route("/API/sector/constituency")
def runconstituency():
    return apiconstituency()

# gets party numbers
@app.route("/API/sector/index")
@limiter.limit(RATE_LIMIT)
def runindex():
    return apicomposition()

# shows lobbyists
@app.route("/API/sector/lobbyist")
@limiter.limit(RATE_LIMIT)
def runlobbyist():
    return apilobbyist()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
