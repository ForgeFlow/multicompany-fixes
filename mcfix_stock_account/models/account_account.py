from odoo import api, models, _
from odoo.exceptions import ValidationError


class AccountAccount(models.Model):
    _inherit = "account.account"

    @api.constrains('company_id')
    def _check_company_id_out_model(self):
        super(AccountAccount, self)._check_company_id_out_model()
        if not self.env.context.get('bypass_company_validation', False):
            for rec in self:
                if not rec.company_id:
                    continue
                field = self.env['stock.location'].search(
                    [('valuation_in_account_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Account Account is assigned to Stock Location '
                          '(%s).' % field.name_get()[0][1]))
                field = self.env['stock.location'].search(
                    [('valuation_out_account_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Account Account is assigned to Stock Location '
                          '(%s).' % field.name_get()[0][1]))
