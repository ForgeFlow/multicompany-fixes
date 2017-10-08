# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import ValidationError


class SaleReport(models.Model):
    _inherit = 'sale.report'

    @api.onchange('company_id')
    def onchange_company_id(self):
        super(SaleReport, self).onchange_company_id()
        self.warehouse_id = False

    @api.multi
    @api.constrains('warehouse_id', 'company_id')
    def _check_company_warehouse_id(self):
        for report in self.sudo():
            if report.company_id and report.warehouse_id.company_id and \
                    report.company_id != report.warehouse_id.company_id:
                raise ValidationError(
                    _('The Company in the Report and in '
                      'Warehouse must be the same.'))
        return True
