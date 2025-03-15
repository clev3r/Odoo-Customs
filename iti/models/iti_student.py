from odoo import models, fields


class itiStudent(models.Model):
    _name = "iti.student"

    name = fields.Char(required=True)
    birth_date = fields.Date()
    salary = fields.Float()
    address = fields.Text()
    gender = fields.Selection([('m', "Male"), ('f', "Female")]
                              )
    accepted = fields.Boolean()
    level = fields.Integer()
    image = fields.Binary()
    cv = fields.Html()
    login_time = fields.Datetime()
    track_id = fields.Many2one("iti.track")
    skills_ids = fields.Many2many("iti.skill")
    track_capacity = fields.Integer(related="track_id.capacity")