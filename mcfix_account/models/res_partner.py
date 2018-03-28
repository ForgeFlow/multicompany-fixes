from odoo import api, models, _
from odoo.exceptions import ValidationError


class AccountFiscalPosition(models.Model):
    _inherit = 'account.fiscal.position'

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if self.company_id and self.tax_ids:
            for tax in self.tax_ids:
                if tax.tax_src_id.company_id and \
                        tax.tax_src_id.company_id != self.company_id:
                    tax.tax_src_id = False
                if tax.tax_dest_id.company_id and \
                        tax.tax_dest_id.company_id != self.company_id:
                    tax.tax_dest_id = False
        if self.company_id and self.account_ids:
            for account in self.account_ids:
                if account.account_src_id.company_id and \
                        account.account_src_id.company_id != self.company_id:
                    account.account_src_id = False
                if account.account_dest_id.company_id and \
                        account.account_dest_id.company_id != self.company_id:
                    account.account_dest_id = False

    @api.multi
    @api.constrains('company_id', 'tax_ids')
    def _check_company_id_tax_ids(self):
        for rec in self.sudo():
            for line in rec.tax_ids:
                if rec.company_id and line.tax_src_id.company_id and\
                        rec.company_id != line.tax_src_id.company_id:
                    raise ValidationError(
                        _('The Company in the Account Fiscal Position and in '
                          'Account Tax (%s) must be the same.'
                          ) % line.tax_src_id.name_get()[0][1])
            for line in rec.tax_ids:
                if rec.company_id and line.tax_dest_id.company_id and\
                        rec.company_id != line.tax_dest_id.company_id:
                    raise ValidationError(
                        _('The Company in the Account Fiscal Position and in '
                          'Account Tax (%s) must be the same.'
                          ) % line.tax_dest_id.name_get()[0][1])

    @api.multi
    @api.constrains('company_id', 'account_ids')
    def _check_company_id_account_ids(self):
        for rec in self.sudo():
            for line in rec.account_ids:
                if rec.company_id and line.account_src_id.company_id and\
                        rec.company_id != line.account_src_id.company_id:
                    raise ValidationError(
                        _('The Company in the Account Fiscal Position and in '
                          'Account Account (%s) must be the same.'
                          ) % line.account_src_id.name_get())
            for line in rec.account_ids:
                if rec.company_id and line.account_dest_id.company_id and\
                        rec.company_id != line.account_dest_id.company_id:
                    raise ValidationError(
                        _('The Company in the Account Fiscal Position and in '
                          'Account Account (%s) must be the same.'
                          ) % line.account_dest_id.name_get())

    @api.constrains('company_id')
    def _check_company_id_out_model(self):
        self._check_company_id_base_model()

    def _check_company_id_search(self):
        res = super()._check_company_id_search()
        res.append(('account.invoice', [('fiscal_position_id', '=', self.id)]))
        return res


class Partner(models.Model):
    _inherit = 'res.partner'

    def _check_company_id_search(self):
        res = super()._check_company_id_search()
        res = res + [
            ('account.invoice', [('partner_id', '=', self.id)]),
            ('account.invoice', [('commercial_partner_id', '=', self.id)]),
            ('account.analytic.line', [('partner_id', '=', self.id)]),
            ('account.invoice.line', [('partner_id', '=', self.id)]),
            ('account.bank.statement.line', [('partner_id', '=', self.id)]),
            ('account.move', [('partner_id', '=', self.id)]),
            ('account.move.line', [('partner_id', '=', self.id)]),
            ('account.payment', [('partner_id', '=', self.id)]),
        ]
        return res
