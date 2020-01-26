from flask import Flask, request, redirect, make_response
from flask_restful import reqparse, abort, Api, Resource
from flask_pymongo import PyMongo
from werkzeug.security import check_password_hash, generate_password_hash
from app.helpers import helpers
from datetime import datetime
from uuid import uuid4
import json, uuid

class AccountUtils:
    @staticmethod
    def check_user_pass_args(args, error_for_existing_account):
        from app import mongo
        if not args['username']:
            return {'ERROR': 'username is required.'}
        elif not args['password']:
            return {'ERROR': 'password is required.'}
        elif error_for_existing_account and AccountUtils.account_for_args(args):
            return {'ERROR': 'User {} is already registered.'.format(args['username'])}
        
        return {}

    @staticmethod
    def account_exists_with_args(args):
        from app import mongo
        if 'username' in args and mongo.db.accounts.find_one({'username': args['username']}):
            return True
        elif 'api-key' in args and mongo.db.accounts.find_one({'api_key': args['api-key']}):
            return True
        
        return False

    @staticmethod
    def register_with_args(args):
        from app import mongo
        registration = {
            "username": args['username'],
            "password": generate_password_hash(args['password']),
            "date_created": datetime.now(),
            "api_key": str(uuid4()),
            "session_token": str(uuid4())
        }
        mongo.db.accounts.insert_one(registration)
        return registration

    @staticmethod
    def account_for_args(args):
        from app import mongo
        args_check = AccountUtils.check_user_pass_args(args, False)
        if 'ERROR' in args_check:
            return args_check
        account = mongo.db.accounts.find_one({'username': args['username']})
        if not account:
            return {'ERROR': 'no account found for {}.'.format(args['username'])}
        elif not check_password_hash(account['password'], args['password']):
            return {'ERROR': 'incorrect password!'}
        else:
            return account

class Account(Resource):
    
    def post(self):
        args = helpers.parsed_args(['username', 'password'], [])
        args_check = AccountUtils.check_user_pass_args(args, True)
        if 'ERROR' in args_check:
            abort(500, args_check['ERROR'])
        
        registration = register(args)
        return make_response(registration, 200, {'Content-Type': 'application/json'})

        
    def get(self):
        args = helpers.parsed_args([], ['api-key'])

        if not ['api-key']:
            abort(500, 'api-key is required.')

        account = mongo.db.accounts.find_one({'api_key': args['api-key']})
        if not account:
            abort(500, 'no account found for key {}.'.format(args['api-key']))
        
        account['_id'] = str(account['_id'])
        account['date_created'] = str(account['date_created'])
        return make_response(account, 200, {'Content-Type': 'application/json'})