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
from members import apimember
from idsearch import getmember
from config import RATE_LIMIT

app = Flask(__name__)

app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1)
CORS(app, origins=["https://civie.ie"])

limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=[],
    application_limits=[RATE_LIMIT],
    storage_uri="memory://",
)

# shows members
@app.route("/API/sector/member")
def runmembersearch():
    return apimember()

# shows bill records
@app.route("/API/sector/bill")
def runbill():
    return apibill()

# shows vote records
@app.route("/API/sector/vote")
def runvote():
    return apivote()

# shows lobbying records
@app.route("/API/sector/lobby")
def runlobby():
    return apilobby()

# shows debate records
@app.route("/API/sector/debate")
def rundebate():
    return apidebate()

# shows question records
@app.route("/API/sector/question")
def runquestion():
    return apiquestion()

# gets bills, votes, debates, lobbying and questions for the memberid inserted
@app.route("/API/<id>")
def runmember(id):
    return getmember(id)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
