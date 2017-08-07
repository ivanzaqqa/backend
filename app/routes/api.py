'''
put api route in here
'''
from flask import Blueprint, request

# import middlewares
from app.middlewares.authentication import token_required

# controllers import
from app.controllers.ticket_controller import TicketController
from app.controllers.stage_controller import StageController

api = Blueprint('api', __name__)


@api.route('/', methods=['GET'])
@token_required
def api_index(*args, **kwargs):
	return 'api index'

# Ticket api


@api.route('/tickets', methods=['GET', 'POST'])
@token_required
def ticket(*args, **kwargs):
	if(request.method == 'POST'):
		return TicketController.create(request)
	elif(request.method == 'GET'):
		return TicketController.index()

# Get ticket by id


@api.route('/tickets/<id>', methods=['GET', 'PUT', 'PATCH', 'DELETE'])
@token_required
def ticket_id(id, *args, **kwargs):
	if(request.method == 'PUT' or request.method == 'PATCH'):
		return TicketController.update(request, id)
	elif(request.method == 'DELETE'):
		return TicketController.delete(id)
	elif(request.method == 'GET'):
		return TicketController.show(id)

# Stage api


@api.route('/stages', methods=['GET', 'POST'])
@token_required
def stage(*args, **kwargs):
	if(request.method == 'POST'):
		return StageController.create(request)
	elif(request.method == 'GET'):
		return StageController.index()

# Get ticket by id


@api.route('/stages/<id>', methods=['GET', 'PUT', 'PATCH', 'DELETE'])
@token_required
def stage_id(id, *args, **kwargs):
	if(request.method == 'PUT' or request.method == 'PATCH'):
		return StageController.update(request, id)
	elif(request.method == 'DELETE'):
		return StageController.delete(id)
	elif(request.method == 'GET'):
		return StageController.show(id)
