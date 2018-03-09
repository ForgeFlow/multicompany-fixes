from odoo import api, models


class ReportSaleDetails(models.AbstractModel):
    _inherit = 'report.point_of_sale.report_saledetails'

    @api.multi
    def get_report_values(self, docids, data=None):
        res = super(ReportSaleDetails, self).get_report_values(
            docids=docids, data=data)
        res['company_id'] = self.env['res.company'].browse(data['company_id'])
        return res
