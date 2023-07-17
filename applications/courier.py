from flask import Flask, request, Response, json
from configuration import Configuration
from models import database, Product, Category, ProductCategory, Order, OrderProduct
from flask_jwt_extended import JWTManager, get_jwt_identity
from roleDecorator import roleCheck
from sqlalchemy import and_

application = Flask(__name__)
application.config.from_object(Configuration)

jwt = JWTManager(application)


@application.route("/orders_to_deliver", methods=["GET"])
@roleCheck(role="courier")
def orders_to_deliver():
    if request.headers.get('Authorization') is None:
        return Response(json.dumps({"msg": "Missing Authorization Header"}), status=401)

    orders = Order.query.filter(Order.status == "CREATED").all()

    orderList = [{"id": order.id, "email": order.customerEmail}
                 for order in orders]

    return Response(json.dumps({"orders": orderList}), status=200)


@application.route("/pick_up_order", methods=["POST"])
@roleCheck(role="courier")
def pick_up_order():
    if request.headers.get('Authorization') is None:
        return Response(json.dumps({"msg": "Missing Authorization Header"}), status=401)

    id = request.json.get("id", None)

    if id is None:
        return Response(json.dumps({"message": "Missing order id."}), status=400)

    try:
        if int(id) <= 0:
            return Response(json.dumps({"message": "Invalid order id."}), status=400)
    except ValueError:
        return Response(json.dumps({"message": "Invalid order id."}), status=400)

    order = Order.query.filter(
        and_(Order.status == "CREATED", Order.id == id)).first()

    if order is None:
        return Response(json.dumps({"message": "Invalid order id."}), status=400)

    order.status = "PENDING"
    database.session.commit()

    return Response(status=200)


if __name__ == "__main__":
    database.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=5003)
