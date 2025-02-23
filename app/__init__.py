from flask import Flask
from dotenv import load_dotenv
import os
from flask_pymongo import PyMongo
from flask_mail import Mail,Message
import json
from flask_apscheduler import APScheduler
from datetime import datetime


mail = Mail()
mongo = PyMongo(maxPoolSize=50,   # Maximum number of connections
    minPoolSize=10,   # Minimum number of connections
    maxIdleTimeMS=120000  # Time before a connection is closed if idle
    )
scheduler = APScheduler()


def send_email_alert(low_stock, finished, expired, expiring_soon,manager_email):
    """Send an email notification to the manager."""

    subject = "🚨 Medicine Inventory Alert 🚨"
    body = "The following medicines require attention:\n\n"

    if low_stock:
        body += "⚠️ **Low Stock Medicines:**\n" + "\n".join(low_stock) + "\n\n"
    if expired:
        body += "❗❗ **Low Stock Medicines:**\n" + "\n".join(expired) + "\n\n"
    if finished:
        body += "❗❗ **Low Stock Medicines:**\n" + "\n".join(finished) + "\n\n"
    if expiring_soon:
        body += "⏳ **Expiring Soon Medicines:**\n" + "\n".join(expiring_soon) + "\n\n"

    body += "Please take necessary actions.\n\nBest Regards,\nMedicine Inventory System"

    msg = Message(subject, recipients=[manager_email])
    msg.body = body
    mail.send(msg)
    print("Email sent to manager successfully!")


def fetch_medicine_data(manager_id):
    """Fetch medicine data from MongoDB."""
    medicines = mongo.db.inventory_medicine.find({"manager_id":manager_id}, {"name": 1, "quantity": 1, "threshold": 1, "expiry_date": 1, "manager_id":1})
    return list(medicines)

def check_medicines():
    """Check if any medicines are low on stock or expiring soon and send an alert."""
    managers = mongo.db.user.find({"role":"inventory_manager"},{"name":1,"email":1,"user_id":1})

    for manager in managers:


        medicines = fetch_medicine_data(manager["user_id"])
        low_stock_medicines = []
        expiring_medicines = []
        expired_medicines = []
        finished_medicines = []

        current_time = datetime.now()  # Get the current date and time

        for med in medicines:
            name = med.get("name")
            quantity = med.get("quantity")
            threshold = med.get("threshold")
            expiry_date_str = med.get("expiry_date")

            try:
                expiry_date = datetime.strptime(expiry_date_str, "%Y-%m-%d")
                days_to_expiry = (expiry_date - current_time).days  # Get difference in days
            except (ValueError, TypeError):
                continue  # Skip if expiry_date format is incorrect

            if quantity <= threshold:
                mongo.db.inventory_medicine.update_one({"name":name,"manager_id":manager["user_id"]},
                                                       {"$set":{
                                                           "status":"Low Stock"
                                                       }})
                low_stock_medicines.append(f"{name} (Only {quantity} left)")
            elif quantity <=0:
                mongo.db.inventory_medicine.update_one({"name":name,"manager_id":manager["user_id"]},
                                                       {"$set":{
                                                           "status":"Not Available"
                                                       }})
                finished_medicines.append(f"{name} (Stock over)")

            if 0 <= days_to_expiry < 5:  # If expiry is within 5 days
                expiring_medicines.append(f"{name} (Expiring in {days_to_expiry} days)")
            elif days_to_expiry <= 0:
                # mongo.db.inventory_medicine.update_one({"name":name,"manager_id":manager["user_id"]},
                #                                        {"$set":{
                #                                            "status":"Expired"
                #                                        }})
                expired_medicines.append(f"{name} (Expired)")

        if low_stock_medicines or expiring_medicines:
            send_email_alert(low_stock_medicines, finished_medicines, expired_medicines, expiring_medicines,manager["email"])


def create_app():

    app = Flask(__name__)
    load_dotenv()

    # Replace with your actual credentials
    app.config["MONGO_URI"] = os.getenv("MONGO_URL")
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
    

    app.register_blueprint(auth, url_prefix = "/")
    app.register_blueprint(routes, url_prefix = "/")
    
    mongo.init_app(app)
    mail.init_app(app)
    scheduler.init_app(app)
    
    def check_medicines_job():
        """Wrapper function to run check_medicines() inside the Flask app context."""
        with app.app_context():
            check_medicines()

    scheduler.add_job(id="medicine_check", func=check_medicines_job, trigger="cron", hour=9, minute=0)
    scheduler.start()

    return app

