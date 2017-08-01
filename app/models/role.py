import datetime

from app.models.base_model import BaseModel
from app.models import db

class Role(db.Model, BaseModel):
	# table name
	__tablename__ = 'roles'
	# visible fields
	visible = ['name', 'created_at', 'updated_at']

	# column definitions
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String, unique=True)
	created_at = db.Column(db.DateTime)
	updated_at = db.Column(db.DateTime)

	def __init__(self):
		self.created_at = datetime.datetime.now()
		self.updated_at = datetime.datetime.now()
