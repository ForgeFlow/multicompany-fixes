# Copyright 2018 Creu Blanca
# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo import models


class AccountFiscalPosition(models.Model):
    _inherit = 'account.fiscal.position'

    def _check_company_id_search(self):
        res = super()._check_company_id_search()
        res += [
            ('pos.config', [('default_fiscal_position_id', '=', self.id)]),
            ('pos.config', [('fiscal_position_ids', 'in', self.ids)]),
            ('pos.order', [('fiscal_position_id', '=', self.id)]),
        ]
        return res
