"""
Main Flask application for the API. This file has all of the routes for
the api, and sets up CORS, rate limiting and caching.
"""
from flask import Flask
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
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

# Proxy configuration
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1)

# Caching configuration
app.config["CACHE_TYPE"] = "SimpleCache"
app.config["CACHE_DEFAULT_TIMEOUT"] = 300  # 5 minutes

cache = Cache(app)

# CORS configuration
CORS(app, origins=[
    "https://civie.ie",
    "https://www.civie.ie",
    "http://localhost:4321",
    "http://127.0.0.1:4321",
    "http://loadbalancer-1141809072.us-east-1.elb.amazonaws.com",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://192.168.128.150:5500",
    "https://dynamic.civie.ie",
])

# Rate limiting configuration
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=[],
    storage_uri="memory://",
)

# Shows members
@app.route("/API/sector/member")
@limiter.limit(RATE_LIMIT)
@cache.cached(timeout=3600)
def runmembersearch():
    return apimember()

# Shows bill records
@app.route("/API/sector/bill")
@limiter.limit(RATE_LIMIT)
@cache.cached(timeout=300)
def runbill():
    return apibill()

# Shows vote records
@app.route("/API/sector/vote")
@limiter.limit(RATE_LIMIT)
@cache.cached(timeout=300)
def runvote():
    return apivote()

# Shows lobbying records
@app.route("/API/sector/lobby")
@limiter.limit(RATE_LIMIT)
@cache.cached(timeout=1800)
def runlobby():
    return apilobby()

# Shows debate records
@app.route("/API/sector/debate")
@limiter.limit(RATE_LIMIT)
@cache.cached(timeout=300)
def rundebate():
    return apidebate()

# Shows question records
@app.route("/API/sector/question")
@limiter.limit(RATE_LIMIT)
@cache.cached(timeout=300)
def runquestion():
    return apiquestion()

# Gets bills, votes, debates, lobbying and questions for the member ID inserted
@app.route("/API/<id>")
@limiter.limit(RATE_LIMIT)
@cache.cached(timeout=300)
def runmember(id):
    return getmember(id)

# Shows every party currently in the Dáil
@app.route("/API/sector/party")
@limiter.limit(RATE_LIMIT)
@cache.cached(timeout=3600)
def runparty():
    return apiparty()

# For constituency map
@app.route("/API/sector/constituency")
@cache.cached(timeout=86400)
def runconstituency():
    return apiconstituency()

# Gets party numbers
@app.route("/API/sector/index")
@limiter.limit(RATE_LIMIT)
@cache.cached(timeout=900)
def runindex():
    return apicomposition()

# Shows lobbyists
@app.route("/API/sector/lobbyist")
@limiter.limit(RATE_LIMIT)
@cache.cached(timeout=1800)
def runlobbyist():
    return apilobbyist()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
