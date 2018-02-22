from odoo import api, models, _
from odoo.exceptions import ValidationError


class AccountFiscalPosition(models.Model):
    _inherit = 'account.fiscal.position'

    @api.constrains('company_id')
    def _check_company_id_out_model(self):
        super(AccountFiscalPosition, self)._check_company_id_out_model()
        if not self.env.context.get('bypass_company_validation', False):
            for rec in self:
                if not rec.company_id:
                    continue
                field = self.env['purchase.order'].search(
                    [('fiscal_position_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Account Fiscal Position is assigned to '
                          'Purchase Order (%s).' % field.name_get()[0][1]))


class Partner(models.Model):
    _inherit = 'res.partner'

    @api.constrains('company_id')
    def _check_company_id_out_model(self):
        super(Partner, self)._check_company_id_out_model()
        if not self.env.context.get('bypass_company_validation', False):
            for rec in self:
                if not rec.company_id:
                    continue
                field = self.env['purchase.order.line'].sudo().search(
                    [('partner_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Res Partner is assigned to Purchase Order Line '
                          '(%s).' % field.name_get()[0][1]))
                field = self.env['purchase.order'].sudo().search(
                    [('partner_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Res Partner is assigned to Purchase Order '
                          '(%s).' % field.name_get()[0][1]))
                field = self.env['purchase.order'].sudo().search(
                    [('dest_address_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Res Partner is assigned to Purchase Order '
                          '(%s).' % field.name_get()[0][1]))
