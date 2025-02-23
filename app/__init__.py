from flask import Flask
from dotenv import load_dotenv
import os
from flask_pymongo import PyMongo
from flask_mail import Mail,Message
import json
from flask_apscheduler import APScheduler


mail = Mail()
mongo = PyMongo(maxPoolSize=50,   # Maximum number of connections
    minPoolSize=10,   # Minimum number of connections
    maxIdleTimeMS=120000  # Time before a connection is closed if idle
    )
scheduler = APScheduler()




def create_app():

    app = Flask(__name__)
    load_dotenv()

    # Replace with your actual credentials
    app.config["MONGO_URI"] = os.getenv("DATABASE_URI")
    app.config["SECRET_KEY"] = os.urandom(24)

    # Mailtrap configuration
    app.config['MAIL_SERVER']='smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USERNAME'] = os.getenv("GMAIL-ACCOUNT")
    app.config['MAIL_PASSWORD'] = os.getenv("PASS-KEY")
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv("GMAIL-ACCOUNT")

    # Scheduler configuration
    app.config['SCHEDULER_API_ENABLED'] = True

    

    # @app.template_filter('json_loads')
    # def json_loads_filter(s):
    #     return json.loads(s)

    from .auth import auth
    from .routes import routes
    # from .doctor import doctor
    # from .nurse import nurse
    # from .inventory_manager import inventory_manager

    app.register_blueprint(auth, url_prefix = "/")
    app.register_blueprint(routes, url_prefix = "/")
    
    mongo.init_app(app)
    mail.init_app(app)
    scheduler.init_app(app)
    # scheduler.start()

           

        


    return app

