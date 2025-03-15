from email.policy import default

from odoo import fields, models, api


class PurchaseRequest(models.Model):
    _name = "purchase.request"
    _description = "Purchase Request"

    name = fields.Char(string="name", required=True)
    request_by = fields.Many2one('res.users', string='User', required=True, default=lambda self: self.env.user)
    start_date = fields.Date(string='Start Date', default=fields.Date.today)
    end_date = fields.Date(string='End Date')
    rejection_reason = fields.Text(string="Rejection Reason", readonly=True)
    order_lines = fields.One2many('purchase.request.line', 'order_id', string='Order Lines')
    total_price = fields.Float(string='Total Price', compute='_compute_total_price', store=True)
    status = fields.Selection([
        ('draft', 'Draft'),
        ('to_approve', 'To be Approved'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', readonly=True, copy=False)

    def submit_to_approve(self):
        for rec in self:
            rec.status = 'to_approve'

    def cancel_order(self):
        for rec in self:
            rec.status = 'cancelled'

    def approve_order(self):
        """Approve the order and send email notification to purchase managers."""
        for rec in self:
            rec.status = 'approved'

            # Find all users in the 'Purchase Manager' group
            group = self.env.ref('purchase.group_purchase_manager')  # Odoo Purchase Manager group
            users = group.users.filtered(lambda u: u.email)  # Get users with valid emails

            if not users:
                raise UserError("No purchase managers have valid emails configured!")

            # Prepare email details
            recipient_emails = ','.join(users.mapped('email'))
            subject = f"Purchase Request {rec.name} Approved"
            body = f"""
                       <p>Hello,</p>
                       <p>The purchase request <b>{rec.name}</b> has been approved.</p>
                       <p>Requested by: {rec.request_by.name}</p>
                       <p>Total Price: {rec.total_price}</p>
                       <p>Best Regards,</p>
                       <p>Your Company</p>
                   """

            # Create and send the email
            mail_values = {
                'subject': subject,
                'body_html': body,
                'email_to': recipient_emails,
                'email_from': self.env.user.email or 'noreply@yourcompany.com',  # Ensure valid sender email
            }
            mail = self.env['mail.mail'].create(mail_values)
            mail.send()

    def reject_order(self):
        """Open the rejection wizard instead of directly rejecting."""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Reject Purchase Request',
            'res_model': 'purchase.request.reject.wizard',
            'view_mode': 'form',
            'target': 'new',  # Opens as a popup
            'context': {'active_id': self.id},
        }

    def reset_draft(self):
        for rec in self:
            rec.status = 'draft'

    @api.depends('order_lines.total')
    def _compute_total_price(self):
        for order in self:
            order.total_price = sum(order.order_lines.mapped('total'))


class PurchaseRequestLine(models.Model):
    _name = 'purchase.request.line'

    product_id = fields.Many2one('product.product', string='Product', required=True)
    description = fields.Char(string='Description', related='product_id.name')
    quantity = fields.Float(string='Quantity', default=1)
    cost_price = fields.Float(string='Price', readonly=True, related='product_id.lst_price')
    total = fields.Float(string='Total', compute='_compute_total', store=True)

    order_id = fields.Many2one('purchase.request', string='Order')

    @api.depends('quantity', 'cost_price')
    def _compute_total(self):
        for line in self:
            line.total = line.quantity * line.cost_price
