from odoo import api, fields, models


class PaymentAcquirer(models.Model):
    _inherit = 'payment.acquirer'
    _check_company_auto = True

    journal_id = fields.Many2one(check_company=True)

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if not self.journal_id.check_company(self.company_id):
            self.journal_id = False
