from flask import Blueprint,request,flash,session,redirect,url_for,render_template
from . import mongo,mail
from .model import User
import uuid
from bson.binary import Binary

auth = Blueprint("auth",__name__)




@auth.route("/signup",methods=["GET","POST"])
def signup():
    if request.method == "POST":

        data = request.form
        print(data)
        name = data["name"]
        email = data["email"]
        hospital = data["hospital"]
        role = data["role"]
        password = data["password"]
        user_uuid = str(uuid.uuid4()) #generates uuid for identification purpose, will be unique for all users
        
        data = mongo.db.user.find_one({"user_id":user_uuid})
        while data:
            user_uuid = str(uuid.uuid4())
            data = mongo.db.user.find_one({"user_id":user_uuid})
        user = mongo.db.user.find_one({"email":email})
        if user:
            print("user found")
            flash("User with this mail already exists. Try login in.","error")
            return render_template("signup.html")
        
        session["role"] = role
        session["hospital"] = hospital
        session["email"] = email
        session["user_id"] = user_uuid
        mongo.db.user.insert_one({
            "name":name,
            "email":email,
            "role":role,
            "hospital":hospital,
            "password":password,
            "user_id":user_uuid,
        })
        if role == "doctor":
            mongo.db.doctor.insert_one({
                "name":name,
                "email":email,
                "doctor_id":user_uuid,
                "hospital":hospital,
                "patient_ids":[]
            })
            
        elif role == "nurse":
            mongo.db.nurse.insert_one({
                "name":name,
                "email":email,
                "nurse_id":user_uuid,
                "hospital":hospital,
                "patient_ids":[]
            })
            
            
        else:
            mongo.db.inventory_manager.insert_one({
                "name":name,
                "manager_id":user_uuid,
                "hospital":hospital
            })
        return redirect(url_for("routes.dashboard")) 
    else:    
        return render_template("signup.html")      


    


@auth.route("/login",methods=["GET","POST"])
def login():
    if request.method == "POST":
        data = request.form
        email = data["email"]
        password = data["password"]

        user = mongo.db.user.find_one({
            "email":email,
            "password":password
        })
        if user:
            session["name"] = user["name"]
            session["email"] = email
            session["role"] = user["role"]
            session["hospital"] = user["hospital"]
            session["user_id"] = user["user_id"]
    
            return redirect(url_for("routes.dashboard"))



        else:
            flash("User doesn't exists. Kindly sign up.","error")
            return render_template("login.html")
    else:
        return render_template("login.html")
    

@auth.route("/logout",methods=["GET"])
def logout():
    session.clear()
    return render_template("index.html")
    


    





        

