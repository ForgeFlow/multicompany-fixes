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
        if not self.env.context.get('bypass_company_validation', False):
            for rec in self:
                if not rec.company_id:
                    continue
                field = self.env['account.invoice'].search(
                    [('fiscal_position_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Account Fiscal Position is assigned to '
                          'Account Invoice (%s).' % field.name_get()[0][1]))
                field = self.env['account.invoice.report'].search(
                    [('fiscal_position_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Account Fiscal Position is assigned to '
                          'Account Invoice Report (%s)'
                          '.' % field.name_get()[0][1]))


class Partner(models.Model):
    _inherit = 'res.partner'

    @api.constrains('company_id')
    def _check_company_id_out_model(self):
        super(Partner, self)._check_company_id_out_model()
        if not self.env.context.get('bypass_company_validation', False):
            for rec in self:
                if not rec.company_id:
                    continue
                field = self.env['account.invoice'].search(
                    [('partner_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Res Partner is assigned to Account Invoice '
                          '(%s).' % field.name_get()[0][1]))
                field = self.env['account.invoice'].search(
                    [('commercial_partner_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Res Partner is assigned to Account Invoice '
                          '(%s).' % field.name_get()[0][1]))
                field = self.env['account.analytic.line'].search(
                    [('partner_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Res Partner is assigned to Account Analytic Line '
                          '(%s).' % field.name_get()[0][1]))
                field = self.env['account.invoice.line'].search(
                    [('partner_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Res Partner is assigned to Account Invoice Line '
                          '(%s).' % field.name_get()[0][1]))
                field = self.env['account.bank.statement.line'].search(
                    [('partner_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Res Partner is assigned to '
                          'Account Bank Statement Line (%s)'
                          '.' % field.name_get()[0][1]))
                field = self.env['account.move'].search(
                    [('partner_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Res Partner is assigned to Account Move '
                          '(%s).' % field.name_get()[0][1]))
                field = self.env['account.move.line'].search(
                    [('partner_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Res Partner is assigned to Account Move Line '
                          '(%s).' % field.name_get()[0][1]))
                field = self.env['account.payment'].search(
                    [('partner_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Res Partner is assigned to Account Payment '
                          '(%s).' % field.name_get()[0][1]))
                field = self.env['account.invoice.report'].search(
                    [('partner_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Res Partner is assigned to Account Invoice Report '
                          '(%s).' % field.name_get()[0][1]))
                field = self.env['account.invoice.report'].search(
                    [('commercial_partner_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Res Partner is assigned to Account Invoice Report '
                          '(%s).' % field.name_get()[0][1]))
