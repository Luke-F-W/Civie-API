"""
Main Flask application for the API. This file has all of the routes for
the api, and sets up CORS and rate limiting. there isn't much
to talk about here.
"""

from flask import Flask, jsonify
from flask_cors import CORS
import json
from billgetter import apibill
from votegetter import apivote
from lobbygetter import apilobby
from debategetter import apidebate
from questiongetter import apiquestion
from config import memberss,  mainstatss
from idsearch import getmember
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
CORS(app, origins=["http://127.0.0.1:5500", "https://civie.ie"])

limiter =Limiter(
    key_func =get_remote_address,
    app=app,
    default_limits= []
)
#will be used for index on website, judt general stats
@app.route("/API/sector/index")
@limiter.limit("50 per hour")
def stats():
    with open(mainstatss, "r", encoding="utf-8") as f:
        data = json.load(f)
    return jsonify(data)

#shows all members
@app.route("/API/other/members")
@limiter.limit("100 per hour")
def member():
    with open(memberss, "r", encoding="utf-8") as f:
        data =json.load(f)
    return jsonify(data)

#shows bill records
@app.route("/API/sector/bill")
@limiter.limit("100 per hour")
def runbill():
    return apibill()
#shows vote records
@app.route("/API/sector/vote")
@limiter.limit("100 per hour")
def runvote():
    return apivote()

#shows lobbying records
@app.route("/API/sector/lobby")

@limiter.limit("100 per hour")
def runlobby():
    return apilobby()

#shows debate records
@app.route("/API/sector/debate")
@limiter.limit("100 per hour")
def rundebate():
    return apidebate()

#shows question records
@app.route("/API/sector/question")
@limiter.limit("100 per hour")
def runquestion():
    return apiquestion()

#gets bills, votes, debates, lobbying and questions for the memberid inserted
@app.route("/API/<id>")
@limiter.limit("100 per hour")
def runmember(id):
    return getmember(id)

if __name__ == "__main__":
    app.run() 
