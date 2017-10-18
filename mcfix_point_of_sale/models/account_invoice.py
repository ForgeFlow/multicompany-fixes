from odoo import api, models, _
from odoo.exceptions import ValidationError


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.constrains('company_id')
    def _check_company_id(self):
        super(AccountInvoice, self)._check_company_id()
        for rec in self:
            order = self.env['pos.order'].sudo().search(
                [('invoice_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if order:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Invoice is assigned to Pos Order '
                      '%s.' % order.name))
