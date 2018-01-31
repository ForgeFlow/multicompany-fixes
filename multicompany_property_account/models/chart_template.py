# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class WizardMultiChartsAccounts(models.TransientModel):
    _inherit = 'wizard.multi.charts.accounts'

    @api.model
    def default_get(self, fields):
        res = super(WizardMultiChartsAccounts, self).default_get(fields)
        if self._context.get('company_id', False):
            res.update({
                'company_id': self._context.get('company_id')
            })
        return res
