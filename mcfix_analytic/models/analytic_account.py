from odoo import api, models, _
from odoo.exceptions import ValidationError


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        names = super(AccountAnalyticAccount, self).name_get()
        res = self.add_company_suffix(names)
        return res

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if not self.partner_id.check_company(self.company_id):
            self.partner_id = False

    @api.multi
    @api.constrains('company_id', 'partner_id')
    def _check_company_id_partner_id(self):
        for rec in self.sudo():
            if not rec.partner_id.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Account Analytic Account and in '
                      'Res Partner must be the same.'))

    @api.constrains('company_id')
    def _check_company_id_out_model(self):
        self._check_company_id_base_model()

    def _check_company_id_fields(self):
        res = super()._check_company_id_fields()
        res += [self.line_ids, ]
        return res


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    @api.multi
    @api.constrains('company_id', 'account_id')
    def _check_company_id_account_id(self):
        for rec in self.sudo():
            if not rec.account_id.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Account Analytic Line and in '
                      'Account Analytic Account must be the same.'))
