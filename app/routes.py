from flask import Blueprint,request,flash,session,redirect,url_for,render_template,Response
from . import mongo
from datetime import datetime

routes = Blueprint("routes",__name__)

@routes.route("/",methods=["GET"])
def main_page():
    session.clear()
    return render_template("index.html")

@routes.route("/dashboard",methods = ["GET","POST"])
def dashboard():
    print(session)
    if session["role"] == "inventory_manager":
        return redirect("inventory_manager/fetch_data")
    elif session["role"] == "doctor":
        return redirect("doctor/fetch_data")
    elif session["role"] == "nurse":
        return redirect("nurse/fetch_data")
    else:
        return "Fetching wrong data"


# inventory manager routes
@routes.route("/inventory_manager/fetch_data",methods=["GET"])
def fetch_data():


    manager_id = session["user_id"]
    medicines = mongo.db.inventory_medicine.find({"manager_id":manager_id},{"_id":0,"usage_history":0})
    medicine_lst = []
    for i in medicines:
        medicine_lst.append(i)
    print(medicines)
    print(medicine_lst)
    
    return render_template("dashboard.html",medicines=medicine_lst)


@routes.route("/inventory_manager/fetch_usage_history",methods=["GET"])
def usage_history():
    medicine_name = request.args.get("name")
    medicine_data = mongo.db.inventory_medicine.find_one({
        "manager_id":session["user_id"],
        "name":medicine_name                     
        },
        {"_id":0}
    )
    return render_template("medicine_data.html",medicine=medicine_data,
                           usage_data = medicine_data["usage_history"])



@routes.route("/inventory_manager/delete", methods=["GET","POST"])
def delete_medicine():
    name = request.args.get("name")  # Get the medicine name from the form

    result = mongo.db.inventory_medicine.delete_one({"name": name,"manager_id":session["user_id"]})

    if result.deleted_count > 0:
        flash(f"Medicine '{name}' has been deleted successfully.", "success")
    else:
        flash(f"Medicine '{name}' not found!", "error")

    return redirect(url_for("routes.dashboard"))




@routes.route("/inventory_manager/update_medicine", methods=["POST"])
def update_medicine():
    name = request.form["name"]
    quantity = int(request.form["quantity"])  # New quantity
    threshold = int(request.form["threshold"])
    expiry_date = request.form["expiry_date"]
    cost_per_unit = float(request.form["cost_per_unit"])
    stock_status = request.form["stock_status"]  # 'increase' or 'decrease'

    # Fetch existing medicine data
    medicine_data = mongo.db.inventory_medicine.find_one(
        {"manager_id": session["user_id"], "name": name}
    )
    try:
        

        if not medicine_data:
            flash("Medicine not found!", "error")
            return render_template("medicine_data.html",medicine=medicine_data,
                           usage_data = medicine_data["usage_history"])

        previous_quantity = medicine_data["quantity"]  # Old quantity

        # Ensure correct stock status (Increase or Decrease)
        if stock_status == "increase":
            new_quantity = previous_quantity + quantity
        elif stock_status == "decrease":
            if quantity > previous_quantity:
                flash("Cannot decrease more than available stock!", "error")
                return render_template("medicine_data.html",medicine=medicine_data,
                           usage_data = medicine_data["usage_history"])
            new_quantity = previous_quantity - quantity
        else:
            flash("Invalid stock status!", "error")
            return render_template("medicine_data.html",medicine=medicine_data,
                           usage_data = medicine_data["usage_history"])

        # Update medicine data
        result = mongo.db.inventory_medicine.update_one(
            {"name": name, "manager_id": session["user_id"]},
            {"$set": {
                "quantity": new_quantity,
                "threshold": threshold,
                "expiry_date": expiry_date,
                "cost_per_unit": cost_per_unit,
                "last_update": datetime.now().strftime("%Y-%m-%d")
            },
            "$push": {  # Add entry to usage_history
                "usage_history": {
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "quantity_used": quantity,
                    "stock_status": stock_status,
                    "total_quantity":new_quantity
                }
            }}
        )
        # fetching updated fetch_data
        medicine_data = mongo.db.inventory_medicine.find_one(
            {"manager_id": session["user_id"], "name": name}
        )
        

    except Exception as e:
        print(e)
        flash(f"Error updating medicine!", "error")

    return render_template("medicine_data.html",medicine=medicine_data,
                           usage_data = medicine_data["usage_history"])


@routes.route("/inventory_manager/add_medicine", methods=["POST"])
def add_medicine():
    try:
        # Extract form data
        name = request.form.get("name").strip()
        type_ = request.form.get("type")
        quantity = int(request.form.get("quantity"))
        threshold = int(request.form.get("threshold"))
        units = request.form.get("units").strip()
        expiry_date = request.form.get("expiry_date")
        cost_per_unit = float(request.form.get("cost_per_unit"))

        # Validate input
        if not name or not type_ or not units or quantity < 0 or threshold < 0 or cost_per_unit < 0:
            flash("Invalid input. Please fill all fields correctly.", "error")
            return redirect(url_for("routes.dashboard"))

        # Convert expiry date to datetime format
        expiry_date = datetime.strptime(expiry_date, "%Y-%m-%d").strftime("%Y-%m-%d")
        print(expiry_date)

        # Check if medicine already exists
        existing_medicine = mongo.db.inventory_medicine.find_one({"name": name})
        if existing_medicine:
            flash("Medicine already exists!", "error")
            return render_template("dashboard.html")

        # Insert into MongoDB
        mongo.db.inventory_medicine.insert_one({
            "name": name,
            "type": type_,
            "quantity": quantity,
            "threshold": threshold,
            "units": units,
            "expiry_date": expiry_date,
            "last_update": datetime.now().strftime("%Y-%m-%d"),
            "cost_per_unit": cost_per_unit,
            "status":"Available",
            "usage_history":[],
            "manager_id":session["user_id"]
        })

        flash("Medicine added successfully!", "success")

    except Exception as e:
        print(e)
        print(session["user_id"])
        flash("Error adding new medicine!", "error")
    finally:
        return redirect(url_for("routes.dashboard"))
    


@routes.route("/inventory_manager/export_csv")
def export_csv():
    medicines = mongo.db.inventory_medicine.find({"manager_id":session["user_id"]},{"_id":0,"usage_history":0})  # Replace with actual DB query function

    # Define CSV headers
    csv_headers = ["Name", "Type", "Quantity", "Threshold", "Units", "Expiry Date", "Last Update", "Cost/Unit"]

    # Create CSV data
    def generate():
        yield ",".join(csv_headers) + "\n"  # Write headers
        for med in medicines:
            expiry_date = f'"{med["expiry_date"]}"'  # Wrap in quotes
            last_update = f'"{med["last_update"]}"'  # Wrap in quotes
            yield f'{med["name"]},{med["type"]},{med["quantity"]},{med["threshold"]},{med["units"]},{expiry_date},{last_update},{med["cost_per_unit"]}\n'

    # Send CSV file as response
    return Response(generate(), mimetype="text/csv", headers={"Content-Disposition": "attachment; filename=medicine_inventory.csv"})

    


