from odoo import models, fields, api

class PurchaseRequestRejectWizard(models.TransientModel):
    _name = "purchase.request.reject.wizard"
    _description = "Purchase Request Rejection Wizard"

    rejection_reason = fields.Text(string="Rejection Reason", required=True)

    def action_confirm_reject(self):
        """Set the rejection reason and update the status of the purchase request."""
        context = self.env.context
        active_id = context.get('active_id')  # Get the active purchase request ID

        if active_id:
            purchase_request = self.env['purchase.request'].browse(active_id)
            purchase_request.write({
                'status': 'rejected',
                'rejection_reason': self.rejection_reason
            })
