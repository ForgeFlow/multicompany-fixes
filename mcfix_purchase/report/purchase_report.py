# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import ValidationError


class PurchaseReport(models.Model):
    _inherit = 'purchase.report'

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        res = []
        names = super(PurchaseReport, self).name_get()
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
        self.picking_type_id = False
        self.product_tmpl_id = False
        self.fiscal_position_id = False
        self.account_analytic_id = False

    @api.multi
    @api.constrains('picking_type_id', 'company_id')
    def _check_company_picking_type_id(self):
        for report in self.sudo():
            if report.company_id and report.picking_type_id.company_id and \
                    report.company_id != report.picking_type_id.company_id:
                raise ValidationError(
                    _('The Company in the Report and in '
                      'Picking Type must be the same.'))
        return True

    @api.multi
    @api.constrains('product_tmpl_id', 'company_id')
    def _check_company_product_tmpl_id(self):
        for report in self.sudo():
            if report.company_id and report.product_tmpl_id.company_id and \
                    report.company_id != report.product_tmpl_id.company_id:
                raise ValidationError(
                    _('The Company in the Report and in '
                      'Product Template must be the same.'))
        return True

    @api.multi
    @api.constrains('fiscal_position_id', 'company_id')
    def _check_company_fiscal_position_id(self):
        for report in self.sudo():
            if report.company_id and report.fiscal_position_id.company_id and \
                    report.company_id != report.fiscal_position_id.company_id:
                raise ValidationError(
                    _('The Company in the Report and in '
                      'Fiscal Position must be the same.'))
        return True

    @api.multi
    @api.constrains('account_analytic_id', 'company_id')
    def _check_company_account_analytic_id(self):
        for report in self.sudo():
            if report.company_id and report.account_analytic_id.company_id and\
                    report.company_id != report.account_analytic_id.company_id:
                raise ValidationError(
                    _('The Company in the Report and in '
                      'Account Analytic must be the same.'))
        return True
