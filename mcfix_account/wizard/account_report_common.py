from odoo import api, fields, models


class AccountCommonReport(models.TransientModel):
    _inherit = "account.common.report"

    company_id = fields.Many2one(readonly=False, required=True)
    journal_ids = fields.Many2many(default=lambda self: self.env[
        'account.journal'].search([('company_id', '=', self.company_id.id)]))

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if self.company_id:
            self.journal_ids = self.env['account.journal'].search(
                [('company_id', '=', self.company_id.id)])
        else:
            self.journal_ids = self.env['account.journal'].search([])

    def _build_contexts(self, data):
        data['form'].update(self.read(['company_id'])[0])
        result = super(AccountCommonReport, self)._build_contexts(data=data)
        result['company_id'] = data['form']['company_id'][0] or False
        return result
