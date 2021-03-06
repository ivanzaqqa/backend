from flask import current_app

import datetime
import secrets
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

# import classes
from app.models.base_model import BaseModel
from app.models.user_photo import UserPhoto
from app.models import db
from app.services.helper import Helper


class User(db.Model, BaseModel):
	# table name
	__tablename__ = 'users'
	# displayed fields
	visible = ['id', 'first_name', 'last_name', 'role_id', 'social_id', 'username', 'email', 'photos', 'created_at', 'updated_at']

	# columns definitions
	id = db.Column(db.Integer, primary_key=True)
	first_name = db.Column(db.String)
	last_name = db.Column(db.String)
	username = db.Column(db.String, index=True, unique=True)
	email = db.Column(db.String, index=True, unique=True)
	password = db.Column(db.String)
	role_id = db.Column(db.Integer)
	social_id = db.Column(db.String)
	created_at = db.Column(db.DateTime)
	updated_at = db.Column(db.DateTime)
	photos = []

	def __init__(self):
		self.created_at = datetime.datetime.now()
		self.updated_at = datetime.datetime.now()

	def hash_password(self, password):
		self.password = generate_password_hash(password)

	def verify_password(self, password):
		return check_password_hash(self.password, password)

	def generate_auth_token(self, expiration=3600*24):
		s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
		return s.dumps({'id': self.id})

	@staticmethod
	def verify_auth_token(token):
		s = Serializer(current_app.config['SECRET_KEY'])
		try:
			data = s.loads(token)
		except SignatureExpired:
			return None
		except BadSignature:
			return None
		user = db.session.query(User).filter_by(id=data['id']).first()
		return user

	def generate_refresh_token(self):
		return secrets.token_hex(8)

	def include_photos(self):
		results = db.session.query(UserPhoto).filter_by(user_id=self.id).all()
		self.photos = []
		for result in results:
			data = result.as_dict()
			data['url'] = Helper().url_helper(data['url'], current_app.config['GET_DEST'])
			self.photos.append(data)
		return self
