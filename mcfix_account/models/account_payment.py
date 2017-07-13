from odoo import models, fields, api


class AccountPayment(models.Model):
    _inherit = "account.payment"

    company_id = fields.Many2one(store=True, readonly=False,
                                 related=False, required=True)

    @api.onchange('payment_type', 'company_id')
    def _onchange_payment_type(self):
        res = super(AccountPayment, self)._onchange_payment_type()
        res['domain']['journal_id'].append(('company_id', '=',
                                            self.company_id.id))
        return res

    @api.model
    def create(self, vals):
        if 'company_id' not in vals:
            journal_id = vals.get('journal_id')
            journal = self.env['account.journal'].browse(journal_id)
            vals['company_id'] = journal.company_id.id
        return super(AccountPayment, self).create(vals)
