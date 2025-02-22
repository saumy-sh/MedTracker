from flask import Blueprint,request,flash,session,redirect,url_for,render_template
from . import mongo,mail
from .model import User
import uuid

auth = Blueprint("auth",__name__)

auth.route("/signup",methods=["GET","POST"])
def signup():
    if request.method == "POST":
        data = request.form
        name = data["name"]
        email = data["email"]
        org = data["organisation"]
        role = data["role"]
        password = data["password"]
        uuid = uuid.uuid4() #generates uuid for identification purpose, will be unique for all users
        
        data = mongo.db.user.find_one({"id":uuid})
        while data:
            uuid = uuid.uuid4()
            data = mongo.db.userdata.find_one({"id":uuid})

        mongo.db.user.insert_one({
            "name":name,
            "email":email,
            "role":role,
            "organisation":org,
            "password":password,
            "user_id":uuid,
        })
        if role == "doctor":
            mongo.db.doctor.insert_one({
                "name":name,
                "email":email,
                "patient_ids":[],
                "doctor_id":uuid
            })
        elif role == "patient":
            mongo.db.patient.insert_one({
                "name":name,
                "email":email,
                "patient_id":uuid,
                "doctor_id":None,
                "age":data["age"],
                "gender":data["gender"]
            })
        else:
            mongo.db.inventory_manager.insert_one({
                "name":name,
                "manager_id":uuid
            })

        

