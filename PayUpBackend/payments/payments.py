from payments import get_model
from flask import Flask, jsonify, Blueprint, redirect, render_template, request, url_for
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token, 
    get_jwt_identity, get_jwt_claims
)
from decimal import Decimal
import stripe

stripe.api_key = 'sk_live_Lx1v2zP9ULZL0szILUunDo4r00sbKRxuSW'

payments = Blueprint('payments', __name__)

@payments.route('/deposit', methods = ["POST"])
@jwt_required
def deposit():
    #Charge client from database stripe token
    if not request.is_json:
        print("Missing JSON")
        return jsonify({"msg": "Missing JSON in request"}), 400
    
    params = request.get_json()
    amount = params.get('amount', None)
    print('amount')

    uid = get_jwt_identity()

    user = get_model().readUser(uid)
    payment = get_model().readPayment(user["_preffered"])
    print("deposit")
    #Charge Client
    print(Decimal(amount))
    charge = stripe.Charge.create(
        amount = int(float(amount) * 100) ,
        currency = 'usd',
        description = 'PayUp Deposit',
        customer = payment["_stripeToken"]
    )
    print("After Charge")
    return jsonify({"charge": str(charge)}), 200

@payments.route('/withdraw')
@jwt_required
def withdraw():
    #Pay client through stripe token 
    print("withdraw")

#Body = {'mask': 4326 , 'type': Wells Fargo}
@payments.route('/deletePayment', methods = ["POST"])
@jwt_required
def deletePayment():
    print("In Delete")
    if not request.is_json:
        print("Missing JSON")
        return jsonify({"msg": "Missing JSON in request"}), 400

    params = request.get_json()
    print(params)

    _mask = params.get('mask', None)
    _name = params.get('type', None)
    print("_mask:" + str(_mask))
    print("_type:" + str(_name))

    uid = get_jwt_identity()

    user = get_model().readUser(uid)

    for i in range(5):
        payQuery = "_payment" + str(i + 1)
        paymentId = user[str(payQuery)]
        print("Delete: " + str(paymentId))
        if paymentId != None:
            payment = get_model().readPayment(paymentId)
            if payment["_name"] == _name:
                print("Type Match")
                if payment["_mask"] == _mask or payment["_mask"] == None:
                    print("Mask Match")
                    deletedPay = get_model().deletePayment(paymentId)
                    user[str(payQuery)] = None
                    if user["_preffered"] == paymentId:
                        user["_preffered"] = None
                    updatedUser = get_model().updateUser(user, uid)
                    return jsonify({"status": 1}), 200
    return jsonify({"status": -1}), 200