from calendar import timegm
from zenora import APIClient
from flask import Flask, request, abort, session, g
from datetime import datetime, timedelta
from flask_cors import CORS

from .util import auth_required, get_username_from_jwt
from .models import db, Quote

import os
import jwt

app = Flask(__name__)
discord_api = APIClient(
    token=os.environ["BOT_TOKEN"], client_secret=os.environ["OAUTH_CLIENT_SECRET"])
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URI"]
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SECURE"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "None"
app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]
db.init_app(app)
CORS(app, supports_credentials=True)


@app.get("/auth")
@auth_required
def get_auth_status():
    return "Authenticated"


@app.get("/username")
@auth_required
def get_username():
    return get_username_from_jwt(session["auth"])

@app.post("/logout")
@auth_required
def logout():
    session.clear()
    return "Success"

@app.post("/oauth/callback")
def oauth_callback():
    code = request.json["code"]
    access_token = discord_api.oauth.get_access_token(
        code, redirect_uri=os.environ["REDIRECT_URI"]
    ).access_token
    bearer_client = APIClient(access_token, validate_token=False, bearer=True)
    user = bearer_client.users.get_current_user()

    encoded_jwt = jwt.encode({"id": user.id, "username": f"{user.username}#{user.discriminator}", "exp": timegm((datetime.now(
    ) + timedelta(minutes=30)).utctimetuple())}, os.environ["SECRET_KEY"], algorithm="HS256")

    session["auth"] = encoded_jwt

    return "Logged in"


@app.get("/quotes/all")
def get_all_quotes():
    quotes = Quote.query.all()
    return {"quotes": [{"author": i.name, "content": i.content, "created_at": str(int(i.created_at.timestamp()))} for i in quotes]}


@app.post("/quotes/add")
@auth_required
def add_quote():
    content = request.json["content"]

    existing_user_quote = bool(
        Quote.query.filter_by(user_id=g.user_id).first())

    if existing_user_quote:
        # A user can only upload quote once
        abort(403)

    new_quote = Quote(user_id=g.user_id, name=get_username_from_jwt(session["auth"]),
                      content=content, created_at=datetime.now())
    db.session.add(new_quote)
    db.session.commit()

    return "Quote added"
