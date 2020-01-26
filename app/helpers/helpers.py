from flask import session
from flask_restful import reqparse
from datetime import timedelta

def set_session_token(app, token):
    session.clear()
    session['session_token'] = token
    session.permanent = True
    app.permanent_session_lifetime = timedelta(days=30)


def parsed_args(args, headers):
    parser = reqparse.RequestParser()
    if headers is not None:
        for header in headers:
            parser.add_argument(header, location='headers', required=True)
    if args is not None:
        for arg in args:
            parser.add_argument(arg)
    return parser.parse_args()
