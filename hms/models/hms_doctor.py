from odoo import models, fields,api

class hmsDoctor(models.Model):
    _name = "hms.doctor"
    _rec_name = "full_name"

    first_name = fields.Char(string="First Name", required=True)
    last_name = fields.Char(string="Last Name", required=True)
    image = fields.Binary(string="Image")
    patient_ids = fields.Many2many("hms.patient", "hms_doctor_patient_rel", "doctor_id", "patient_id", string="Patients")
    full_name = fields.Char(compute="_compute_full_name", store=True)



    @api.depends('first_name', 'last_name')
    def _compute_full_name(self):
        for record in self:
            record.full_name = f"{record.first_name} {record.last_name}"

