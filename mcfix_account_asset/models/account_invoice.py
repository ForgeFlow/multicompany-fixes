from odoo import api, models, _
from odoo.exceptions import ValidationError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.constrains('company_id')
    def _check_company_id_out_model(self):
        super(AccountInvoice, self)._check_company_id_out_model()
        if not self.env.context.get('bypass_company_validation', False):
            for rec in self:
                if not rec.company_id:
                    continue
                field = self.env['account.asset.asset'].search(
                    [('invoice_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Account Invoice is assigned to Account Asset Asset '
                          '(%s).' % field.name_get()[0][1]))


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.multi
    @api.constrains('company_id', 'asset_category_id')
    def _check_company_id_asset_category_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.asset_category_id.company_id and\
                    rec.company_id != rec.asset_category_id.company_id:
                raise ValidationError(
                    _('The Company in the Account Invoice Line and in '
                      'Account Asset Category must be the same.'))
