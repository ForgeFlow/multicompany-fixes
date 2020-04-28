# Copyright 2018 Creu Blanca
# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo import api, models


class ReportSaleDetails(models.AbstractModel):
    _inherit = 'report.point_of_sale.report_saledetails'

    @api.multi
    def _get_report_values(self, docids, data=None):
        res = super(ReportSaleDetails, self)._get_report_values(
            docids=docids, data=data)
        res['company_id'] = self.env['res.company'].browse(data['company_id'])
        return res
