# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import ValidationError


class SaleReport(models.Model):
    _inherit = 'sale.report'

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        res = []
        names = super(SaleReport, self).name_get()
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
        self.product_tmpl_id = False
        self.pricelist_id = False
        self.analytic_account_id = False
        self.team_id = False

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
    @api.constrains('pricelist_id', 'company_id')
    def _check_company_pricelist_id(self):
        for report in self.sudo():
            if report.company_id and report.pricelist_id.company_id and \
                    report.company_id != report.pricelist_id.company_id:
                raise ValidationError(
                    _('The Company in the Report and in '
                      'Pricelist must be the same.'))
        return True

    @api.multi
    @api.constrains('analytic_account_id', 'company_id')
    def _check_company_analytic_account_id(self):
        for report in self.sudo():
            if report.company_id and report.analytic_account_id.company_id and\
                    report.company_id != report.analytic_account_id.company_id:
                raise ValidationError(
                    _('The Company in the Report and in '
                      'Analytic Account must be the same.'))
        return True

    @api.multi
    @api.constrains('team_id', 'company_id')
    def _check_company_team_id(self):
        for report in self.sudo():
            if report.company_id and report.team_id.company_id and \
                    report.company_id != report.team_id.company_id:
                raise ValidationError(
                    _('The Company in the Report and in '
                      'Sales Team must be the same.'))
        return True
