from flask import Flask, request, redirect, render_template, url_for, session, flash, g
from flask_restful import Api
from flask_pymongo import PyMongo
from app.api_v1.accounts import Account, AccountUtils
from app.helpers import helpers
from os import makedirs

app = Flask(__name__, instance_relative_config=True)
app.config.from_mapping(
    DEBUG=True,
    TESTING=True,
    SECRET_KEY='dev',
    MONGO_URI='mongodb://localhost:27017/PyAPI'
)
app.config.from_json('config.json', silent=True)
makedirs(app.instance_path, exist_ok=True)

mongo = PyMongo(app, uri=app.config['MONGO_URI'])
api = Api(app)
api.add_resource(Account, '/api_v1/account')

@app.errorhandler(500)
def error(error):
    return "We've encountered an error! ({})".format(str(error))


@app.route('/')
def app_index():
    return render_template('index.html', title='Home')


@app.route('/account')
def account_index():
    return render_template('/account/index.html', account=g.account, title='Account')


@app.route('/account/register', methods=['GET', 'POST'])
def register_index():
    if request.method == 'GET':
        return render_template('/account/register.html', title='Register')
    elif request.method == 'POST':
        args = helpers.parsed_args(['username', 'password'], [])
        args_check = AccountUtils.check_user_pass_args(args, True)
        if 'ERROR' in args_check:
            flash(args_check['ERROR'])
            return render_template('/account/register.html', title='Register')
        else:
            account = AccountUtils.register_with_args(args)
            helpers.set_session_token(app, account['session_token'])
            return redirect(url_for('app_index'))


@app.route('/account/login', methods=['GET', 'POST'])
def login_index():
    if request.method == 'GET':
        return render_template('/account/login.html', title='Login')
    elif request.method == 'POST':
        args = helpers.parsed_args(['username', 'password'], [])
        account = AccountUtils.account_for_args(args)
        if 'ERROR' in account:
            flash(account['ERROR'])
            return render_template('/account/login.html', title='Login')
        else:
            helpers.set_session_token(app, account['session_token'])
            return redirect(url_for('app_index'))


@app.route('/account/logout')
def logout_index():
    session.clear()
    return redirect(url_for('app_index'))


@app.before_request
def get_account_for_session():
    if 'session_token' not in session:
        g.account = None
    else:
        g.account = mongo.db.accounts.find_one({'session_token': session['session_token']})

