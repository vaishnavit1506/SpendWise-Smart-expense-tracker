import os
import logging

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_login import LoginManager

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
# create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1) # needed for url_for to generate with https

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the app with the extension
db.init_app(app)

# Configure login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

with app.app_context():
    # Import models
    from models import User, Category, Expense, Budget  # noqa: F401
    db.create_all()

    # Create default categories if they don't exist
    from models import Category

    default_categories = [
        "Food & Dining", "Transportation", "Housing", "Utilities", 
        "Entertainment", "Shopping", "Personal Care", "Health & Fitness",
        "Education", "Travel", "Gifts & Donations", "Other"
    ]

    existing_categories = {c.name for c in Category.query.all()}
    
    for category_name in default_categories:
        if category_name not in existing_categories:
            new_category = Category(name=category_name)
            db.session.add(new_category)
    
    db.session.commit()
