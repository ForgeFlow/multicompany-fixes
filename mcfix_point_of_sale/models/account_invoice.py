# Copyright 2018 Creu Blanca
# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo import models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def _check_company_id_search(self):
        res = super()._check_company_id_search()
        res += [
            ('pos.order', [('invoice_id', '=', self.id)]),
        ]
        return res
