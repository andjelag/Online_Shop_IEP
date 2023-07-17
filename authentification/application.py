from flask import Flask, request, Response, json
from configuration import Configuration
from models import database, User, UserRole
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, create_refresh_token, get_jwt, get_jwt_identity
from sqlalchemy import and_
import re

application = Flask(__name__)
application.config.from_object(Configuration)


@application.route("/register_customer", methods=["POST"])
def register_customer():
    email = request.json.get("email", "")
    password = request.json.get("password", "")
    forename = request.json.get("forename", "")
    surname = request.json.get("surname", "")

    emailEmpty = len(email) == 0
    passwordEmpty = len(password) == 0
    forenameEmpty = len(forename) == 0
    surnameEmpty = len(surname) == 0

    if forenameEmpty:
        return Response(json.dumps({"message": "Field forename is missing."}), status=400)
    if surnameEmpty:
        return Response(json.dumps({"message": "Field surname is missing."}), status=400)
    if emailEmpty:
        return Response(json.dumps({"message": "Field email is missing."}), status=400)
    if passwordEmpty:
        return Response(json.dumps({"message": "Field password is missing."}), status=400)

    emailRegex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if not re.fullmatch(emailRegex, email):
        return Response(json.dumps({"message": "Invalid email."}), status=400)

    if len(password) < 8:
        return Response(json.dumps({"message": "Invalid password."}), status=400)

    userExists = User.query.filter(User.email == email).first() is not None
    if userExists:
        return Response(json.dumps({"message": "Email already exists."}), status=400)

    customer = User(email=email, password=password,
                    forename=forename, surname=surname)
    database.session.add(customer)
    database.session.commit()

    userRole = UserRole(userId=customer.id, roleId=2)
    database.session.add(userRole)
    database.session.commit()

    return Response(status=200)


@ application.route("/register_courier", methods=["POST"])
def register_courier():
    email = request.json.get("email", "")
    password = request.json.get("password", "")
    forename = request.json.get("forename", "")
    surname = request.json.get("surname", "")

    emailEmpty = len(email) == 0
    passwordEmpty = len(password) == 0
    forenameEmpty = len(forename) == 0
    surnameEmpty = len(surname) == 0

    if forenameEmpty:
        return Response(json.dumps({"message": "Field forename is missing."}), status=400)
    if surnameEmpty:
        return Response(json.dumps({"message": "Field surname is missing."}), status=400)
    if emailEmpty:
        return Response(json.dumps({"message": "Field email is missing."}), status=400)
    if passwordEmpty:
        return Response(json.dumps({"message": "Field password is missing."}), status=400)

    emailRegex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if not re.fullmatch(emailRegex, email):
        return Response(json.dumps({"message": "Invalid email."}), status=400)

    if len(password) < 8:
        return Response(json.dumps({"message": "Invalid password."}), status=400)

    userExists = User.query.filter(User.email == email).first() is not None
    if userExists:
        return Response(json.dumps({"message": "Email already exists."}), status=400)

    courier = User(email=email, password=password,
                   forename=forename, surname=surname)
    database.session.add(courier)
    database.session.commit()

    userRole = UserRole(userId=courier.id, roleId=3)
    database.session.add(userRole)
    database.session.commit()

    return Response(status=200)


jwt = JWTManager(application)


@ application.route("/login", methods=["POST"])
def login():
    email = request.json.get("email", "")
    password = request.json.get("password", "")

    emailEmpty = len(email) == 0
    passwordEmpty = len(password) == 0

    if emailEmpty:
        return Response(json.dumps({"message": "Field email is missing."}), status=400)
    if passwordEmpty:
        return Response(json.dumps({"message": "Field password is missing."}), status=400)

    emailRegex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if not re.fullmatch(emailRegex, email):
        return Response(json.dumps({"message": "Invalid email."}), status=400)

    user = User.query.filter(
        and_(
            User.email == email,
            User.password == password
        )
    ).first()

    if not user:
        return Response(json.dumps({"message": "Invalid credentials."}), status=400)

    additionalClaims = {
        "forename": user.forename,
        "surname": user.surname,
        "roles": [str(role) for role in user.roles]
    }
    accessToken = create_access_token(
        identity=user.email, additional_claims=additionalClaims)

    return Response(json.dumps({"accessToken": accessToken}), status=200)


@application.route("/delete", methods=["POST"])
@jwt_required()
def delete():
    if request.headers.get('Authorization') is None:
        return Response(json.dumps({"msg": "Missing Authorization Header"}), status=401)

    email = get_jwt_identity()

    user = User.query.filter(User.email == email).first()
    userExists = user is not None
    if not userExists:
        return Response(json.dumps({"message": "Unknown user."}), status=400)

    UserRole.query.filter(UserRole.userId == user.id).delete()
    User.query.filter(User.email == email).delete()
    database.session.commit()

    return Response(status=200)


@ application.route("/", methods=["GET"])
def index():
    return "Authentification application works!"


if __name__ == "__main__":
    database.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=5002)
