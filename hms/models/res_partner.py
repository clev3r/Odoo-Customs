from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    related_patient_id = fields.Many2one('hms.patient', string='Related Patient', help="Link to the related patient")
    vat = fields.Char(string='Tax ID')

    @api.constrains('email')
    def _check_email_in_patient_model(self):
        for partner in self:
            if partner.email:
                existing_patient = self.env['hms.patient'].search([('email', '=', partner.email)], limit=1)
                if existing_patient:
                    patient_name = existing_patient.first_name or existing_patient.last_name or "Unknown"
                    raise ValidationError(
                        "This email is already linked to a patient: %s" % patient_name
                    )

    @api.constrains('customer_rank', 'vat')  # Replace 'customer' with 'customer_rank'
    def _check_vat_for_customer(self):
        for partner in self:
            if partner.customer_rank > 0 and not partner.vat:  # Check if the partner is a customer
                raise ValidationError('Tax ID (VAT) is mandatory for CRM customers.')

    def unlink(self):
        for partner in self:
            if partner.related_patient_id:
                raise ValidationError("You cannot delete a customer that is linked to a patient.")
        return super(ResPartner, self).unlink()
