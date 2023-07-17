from flask import Flask, request, Response, json
from configuration import Configuration
from models import database, Product, Category, ProductCategory, Order, OrderProduct
from flask_jwt_extended import JWTManager
from roleDecorator import roleCheck
from sqlalchemy import func, desc
from sqlalchemy.sql.functions import coalesce
import csv
import io

application = Flask(__name__)
application.config.from_object(Configuration)

jwt = JWTManager(application)


@application.route("/update", methods=["POST"])
@roleCheck(role="owner")
def update():

    if request.headers.get('Authorization') == None:
        return Response(json.dumps({"msg": "Missing Authorization Header"}), status=401)

    file = request.files.get("file", None)

    if file is None:
        return Response(json.dumps({"message": "Field file is missing."}), status=400)

    content = file.stream.read().decode("utf-8")
    stream = io.StringIO(content)
    reader = csv.reader(stream)

    products = []
    lineNumber = 0
    for row in reader:
        if len(row) < 3:
            return Response(json.dumps({"message": f"Incorrect number of values on line {lineNumber}."}), status=400)
        try:
            if float(row[2]) <= 0:
                return Response(json.dumps({"message": f"Incorrect price on line {lineNumber}."}), status=400)
        except ValueError:
            return Response(json.dumps({"message": f"Incorrect price on line {lineNumber}."}), status=400)
        productExists = Product.query.filter(
            Product.name == row[1]).first() is not None
        if productExists:
            return Response(json.dumps({"message": f"Product {row[1]} already exists."}), status=400)

        product = {"categories": row[0],
                   "name": row[1], "price": float(row[2])}
        products.append(product)

        lineNumber += 1

    for product in products:
        productInDatabase = Product(
            name=product["name"], price=product["price"])
        database.session.add(productInDatabase)
        database.session.commit

        categories = product["categories"].split('|')
        for categoryName in categories:
            categoryInDatabase = Category.query.filter(
                Category.name == categoryName).first()
            if categoryInDatabase is None:
                newCategory = Category(name=categoryName)
                database.session.add(newCategory)
                database.session.commit()

                productCategory = ProductCategory(
                    productId=productInDatabase.id, categoryId=newCategory.id)
                database.session.add(productCategory)
                database.session.commit()
            else:
                productCategory = ProductCategory(
                    productId=productInDatabase.id, categoryId=categoryInDatabase.id)
                database.session.add(productCategory)
                database.session.commit()

    return Response(status=200)


@application.route("/product_statistics", methods=["GET"])
@roleCheck(role="owner")
def product_statistics():
    if request.headers.get('Authorization') == None:
        return Response(json.dumps({"msg": "Missing Authorization Header"}), status=401)

    statistics = database.session.query(Product.name, coalesce(func.sum(Product.sold), 0), coalesce(func.sum(
        Product.waiting), 0)).select_from(Product).group_by(Product.name)

    statistics = [{"name": product[0], "sold":int(product[1]), "waiting":int(
        product[2])} for product in statistics if not (product[1] == 0 and product[2] == 0)]

    return Response(json.dumps({"statistics": statistics}), status=200)

    # soldSubquery = database.session.query(
    #     Product.name, func.sum(OrderProduct.quantity).label("sold")).join(Product).join(Order).group_by(Product.name).filter(Order.status == "COMPLETE").subquery()
    # waitingSubquery = database.session.query(
    #     Product.name, func.sum(OrderProduct.quantity).label("waiting")).join(Product).join(Order).group_by(Product.name).filter(Order.status == "PENDING").subquery()

    # statistics = database.session.query(Product.name, coalesce(
    #     soldSubquery.c.sold, 0), coalesce(waitingSubquery.c.waiting, 0)).select_from(OrderProduct).join(Product).group_by(Product.name).outerjoin(waitingSubquery, Product.name == waitingSubquery.c.name).outerjoin(soldSubquery, Product.name == soldSubquery.c.name).all()
    # statistics = waitingSubquery.all()

    # statistics = soldSubquery.join(
    #     waitingSubquery, Product.name == waitingSubquery.c.name).all()


@application.route("/category_statistics", methods=["GET"])
@roleCheck(role="owner")
def category_statistics():
    if request.headers.get('Authorization') == None:
        return Response(json.dumps({"msg": "Missing Authorization Header"}), status=401)

    statistics = database.session.query(
        Category.name, coalesce(func.sum(Product.sold), 0).label("sold")
    ).join(Category.products, isouter=True).group_by(Category.id).order_by(desc("sold"), Category.name).all()

    stats = [category[0] for category in statistics]

    return Response(json.dumps({"statistics": stats}), status=200)


if __name__ == "__main__":
    database.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=5001)
