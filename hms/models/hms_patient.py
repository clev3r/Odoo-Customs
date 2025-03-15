from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import ValidationError
import re


class hmsPatient(models.Model):
    _name = "hms.patient"
    _rec_name = "first_name"
    _description = 'Patient'

    first_name = fields.Char(required=True)
    last_name = fields.Char(required=True)
    email = fields.Char(string="Email", required=True)
    birth_date = fields.Date()
    age = fields.Integer(compute='_compute_age', store=True)
    address = fields.Text()
    blood_type = fields.Selection([('a', 'A'),
                                   ('b', 'B'),
                                   ('ab', 'AB'),
                                   ('o', 'O')])
    cr_ratio = fields.Float(string="CR Ratio")
    history = fields.Html()
    pcr = fields.Boolean(string="PCR", default=False)
    image = fields.Binary()
    doctor_ids = fields.Many2many("hms.doctor", "hms_doctor_patient_rel", "patient_id", "doctor_id", string="Doctors")
    department_id = fields.Many2one("hms.department")
    department_capacity = fields.Integer(related="department_id.capacity")
    log_history = fields.One2many('hms.patient.log', 'patient_id', string='Log History')
    patient_state = fields.Selection([('un', 'Undetermined'),
                                      ('g', 'Good'),
                                      ('f', 'Fair'),
                                      ('s', 'Serious')], default='un')

    @api.constrains('email')
    def _check_email_valid_and_unique(self):
        for record in self:
            # Check if the email is valid (basic email regex pattern)
            email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
            if record.email and not re.match(email_regex, record.email):
                raise ValidationError(f"The email address '{record.email}' is not valid.")

            # Check if the email is unique in the patient records
            if self.search_count([('email', '=', record.email)]) > 1:
                raise ValidationError(f"The email address '{record.email}' is already associated with another patient.")

    @api.depends('birth_date')
    def _compute_age(self):
        for record in self:
            if record.birth_date:
                today = datetime.today()
                birth_date = fields.Date.from_string(record.birth_date)
                record.age = today.year - birth_date.year - (
                        (today.month, today.day) < (birth_date.month, birth_date.day))
            else:
                record.age = 0

    @api.onchange('age')
    def _on_change_age(self):
        if 30 > self.age >= 1:
            self.pcr = True
            return {
                'warning': {
                    'title': 'Warning',
                    'message': 'PCR has been checked!'  # PROBLEMAAAAAAAAAAA
                }
            }
        else:
            self.pcr = False

    @api.model
    def create(self, vals):
        # Create the patient and log if 'patient_state' is passed in the values
        patient = super(hmsPatient, self).create(vals)
        if 'patient_state' in vals:
            state_name = dict(self._fields["patient_state"].selection).get(vals.get('patient_state'), "Unknown")
            self.env['hms.patient.log'].create({
                'patient_id': patient.id,
                'description': f'State changed to {state_name}',
                'create_uid': self.env.user.id,
                'create_date': fields.Datetime.now(),
            })
        return patient

    def write(self, vals):
        # Track patient state changes
        if 'patient_state' in vals:
            state_name = dict(self._fields["patient_state"].selection).get(vals.get('patient_state'), "Unknown")
            self.env['hms.patient.log'].create({
                'patient_id': self.id,
                'description': f'State changed to {state_name}',
                'create_uid': self.env.user.id,
                'create_date': fields.Datetime.now(),
            })
        return super(hmsPatient, self).write(vals)


class HMSPatientLog(models.Model):
    _name = 'hms.patient.log'
    _description = 'Patient Log'

    patient_id = fields.Many2one('hms.patient', string='Patient')
    create_uid = fields.Many2one('res.users', string='Created By', readonly=True)
    create_date = fields.Datetime(string='Created On', readonly=True)
    description = fields.Text(string='Description')
