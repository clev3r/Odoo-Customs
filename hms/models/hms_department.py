from odoo import models, fields

class hmsDepartment(models.Model):
    _name = "hms.department"

    name = fields.Char(string="Name")
    capacity = fields.Integer(string="Capacity")
    is_open = fields.Boolean(string="Open")
    patient_id = fields.One2many("hms.patient", "department_id", string="Patients")