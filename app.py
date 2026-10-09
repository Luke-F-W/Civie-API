"""
Main Flask application for the API. This file has all of the routes for
the api, and sets up CORS and rate limiting. there isn't much
to talk about here.
"""

from flask import Flask, Response
from flask_cors import CORS
import json
from billgetter import apibill
from votegetter import apivote
from lobbygetter import apilobby
from debategetter import apidebate
from questiongetter import apiquestion
from members import apimember
from config import dbpath
from idsearch import getmember
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import sqlite3

app = Flask(__name__)
CORS(app, origins=["http://127.0.0.1:5500", "http://127.0.0.1:5000", "https://civie.ie", "http://192.168.1.26:5500", "http://192.168.1.154:5500"])

limiter =Limiter(
    key_func =get_remote_address,
    app=app,
    default_limits= []
)

#shows members
@app.route("/API/sector/member")
@limiter.limit("10000000 per hour")
def runmembersearch():
    return apimember()

#shows bill records
@app.route("/API/sector/bill")
@limiter.limit("10000000 per hour")
def runbill():
    return apibill()

#shows vote records
@app.route("/API/sector/vote")
@limiter.limit("10000000 per hour")
def runvote():
    return apivote()

#shows lobbying records
@app.route("/API/sector/lobby")
@limiter.limit("10000000 per hour")
def runlobby():
    return apilobby()

#shows debate records
@app.route("/API/sector/debate")
@limiter.limit("10000000 per hour")
def rundebate():
    return apidebate()

#shows question records
@app.route("/API/sector/question")
@limiter.limit("10000000 per hour")
def runquestion():
    return apiquestion()

#gets bills, votes, debates, lobbying and questions for the memberid inserted
@app.route("/API/<id>")
@limiter.limit("10000000 per hour")
def runmember(id):
    return getmember(id)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)

