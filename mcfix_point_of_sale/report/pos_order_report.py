# -*- coding: utf-8 -*-
from odoo import models, api, _
from odoo.exceptions import ValidationError


class ReportPosOrder(models.Model):
    _inherit = 'report.pos.order'

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        res = []
        names = super(ReportPosOrder, self).name_get()
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
        self.order_id = False
        self.product_tmpl_id = False
        self.location_id = False
        self.journal_id = False
        self.config_id = False
        self.stock_location_id = False
        self.pricelist_id = False

    @api.multi
    @api.constrains('order_id', 'company_id')
    def _check_company_order_id(self):
        for pos_order in self.sudo():
            if pos_order.company_id and pos_order.order_id.company_id and \
                    pos_order.company_id != pos_order.order_id.company_id:
                raise ValidationError(
                    _('The Company in the Report Pos Order and in '
                      'Pos Order must be the same.'))
        return True

    @api.multi
    @api.constrains('product_tmpl_id', 'company_id')
    def _check_company_product_tmpl_id(self):
        for pos_order in self.sudo():
            if pos_order.company_id and pos_order.product_tmpl_id.company_id \
                    and pos_order.company_id != pos_order.product_tmpl_id.\
                    company_id:
                raise ValidationError(
                    _('The Company in the Report Pos Order and in '
                      'Product Template must be the same.'))
        return True

    @api.multi
    @api.constrains('location_id', 'company_id')
    def _check_company_location_id(self):
        for pos_order in self.sudo():
            if pos_order.company_id and pos_order.location_id.company_id and \
                    pos_order.company_id != pos_order.location_id.company_id:
                raise ValidationError(
                    _('The Company in the Report Pos Order and in '
                      'Location must be the same.'))
        return True

    @api.multi
    @api.constrains('journal_id', 'company_id')
    def _check_company_journal_id(self):
        for pos_order in self.sudo():
            if pos_order.company_id and pos_order.journal_id.company_id and \
                    pos_order.company_id != pos_order.journal_id.company_id:
                raise ValidationError(
                    _('The Company in the Report Pos Order and in '
                      'Journal must be the same.'))
        return True

    @api.multi
    @api.constrains('config_id', 'company_id')
    def _check_company_config_id(self):
        for pos_order in self.sudo():
            if pos_order.company_id and pos_order.config_id.company_id and \
                    pos_order.company_id != pos_order.config_id.company_id:
                raise ValidationError(
                    _('The Company in the Report Pos Order and in '
                      'Pos Config must be the same.'))
        return True

    @api.multi
    @api.constrains('stock_location_id', 'company_id')
    def _check_company_stock_location_id(self):
        for pos_order in self.sudo():
            if pos_order.company_id and pos_order.stock_location_id.company_id\
                    and pos_order.company_id != pos_order.stock_location_id.\
                    company_id:
                raise ValidationError(
                    _('The Company in the Report Pos Order and in '
                      'Warehouse must be the same.'))
        return True

    @api.multi
    @api.constrains('pricelist_id', 'company_id')
    def _check_company_pricelist_id(self):
        for pos_order in self.sudo():
            if pos_order.company_id and pos_order.pricelist_id.company_id and \
                    pos_order.company_id != pos_order.pricelist_id.company_id:
                raise ValidationError(
                    _('The Company in the Report Pos Order and in '
                      'Pricelist must be the same.'))
        return True
