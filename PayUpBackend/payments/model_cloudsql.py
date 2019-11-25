# Copyright 2015 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

builtin_list = list

db = SQLAlchemy()


def init_app(app):
    # Disable track modifications, as it unnecessarily uses memory.
    app.config.setdefault('SQLALCHEMY_TRACK_MODIFICATIONS', False)
    db.init_app(app)


def from_sql(row):
    """Translates a SQLAlchemy model instance into a dictionary"""
    data = row.__dict__.copy()
    data['id'] = row.id
    data.pop('_sa_instance_state')
    return data

def user_from_sql(row):
    data = row.__dict__.copy()
    data.pop('_sa_instance_state')
    return data


# [START model]
class Payment(db.Model):
    __tablename__ = 'Payment'

    id = db.Column(db.Integer, primary_key=True)
    _type = db.Column(db.String(32))
    _name = db.Column(db.String(32))
    _stripeToken = db.Column(db.String(255))
    _dateAdded = db.Column(db.String(255))
    _plaidToken = db.Column(db.String(255))
    _mask = db.Column(db.String(16))
    _uid = db.Column(db.String(255))


class Users(db.Model):
    __tablename__ = 'Users'

    _uid = db.Column(db.String(255), primary_key=True)
    _payment1 = db.Column(db.Integer)
    _payment2 = db.Column(db.Integer)
    _payment3 = db.Column(db.Integer)
    _payment4 = db.Column(db.Integer)
    _payment5 = db.Column(db.Integer)
    _preffered = db.Column(db.Integer)

# [END model]


# # [START list]
# def list(limit=10, cursor=None):
#     cursor = int(cursor) if cursor else 0
#     query = (Book.query
#              .order_by(Book.title)
#              .limit(limit)
#              .offset(cursor))
#     books = builtin_list(map(from_sql, query.all()))
#     next_page = cursor + limit if len(books) == limit else None
#     return (books, next_page)
# # [END list]


# [START read]
def readPayment(id):
    result = Payment.query.get(id)
    if not result:
        return None
    return from_sql(result)

def readUser(id):
    result = Users.query.get(id)
    if not result:
        return None
    return user_from_sql(result)
# [END read]


# [START create]
def createPayment(data):
    payment = Payment(**data)
    db.session.add(payment)
    db.session.commit()
    return from_sql(payment)

def createUser(data):
    user = Users(**data)
    db.session.add(user)
    db.session.commit()
    return user_from_sql(user)
# [END create]


# [START update]
def updatePayment(data, id):
    payment = Payment.query.get(id)
    for k, v in data.items():
        setattr(payment, k, v)
    db.session.commit()
    return from_sql(payment)

def updateUser(data, id):
    print("Updating User")
    user = Users.query.get(id)
    print("Update: " + str(user))
    for k, v in data.items():
        setattr(user, k, v)
    db.session.commit()
    return user_from_sql(user)
# [END update]


def deletePayment(id):
    Payment.query.filter_by(id=id).delete()
    db.session.commit()

def deleteUser(id):
    Users.query.filter_by(id=id).delete()
    db.session.commit()


def _create_database():
    """
    If this script is run directly, create all the tables necessary to run the
    application.
    """
    app = Flask(__name__)
    app.config.from_pyfile('../config.py')
    init_app(app)
    with app.app_context():
        db.create_all()
    print("All tables created")


if __name__ == '__main__':
    _create_database()
