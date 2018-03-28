from odoo import api, models, _
from odoo.exceptions import ValidationError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def _check_company_id_search(self):
        res = super()._check_company_id_search()
        res += [
            ('account.asset.asset', [('invoice_id', '=', self.id)]),
        ]
        return res


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.multi
    @api.constrains('company_id', 'asset_category_id')
    def _check_company_id_asset_category_id(self):
        for rec in self.sudo():
            if not rec.asset_category_id.company_id.check_company(
                rec.company_id
            ):
                raise ValidationError(
                    _('The Company in the Account Invoice Line and in '
                      'Account Asset Category must be the same.'))
