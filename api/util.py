from functools import wraps
from flask import abort, session, g

import jwt
import os

def auth_required(f):
    @wraps(f)
    def inner(*args, **kwargs):
        token = session.get("auth")
        if not token:
            abort(401) 
        try:
            decoded_jwt = jwt.decode(token, os.environ["SECRET_KEY"], algorithms=["HS256"])
            g.user_id = decoded_jwt["id"]  # Putting user id in global request context
        except jwt.PyJWTError:
            abort(401)

        return f(*args, **kwargs)
    return inner