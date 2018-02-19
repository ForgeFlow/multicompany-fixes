from odoo import api, models


class ReportJournal(models.AbstractModel):
    _inherit = 'report.account.report_journal'

    @api.model
    def get_report_values(self, docids, data=None):
        res = super(ReportJournal, self).\
            get_report_values(docids=docids, data=data)
        res['company_id'] = self.env['res.company'].browse(
            data['form']['company_id'][0])
        return res


class ReportGeneralLedger(models.AbstractModel):
    _inherit = 'report.account.report_generalledger'

    @api.model
    def get_report_values(self, docids, data=None):
        res = super(ReportGeneralLedger, self).\
            get_report_values(docids=docids, data=data)
        res['company_id'] = self.env['res.company'].browse(
            data['form']['company_id'][0])
        return res


class ReportPartnerLedger(models.AbstractModel):
    _inherit = 'report.account.report_partnerledger'

    @api.model
    def get_report_values(self, docids, data=None):
        res = super(ReportPartnerLedger, self).\
            get_report_values(docids=docids, data=data)
        res['company_id'] = self.env['res.company'].browse(
            data['form']['company_id'][0])
        return res


class ReportTrialBalance(models.AbstractModel):
    _inherit = 'report.account.report_trialbalance'

    @api.model
    def get_report_values(self, docids, data=None):
        res = super(ReportTrialBalance, self).\
            get_report_values(docids=docids, data=data)
        res['company_id'] = self.env['res.company'].browse(
            data['form']['company_id'][0])
        return res


class ReportOverdue(models.AbstractModel):
    _inherit = 'report.account.report_overdue'

    @api.model
    def get_report_values(self, docids, data=None):
        res = super(ReportOverdue, self).\
            get_report_values(docids=docids, data=data)
        res['company_id'] = self.env['res.company'].browse(
            [self.env.user.company_id.id]),
        return res


class ReportAgedPartnerBalance(models.AbstractModel):
    _inherit = 'report.account.report_agedpartnerbalance'

    @api.model
    def get_report_values(self, docids, data=None):
        res = super(ReportAgedPartnerBalance, self).\
            get_report_values(docids=docids, data=data)
        res['company_id'] = self.env['res.company'].browse(
            data['form']['company_id'][0])
        return res


class ReportFinancial(models.AbstractModel):
    _inherit = 'report.account.report_financial'

    @api.model
    def get_report_values(self, docids, data=None):
        res = super(ReportFinancial, self).\
            get_report_values(docids=docids, data=data)
        res['company_id'] = self.env['res.company'].browse(
            data['form']['company_id'][0])
        return res


class ReportTax(models.AbstractModel):
    _inherit = 'report.account.report_tax'

    @api.model
    def get_report_values(self, docids, data=None):
        res = super(ReportTax, self).\
            get_report_values(docids=docids, data=data)
        res['company_id'] = self.env['res.company'].browse(
            data['form']['company_id'][0])
        return res
