from odoo import api, models


class ReportJournal(models.AbstractModel):
    _inherit = 'report.account.report_journal'

    @api.model
    def _get_report_values(self, docids, data=None):
        res = super(ReportJournal, self).\
            get_report_values(docids=docids, data=data)
        res['company_id'] = self.env['res.company'].browse(
            data['form']['company_id'][0])
        return res


class ReportAgedPartnerBalance(models.AbstractModel):
    _inherit = 'report.account.report_agedpartnerbalance'

    @api.model
    def _get_report_values(self, docids, data=None):
        res = super(ReportAgedPartnerBalance, self).\
            get_report_values(docids=docids, data=data)
        res['company_id'] = self.env['res.company'].browse(
            data['form']['company_id'][0])
        return res
