from marshmallow import Schema, fields
from datetime import datetime
import uuid


 
class User(Schema):
    name = fields.String(required=True)
    email = fields.Email()
    hospital = fields.String(required=True)
    role = fields.String(required=True)
    password = fields.String(required=True)
    user_id = fields.String(required=True,default=uuid.uuid4())

class UsageHistory(Schema):
    """Schema to store medicine usage history"""
    date = fields.String(required=True)
    quantity_used = fields.Integer(required=True)
    stock_status = fields.String(required=True)
    total_quantity = fields.Integer()

class InventoryMedicine(Schema):
    name = fields.String(required=True)
    type = fields.String(required=True)
    # batch_no = fields.String(required=True)
    quantity = fields.Integer(required=True)
    threshold = fields.Integer(required=True)  # Low stock alert level
    units = fields.String(required=True)  # Tablets, Capsules, etc.
    expiry_date = fields.String(required=False,default="null")
    # supplier = fields.String(required=True)
    last_updated = fields.DateTime(default=datetime.now)  
    cost_per_unit = fields.Integer()
    status = fields.String()
    usage_history = fields.List(fields.Nested(UsageHistory),required=False,default=[])
    manager_id = fields.String() #stores inventory managers id so that respective hospital's inventory can be recognised

class InventoryManager(Schema):
    name = fields.String(required=True)
    hospital = fields.String(required=True)
    manager_id = fields.String(required=True)
    email = fields.Email(required=True)
    # inventory = fields.List() # stores medicine_id

class Doctor(Schema):
    name = fields.String(required=True)
    hospital = fields.String(required=True)
    email = fields.Email(required=True)
    doctor_id = fields.String(required=True)
    patient_ids = fields.List(fields.String(),default=[])
    # hospital_id = fields.UUID(required=True)

class Nurse(Schema):
    name = fields.String(required=True)
    hospital = fields.String(required=True)
    email = fields.Email(required=True)
    patient_ids = fields.List(fields.String(),default=[])
    nurse_id = fields.String(required=True)



class PatientMedication(Schema):
    """ Schema for individual patient medication details """

    name = fields.String(required=True)
    dosage = fields.String(required=True)
    frequency = fields.Integer(required=True)
    time = fields.List(fields.Time(),required=True)
    start_date = fields.String(required=True)
    end_date = fields.String(required=True)
    prescribed_by = fields.String(required=True) #references doctor's id

class Patient(Schema):
    """ Schema for individual patients """
    name = fields.String(required=True)
    patient_id = fields.UUID(required=True)
    age = fields.Integer()
    gender = fields.String()
    doctor_id = fields.String(required=True)
    assigned_nurse = fields.String(required=True)
    medications = fields.List(fields.Nested(PatientMedication),required = False) 



