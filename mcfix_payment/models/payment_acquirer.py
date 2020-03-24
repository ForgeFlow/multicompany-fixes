from odoo import api, models, _
from odoo.exceptions import ValidationError


class PaymentAcquirer(models.Model):
    _inherit = 'payment.acquirer'

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if not self.journal_id.check_company(self.company_id):
            self.journal_id = False

    @api.multi
    @api.constrains('company_id', 'journal_id')
    def _check_company_id_journal_id(self):
        for rec in self.sudo():
            if not rec.journal_id.check_company(rec):
                raise ValidationError(
                    _('The Company in the Payment Acquirer and in '
                      'Account Journal must be the same.'))
