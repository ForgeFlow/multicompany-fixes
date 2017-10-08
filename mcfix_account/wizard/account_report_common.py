# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import ValidationError


class AccountCommonReport(models.TransientModel):
    _inherit = 'account.common.report'

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        res = []
        names = super(AccountCommonReport, self).name_get()
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

    @api.multi
    @api.constrains('journal_ids', 'company_id')
    def _check_company_journal_ids(self):
        for common_report in self.sudo():
            for account_journal in common_report.journal_ids:
                if common_report.company_id and \
                        common_report.company_id != account_journal.company_id:
                    raise ValidationError(
                        _('The Company in the Report and in '
                          'Journal must be the same.'))
        return True
