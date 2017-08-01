'''
put api route in here
'''
from flask import Blueprint, request

# import middlewares
from app.middlewares.authentication import token_required

# import models
from app.models.user import User

# import controllers
from app.controllers.order_controller import OrderController

api = Blueprint('api', __name__)


@api.route('/', methods=['GET'])
@token_required
def index(*args, **kwargs):
	return 'api index'

@api.route('/order', methods=['POST'])
@token_required
def order(*args, **kwargs):
	# check if user is valid
	user = User.verify_auth_token(kwargs['user'])
	return OrderController.order(request)