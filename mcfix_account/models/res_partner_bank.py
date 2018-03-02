from odoo import api, models, _
from odoo.exceptions import ValidationError


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    @api.constrains('company_id')
    def _check_company_id_out_model(self):
        super(ResPartnerBank, self)._check_company_id_out_model()
        if not self.env.context.get('bypass_company_validation', False):
            for rec in self:
                if not rec.company_id:
                    continue
                field = self.env['account.invoice'].search(
                    [('partner_bank_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Res Partner Bank is assigned to Account Invoice '
                          '(%s).' % field.name_get()[0][1]))
                field = self.env['account.bank.statement.line'].search(
                    [('bank_account_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Res Partner Bank is assigned to '
                          'Account Bank Statement Line (%s)'
                          '.' % field.name_get()[0][1]))
                # Waiting merge of https://github.com/odoo/odoo/pull/23480
                # field = self.env['account.journal'].search(
                #     [('bank_account_id', '=', rec.id),
                #      ('company_id', '!=', False),
                #      ('company_id', '!=', rec.company_id.id)], limit=1)
                # if field:
                #     raise ValidationError(
                #         _('You cannot change the company, as this '
                #           'Res Partner Bank is assigned to Account Journal '
                #           '(%s).' % field.name_get()[0][1]))
