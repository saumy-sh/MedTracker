from marshmallow import Schema, fields
from datetime import datetime


 
class User(Schema):
    name = fields.String(required=True)
    email = fields.Email()
    organisation = fields.String(required=True)
    role = fields.String(required=True)
    password = fields.String(required=True)
    user_id = fields.UUID(required=True,default=None)

class InventoryMedicine(Schema):
    name = fields.String(required=True)
    batch_no = fields.String(required=True)
    quantity = fields.Integer(required=True)
    threshold = fields.Integer(required=True)  # Low stock alert level
    unit = fields.String(required=True)  # Tablets, Capsules, etc.
    expiry_date = fields.String(required=True)
    supplier = fields.String(required=True)
    last_updated = fields.DateTime(default=datetime.now())  
    manager_id = fields.UUID() #stores inventory managers id

class InventoryManager(Schema):
    name = fields.String(required=True)
    manager_id = fields.UUID(required=True)
    # inventory = fields.List() # stores medicine_id

class Doctor(Schema):
    name = fields.String(required=True)
    email = fields.Email()
    doctor_id = fields.UUID(required=True)
    patient_ids = fields.List()
    # hospital_id = fields.UUID(required=True)


class PatientMedication(Schema):
    """ Schema for individual patient medication details """

    name = fields.String(required=True)
    dosage = fields.String(required=True)
    frequency = fields.Integer(required=True)
    start_date = fields.String(required=True)
    end_date = fields.String(required=True)
    prescribed_by = fields.UUID(required=True) #references doctor's id

class Patient(Schema):
    """ Schema for individual patients """
    name = fields.String(required=True)
    patient_id = fields.UUID(required=True)
    age = fields.Integer()
    gender = fields.String()
    doctor_id = fields.UUID(required=True)
    medications = fields.Dict(keys=fields.String(), values=fields.List(fields.Nested(PatientMedication))) 



