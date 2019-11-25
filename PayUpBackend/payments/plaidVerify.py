from flask import Flask, jsonify, Blueprint, redirect, render_template, request, url_for
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token, 
    get_jwt_identity, get_jwt_claims
)
import plaid
import stripe
from payments import get_model
import datetime

stripe.api_key = 'pk_live_KuOhhyOaB1XR1TuPZqQYgJCy00QOuy7mct'

plaidVerify = Blueprint('plaidVerify', __name__)

PLAID_CLIENT_ID = "5cf74d115885ff001239e890"
PLAID_SECRET = "8dcfe7319c38c7f29b94af7813655a"
PLAID_PUBLIC_KEY = "7ea15e63e03666c292fe0815c58488"
# Use 'sandbox' to test with Plaid's Sandbox environment (username: user_good,
# password: pass_good)
# Use `development` to test with live users and credentials and `production`
# to go live
PLAID_ENV = "development"
# PLAID_PRODUCTS is a comma-separated list of products to use when initializing
# Link. Note that this list must contain 'assets' in order for the app to be
# able to create and retrieve asset reports.
PLAID_PRODUCTS = 'transactions'

# PLAID_COUNTRY_CODES is a comma-separated list of countries for which users
# will be able to select institutions from.
PLAID_COUNTRY_CODES = 'US,CA,GB,FR,ES'

client = plaid.Client(client_id = PLAID_CLIENT_ID, secret=PLAID_SECRET,
                      public_key=PLAID_PUBLIC_KEY, environment=PLAID_ENV, api_version='2019-05-29')


@plaidVerify.route('/bankAuth')
@jwt_required
def plaidAuth():
    print("Plaid Auth")
    array = str(request.headers['Authorization']).split(' ')
    token = array[1]
    print(token)

    return render_template('plaidLink.ejs', token = token)

#Maybe Secure
@plaidVerify.route('/newToken', methods=["POST"])
@jwt_required
def newToken():
    print("New Token")
    if not request.is_json:
        print("Missing JSON")
        return jsonify({"msg": "Missing JSON in request"}), 400

    params = request.get_json()
    print(params)

    PLAID_LINK_PUBLIC_TOKEN = params.get('public_token', None)
    ACCOUNT_ID = params.get('id', None)
    bankName = params.get('type', None)
    mask = params.get('mask', None)
    print(PLAID_LINK_PUBLIC_TOKEN)
    print(ACCOUNT_ID)
    print(bankName)
    print(mask)

    exchange_token_response = client.Item.public_token.exchange(PLAID_LINK_PUBLIC_TOKEN)
    access_token = exchange_token_response['access_token']

    stripe_response = client.Processor.stripeBankAccountTokenCreate(access_token, ACCOUNT_ID)
    bank_account_token = stripe_response['stripe_bank_account_token']

    uid = get_jwt_identity()

    customer = stripe.Customer.create( 
        source = bank_account_token,
        description = uid
    )
    print("Costumer: " + str(customer))

    #TODO: Add new method to database
    data = {
        '_type': "Bank",
        '_name': bankName,
        '_stripeToken': customer.id,
        '_dateAdded': datetime.datetime.now(),
        '_plaidToken': PLAID_LINK_PUBLIC_TOKEN,
        '_mask': mask,
        '_uid': uid
    }
    print("newToken: " + str(data))
    newPayment = get_model().createPayment(data)

    addPaymentToUser(uid, newPayment['id'])

    return jsonify({"success": "success"}), 200

@plaidVerify.route('/bank/<name>/<mask>')
def bankRedirect(name, mask):
    return render_template('success.html')

@plaidVerify.route('/bankError')
def bankErrorRedirect():
    return render_template('error.html')

def addPaymentToUser(uid, paymentId):
    user = get_model().readUser(uid)
    print("User " + str(user))
    if user == None:
        data = {
            "_uid": uid,
            "_payment1": paymentId,
            "_payment2": None,
            "_payment3": None,
            "_payment4": None,
            "_payment5": None,
            "_preffered": paymentId
        }
        get_model().createUser(data)

    elif user['_payment1'] == None:
        user['_payment1'] = paymentId
        user['_preffered'] = paymentId
        data = get_model().updateUser(user, uid)

    elif user['_payment2'] == None:
        user['_payment2'] = paymentId
        user['_preffered'] = paymentId
        print('Payment 2:' + str(user))
        data = get_model().updateUser(user, uid)

    elif user['_payment3'] == None:
        print('Payment 3:' + str(user))
        user['_payment3'] = paymentId
        user['_preffered'] = paymentId
        data = get_model().updateUser(user, uid)

    elif user['_payment4'] == None:
        user['_payment4'] = paymentId
        user['_preffered'] = paymentId
        print('Payment 4:' + str(user))
        data = get_model().updateUser(user, uid)

    else:
        user['_payment5'] = paymentId
        user['_preffered'] = paymentId
        print('Payment 5:' + str(user))
        data = get_model().updateUser(user, uid)
