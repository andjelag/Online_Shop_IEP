from flask import Flask, request, Response, json
from configuration import Configuration
from models import database, Product, Category, ProductCategory, Order, OrderProduct
from flask_jwt_extended import JWTManager, get_jwt_identity
from roleDecorator import roleCheck
from sqlalchemy import and_

application = Flask(__name__)
application.config.from_object(Configuration)

jwt = JWTManager(application)


@application.route("/search", methods=["GET"])
@roleCheck(role="customer")
def search():
    if request.headers.get('Authorization') == None:
        return Response(json.dumps({"msg": "Missing Authorization Header"}), status=401)

    name = request.args.get("name", "")
    category = request.args.get("category", "")

    categoriesFromDatabase = database.session.query(Category.name).filter(and_(
        Category.name.like(f"%{category}%"),
        Category.id == ProductCategory.categoryId,
        ProductCategory.productId == Product.id,
        Product.name.like(f"%{name}%")
    )).distinct().all()
    categories = [
        categoryFromDatabase.name for categoryFromDatabase in categoriesFromDatabase]

    products = Product.query.join(Product.categories).filter(
        and_(Category.name.like(f"%{category}%"), Product.name.like(f"%{name}%"))).all()
    products = [
        {"categories": [category.name for category in product.categories], "id": product.id, "name": product.name,
         "price": product.price} for product in products]

    return Response(json.dumps({"categories": categories, "products": products}), status=200)


@application.route("/order", methods=["POST"])
@roleCheck(role="customer")
def order():
    if request.headers.get('Authorization') == None:
        return Response(json.dumps({"msg": "Missing Authorization Header"}), status=401)

    requests = request.json.get("requests", None)

    if requests is None:
        return Response(json.dumps({"message": "Field requests is missing."}), status=400)

    requestNumber = 0
    products = []
    price = 0
    for req in requests:
        if "id" not in req:
            return Response(json.dumps({"message": f"Product id is missing for request number {requestNumber}."}), status=400)

        if "quantity" not in req:
            return Response(json.dumps({"message": f"Product quantity is missing for request number {requestNumber}."}),
                            status=400)

        productId = req["id"]
        productQuantity = req["quantity"]

        try:
            if int(productId) <= 0:
                return Response(json.dumps({"message": f"Invalid product id for request number {requestNumber}."}), status=400)
        except ValueError:
            return Response(json.dumps({"message": f"Invalid product id for request number {requestNumber}."}), status=400)

        try:
            if int(productQuantity) <= 0:
                return Response(json.dumps({"message": f"Invalid product quantity for request number {requestNumber}."}),
                                status=400)
        except ValueError:
            return Response(json.dumps({"message": f"Invalid product quantity for request number {requestNumber}."}),
                            status=400)

        product = Product.query.filter(Product.id == productId).first()

        if not product:
            return Response(json.dumps({"message": f"Invalid product for request number {requestNumber}."}), status=400)

        price += product.price * productQuantity
        products.append({"product": product, "quantity": productQuantity})

        requestNumber += 1

    identity = get_jwt_identity()
    order = Order(price=price, status="CREATED", customerEmail=identity)
    database.session.add(order)
    database.session.commit()

    for product in products:
        orderProduct = OrderProduct(
            orderId=order.id, productId=product["product"].id, quantity=product["quantity"])
        product["product"].waiting += product["quantity"]
        database.session.add(orderProduct)
        database.session.commit()

    return Response(json.dumps({"id": order.id}), status=200)


@application.route("/status", methods=["GET"])
@roleCheck(role="customer")
def status():
    if request.headers.get('Authorization') == None:
        return Response(json.dumps({"msg": "Missing Authorization Header"}), status=401)

    identity = get_jwt_identity()
    orders = Order.query.filter(
        Order.customerEmail == identity).all()
    orders = [
        {"products": [
            {"categories": [category.name for category in product.categories], "name": product.name,
             "price": product.price, "quantity": OrderProduct.query.filter(and_(OrderProduct.productId == product.id, OrderProduct.orderId == order.id)).first().quantity} for product in order.products],
         "price": order.price, "status": order.status, "timestamp": order.timestamp.isoformat()} for order in orders]

    return Response(json.dumps({"orders": orders}), status=200)


@application.route("/delivered", methods=["POST"])
@roleCheck(role="customer")
def delivered():
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
        and_(Order.status == "PENDING", Order.id == id)).first()

    if order is None:
        return Response(json.dumps({"message": "Invalid order id."}), status=400)

    order.status = "COMPLETE"
    database.session.commit()
    for product in order.products:
        quantity = OrderProduct.query.filter(
            OrderProduct.orderId == order.id, OrderProduct.productId == product.id).first().quantity
        product.sold += quantity
        product.waiting -= quantity
        database.session.commit()

    return Response(status=200)


if __name__ == "__main__":
    database.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=5002)
