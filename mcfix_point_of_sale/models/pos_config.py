# -*- coding: utf-8 -*-
from odoo import models, api, _
from odoo.exceptions import ValidationError


class PosConfig(models.Model):
    _inherit = 'pos.config'

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        res = []
        names = super(PosConfig, self).name_get()
        multicompany_group = self.env.ref('base.group_multi_company')
        if multicompany_group not in self.env.user.groups_id:
            return names
        for name in names:
            rec = self.browse(name[0])
            name = '%s [%s]' % (name[1], rec.company_id.name) if \
                rec.company_id else name[1]
            res += [(rec.id, name)]
        return res

    @api.onchange('company_id')
    def onchange_company_id(self):
        self.journal_ids = False
        self.journal_id = self.env['account.journal'].search(
            [('type', '=', 'sale'), ('company_id', '=', self.company_id.id)],
            limit=1
        )
        self.invoice_journal_id = self.env['account.journal'].search(
            [('type', '=', 'sale'), ('company_id', '=', self.company_id.id)],
            limit=1
        )
        self.stock_location_id = self.env['stock.warehouse'].search(
            [('company_id', '=', self.company_id.id)], limit=1
        ).lot_stock_id
        self.pricelist_id = False
        self.fiscal_position_ids = False
        self.default_fiscal_position_id = False

    @api.multi
    @api.constrains('journal_ids', 'company_id')
    def _check_company_journal_ids(self):
        for config in self.sudo():
            for account_journal in config.journal_ids:
                if config.company_id and \
                        config.company_id != account_journal.company_id:
                    raise ValidationError(
                        _('The Company in the Pos Config and in '
                          'Available Payment Methods must be the same.'))
        return True

    @api.multi
    @api.constrains('stock_location_id', 'company_id')
    def _check_company_stock_location_id(self):
        for config in self.sudo():
            if config.company_id and config.stock_location_id.company_id and \
                    config.company_id != config.stock_location_id.company_id:
                raise ValidationError(
                    _('The Company in the Pos Config and in '
                      'Stock Location must be the same.'))
        return True

    @api.multi
    @api.constrains('journal_id', 'company_id')
    def _check_company_journal_id(self):
        for config in self.sudo():
            if config.company_id and config.journal_id.company_id and \
                    config.company_id != config.journal_id.company_id:
                raise ValidationError(
                    _('The Company in the Pos Config and in '
                      'Sale Journal must be the same.'))
        return True

    @api.multi
    @api.constrains('invoice_journal_id', 'company_id')
    def _check_company_invoice_journal_id(self):
        for config in self.sudo():
            if config.company_id and config.invoice_journal_id.company_id and \
                    config.company_id != config.invoice_journal_id.company_id:
                raise ValidationError(
                    _('The Company in the Pos Config and in '
                      'Invoice Journal must be the same.'))
        return True

    @api.multi
    @api.constrains('pricelist_id', 'company_id')
    def _check_company_pricelist_id(self):
        for config in self.sudo():
            if config.company_id and config.pricelist_id.company_id and \
                    config.company_id != config.pricelist_id.company_id:
                raise ValidationError(
                    _('The Company in the Pos Config and in '
                      'Pricelist must be the same.'))
        return True

    @api.multi
    @api.constrains('fiscal_position_ids', 'company_id')
    def _check_company_fiscal_position_ids(self):
        for config in self.sudo():
            for account_fiscal_position in config.fiscal_position_ids:
                if config.company_id and account_fiscal_position.company_id \
                        and config.company_id != account_fiscal_position.\
                        company_id:
                    raise ValidationError(
                        _('The Company in the Pos Config and in '
                          'Fiscal Position must be the same.'))
        return True

    @api.multi
    @api.constrains('default_fiscal_position_id', 'company_id')
    def _check_company_default_fiscal_position_id(self):
        for config in self.sudo():
            if config.company_id and config.default_fiscal_position_id.\
                    company_id and config.company_id != config.\
                    default_fiscal_position_id.company_id:
                raise ValidationError(
                    _('The Company in the Pos Config and in '
                      'Default Fiscal Position must be the same.'))
        return True

    @api.constrains('company_id')
    def _check_company_id(self):
        for rec in self:
            pos_order = self.env['report.pos.order'].search(
                [('config_id', '=', rec.id),
                 ('company_id', '!=', False),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if pos_order:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Point of Sale is assigned to Pos Order '
                      '%s.' % pos_order.name))
