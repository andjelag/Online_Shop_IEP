from flask import Flask
from configuration import Configuration
from flask_migrate import Migrate, init, migrate, upgrade
from models import database, Role, UserRole, User
from sqlalchemy_utils import database_exists, create_database

application = Flask(__name__)
application.config.from_object(Configuration)

migrateObject = Migrate(application, database)

if not database_exists(application.config["SQLALCHEMY_DATABASE_URI"]):
    create_database(application.config["SQLALCHEMY_DATABASE_URI"])

database.init_app(application)

with application.app_context() as context:
    init()
    migrate(message="Production migration")
    upgrade()

    roleForOwner = Role(name="owner")
    roleForCustomer = Role(name="customer")
    roleForCourier = Role(name="courier")
    database.session.add(roleForOwner)
    database.session.add(roleForCustomer)
    database.session.add(roleForCourier)
    database.session.commit()

    owner = User(
        email="onlymoney@gmail.com",
        password="evenmoremoney",
        forename="Scrooge",
        surname="McDuck"
    )
    database.session.add(owner)
    database.session.commit()

    userRole = UserRole(
        userId=owner.id,
        roleId=roleForOwner.id
    )
    database.session.add(userRole)
    database.session.commit()
