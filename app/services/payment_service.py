import datetime
import base64
import requests
from app.models import db
# import model class
from app.models.payment import Payment
from app.models.order_details import OrderDetails
from app.models.order import Order
from app.models.user_ticket import UserTicket
from app.configs.constants import MIDTRANS_API_BASE_URL as url, SERVER_KEY


class PaymentService():

    def __init__(self):
        self.authorization = base64.b64encode(bytes(SERVER_KEY, 'utf-8')).decode()
        self.headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json', 
            'Authorization': 'Basic ' + self.authorization
        }

    def admin_get(self):
        results = db.session.query(Payment).all()
        _results = []
        for result in results:
            data = result.as_dict()
            data['user'] = result.order.user.as_dict()
            _results.append(data)
        return {
            'data': _results,
            'message': 'payment retrieved successsfully'
        }

    def get(self, user_id):
        # get the orders
        orders = db.session.query(Order).filter_by(user_id=user_id).all()
        _results = []
        for order in orders:
            data = db.session.query(Payment).filter_by(order_id=order.id).first().as_dict()
            _results.append(data)
        return {
            'data': _results,
            'message': 'payment retrieved successsfully'
        }

    def admin_show(self, payment_id):
        result = db.session.query(Payment).filter_by(id=payment_id).first()
        data = result.as_dict()
        data['user'] = result.order.user.as_dict()
        return {
            'data': data,
            'message': 'payment retrieved successsfully'
        }

    def show(self, payment_id):
        result = db.session.query(Payment).filter_by(id=payment_id).first()
        return {
            'data': result.as_dict(),
            'message': 'payment retrieved successsfully'
        }

    def bank_transfer(self, payloads):

        payloads['gross_amount'] = int(payloads['gross_amount'])

        # generate order details payload
        details = self.get_order_details(payloads['order_id'])

        if (payloads['bank'] == 'bca'):

            # payloads validation for BCA virtual account
            if not all(
                isinstance(string, str) for string in [
                        payloads['payment_type'], 
                        payloads['order_id'], 
                        payloads['email'],
                        payloads['first_name'],
                        payloads['last_name'],
                        payloads['phone'],
                        payloads['va_number']
                ]
            ) and not isinstance(payloads['gross_amount'], int):
                return {
                    'error': True,
                    'data': 'payload not valid'
                }
            # todo create payload for BCA virtual account
            data = {}
            data['payment_type'] = payloads['payment_type']
            data['transaction_details'] = {}
            data['transaction_details']['gross_amount'] = payloads['gross_amount']
            data['transaction_details']['order_id'] = payloads['order_id']
            data['customer_details'] = {}
            data['customer_details']['email'] = payloads['email']
            data['customer_details']['first_name'] = payloads['first_name']
            data['customer_details']['last_name'] = payloads['last_name']
            data['customer_details']['phone'] = payloads['phone']
            data['item_details'] = details
            data['bank_transfer'] = {}
            data['bank_transfer']['bank'] = payloads['bank']
            data['bank_transfer']['va_number'] = payloads['va_number']
            data['bank_transfer']['free_text'] = {}
            data['bank_transfer']['free_text']['inquiry'] = [
                {
                    "id": "Free Text ID Free Text ID Free Text ID",
                    "en": "Free Text EN Free Text EN Free Text EN"
                }
            ]
            data['bank_transfer']['free_text']['payment'] = [
                {
                    "id": "Free Text ID Free Text ID Free Text ID",
                    "en": "Free Text EN Free Text EN Free Text EN"
                }
            ]

        if (payloads['bank'] == 'permata'):
            # payload validation for permata
            if not all(
                isinstance(string, str) for string in [
                    payloads['payment_type'],
                    payloads['order_id']
                ]
            ) and not isinstance(payloads['gross_amount'], int):
                return {
                    'error': True,
                    'data': 'payloads is not valid'
                }
            # create paylod for midtrans
            data = {}
            data['payment_type'] = payloads['payment_type']
            data['bank_transfer'] = {}
            data['bank_transfer']['bank'] = payloads['bank']
            data['transaction_details'] = {}
            data['transaction_details']['order_id'] = payloads['order_id']
            data['transaction_details']['gross_amount'] = payloads['gross_amount']

        if(payloads['bank'] == 'bni'):
            # payload validation for bni
            if not all(
                isinstance(string, str) for string in [
                    payloads['payment_type'],
                    payloads['email'],
                    payloads['first_name'],
                    payloads['last_name'],
                    payloads['phone'],
                    payloads['va_number']
                ]
            ) and not isinstance(payloads['gross_amount'], int):
                return {
                    'error': True,
                    'data': 'payloads is not valid'
                }

            # create payload for midtrans
            data = {}
            data['payment_type'] = payloads['payment_type']
            data['bank_transfer'] = {}
            data['bank_transfer']['bank'] = payloads['bank']
            data['bank_transfer']['va_number'] = payloads['va_number']
            data['customer_details'] = {}
            data['customer_details']['email'] = payloads['email']
            data['customer_details']['first_name'] = payloads['first_name']
            data['customer_details']['last_name'] = payloads['last_name']
            data['customer_details']['phone'] = payloads['phone']
            data['item_details'] = details
            data['transaction_details'] = {}
            data['transaction_details']['order_id'] = payloads['order_id']
            data['transaction_details']['gross_amount'] = payloads['gross_amount']

        if(payloads['bank'] == 'mandiri_bill'):
            # payload validation for bni
            if not all(
                isinstance(string, str) for string in [
                    payloads['payment_type'],
                ]
            ) and not isinstance(payloads['gross_amount'], int):
                return {
                    'error': True,
                    'data': 'payloads is not valid'
                }

            # create payload for midtrans
            data = {}
            data['payment_type'] = payloads['payment_type']
            data['item_details'] = details
            data['transaction_details'] = {}
            data['transaction_details']['order_id'] = payloads['order_id']
            data['transaction_details']['gross_amount'] = payloads['gross_amount']

        midtrans_api_response = self.send_to_midtrans_api(data)

        return midtrans_api_response

    def credit_payment(self, payloads):
        if not all(
            isinstance(string, str) for string in [
                payloads['order_id'],
                payloads['email'],
                payloads['first_name'],
                payloads['last_name'],
                payloads['phone'],
                payloads['card_number'],
                payloads['card_exp_month'],
                payloads['card_exp_year'],
                payloads['card_cvv'],
                payloads['client_key']
            ]
        ) and not isinstance(payloads['gross_amount'], int):
            return 'Payload is not valid'

        # get the token id first
        token_id = requests.get(url + 'card/register?' + 'card_number=' + payloads['card_number'] + '&card_exp_month=' + payloads['card_exp_month'] + '&card_exp_year=' + payloads['card_exp_year'] + '&card_cvv=' + payloads['card_cvv'] + '&bank=' + payloads['bank'] + '&secure=' + 'true' + '&gross_amount=' + str(payloads['gross_amount']) + '&client_key=' + payloads['client_key'], headers=self.headers)
        token_id = token_id.json()
        # prepare data 
        data = {}
        if 'status_code' in token_id and token_id['status_code'] == '200':
            data['saved_token_id'] = token_id['saved_token_id']
            data['masked_card'] = token_id['masked_card']
        else:
            return 'Failed to get token'

        item_details = self.get_order_details(payloads['order_id'])

        data['payment_type'] = payloads['payment_type']
        data['transaction_details'] = {}
        data['transaction_details']['order_id'] = payloads['order_id']
        data['transaction_details']['gross_amount'] = payloads['gross_amount']
        data['credit_card'] = {}
        data['credit_card']['token_id'] = token_id['saved_token_id']
        data['item_details'] = item_details
        data['customer_details'] = {}
        data['customer_details']['first_name'] = payloads['first_name']
        data['customer_details']['last_name'] = payloads['last_name']
        data['customer_details']['email'] = payloads['email']
        midtrans_api_response = self.send_to_midtrans_api(data)
        return midtrans_api_response

    def internet_banking(self, payloads):
        if not all(isinstance(string, str) for string in [
            payloads['order_id'],
            payloads['first_name'],
            payloads['last_name'],
            payloads['email'],
            payloads['phone']
        ]) and not isinstance(payloads['gross_amount'], int):
            return {
                'error': True,
                'message': 'payloads is not valid'
            }

        details = self.get_order_details(payloads['order_id'])

        data = {}
        data['payment_type'] = payloads['payment_type']
        data['transaction_details'] = {}
        data['transaction_details']['order_id'] = payloads['order_id']
        data['transaction_details']['gross_amount'] = payloads['gross_amount']
        data['item_details'] = details
        data['customer_details'] = {}
        data['customer_details']['first_name'] = payloads['first_name']
        data['customer_details']['last_name'] = payloads['last_name']
        data['customer_details']['email'] = payloads['email']
        data['customer_details']['phone'] = payloads['phone']        

        if (payloads['payment_type'] == 'cimb_clicks'):
            data['cimb_clicks'] = {}
            data['cimb_clicks']['description'] = payloads['description']
            data['bank'] = 'cimb'

        if (payloads['payment_type'] == 'bca_klikpay'):
            data['bca_klikpay'] = {}
            data['bca_klikpay']['type'] = 1
            data['bca_klikpay']['description'] = 'Devsummit tickets purchase'
            data['bank'] = 'bca'

        if (payloads['payment_type'] == 'bca_klikbca'):
            data['bca_klikbca'] = {}
            data['bca_klikbca']['user_id'] = payloads['user_id']
            data['bca_klikbca']['description'] = payloads['description']
            data['bank'] = 'bca'

        if (payloads['payment_type'] == 'mandiri_clickpay'):
            data['mandiri_clickpay'] = {}
            data['mandiri_clickpay']['card_number'] = payloads['card_number']
            data['mandiri_clickpay']['input1'] = payloads['card_number'][6:]
            data['mandiri_clickpay']['input2'] = payloads['gross_amount']
            data['mandiri_clickpay']['input3'] = payloads['input3']
            data['mandiri_clickpay']['token'] = payloads['token']
            data['bank'] = 'mandiri'

        midtrans_api_response = self.send_to_midtrans_api(data)

        return midtrans_api_response

    # this will send the all payment methods payload to midtrand api
    def send_to_midtrans_api(self, payloads):
        endpoint = url + 'charge'
        result = requests.post(
                endpoint,
                headers=self.headers,
                json=payloads
        )
        payload = result.json()

        if(payload['status_code'] != '400'):
            if 'bank' in payloads and payloads['payment_type'] != 'credit_card':
                payload['bank'] = payloads['bank']
            else:
                payload['bank'] = payload['bank'] if 'bank' in payload else payloads['bank_transfer']['bank']

            if ('status_code' in payload and payload['status_code'] == '201' or payload['status_code'] == '200'):
                self.save_payload(payload, payloads)

            # if  not fraud and captured save ticket to user_ticket table
            if('fraud_status' in payload and payload['fraud_status'] == 'accept' and payload['transaction_status'] == 'capture'):
                order = db.session.query(Order).filter_by(id=payload['order_id']).first()
                self.save_paid_ticket(order.as_dict())

        return payload

    def update(self, id):
        # get the transaction id from payment table
        payment = db.session.query(Payment).filter_by(id=id).first()
        if payment is not None:
            order = payment.order.as_dict()
            payment = payment.as_dict()
        else:
            return 'payment not found'
        payment_status = requests.get(
            url + str(payment['order_id']) + '/status',
            headers=self.headers
        )

        status = payment_status.json()

        if (status['status_code'] in ['200', '201', '407']):

            if (payment['transaction_status'] != status['transaction_status']):
                payment = db.session.query(Payment).filter_by(id=id)
                payment.update({
                    'updated_at': datetime.datetime.now(),
                    'transaction_status': status['transaction_status']
                })
                
                db.session.commit()
                if (payment.first().as_dict()['transaction_status'] == 'capture'):
                    # on payment success
                    self.save_paid_ticket(order)

        return status

    def save_paid_ticket(self, order):
        item_details = db.session.query(OrderDetails).filter_by(order_id=order['id']).all()
        for item in item_details:
            data = item.as_dict()
            user_ticket = UserTicket()
            user_ticket.user_id = order['user_id']
            user_ticket.used = False
            user_ticket.ticket_id = data['ticket_id']
            db.session.add(user_ticket)
            db.session.commit()


    def get_order_details(self, order_id):
        # using order_id to get ticket_id, price, quantity, ticket_type(name) in payment service
        item_details = db.session.query(OrderDetails).filter_by(order_id=order_id).all()
        result = []
        for item in item_details:
            ticket = item.ticket.as_dict()
            item = item.as_dict()
            temp = {}
            temp['name'] = ticket['ticket_type']
            temp['price'] = item['price']
            temp['quantity'] = item['count']
            temp['id'] = item['id']
            result.append(temp)
        return result

    def save_payload(self, data, payloads):
        new_payment = Payment()
        new_payment.transaction_id = data['transaction_id']
        new_payment.order_id = data['order_id']
        new_payment.gross_amount = data['gross_amount']
        new_payment.payment_type = data['payment_type']
        new_payment.transaction_time = data['transaction_time']
        new_payment.transaction_status = data['transaction_status']
        new_payment.bank = data['bank']
        new_payment.fraud_status = data['fraud_status'] if 'fraud_status' in data else None
        new_payment.masked_card = payloads['masked_card'] if 'masked_card' in payloads else None
        new_payment.saved_token_id = payloads['saved_token_id'] if 'saved_token_id' in payloads else None

        db.session.add(new_payment)
        db.session.commit()
