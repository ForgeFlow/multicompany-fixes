# Copyright 2018 Creu Blanca
# Copyright 2018 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo import models


class Pricelist(models.Model):
    _inherit = "product.pricelist"

    def _check_company_id_search(self):
        res = super()._check_company_id_search()
        res += [
            ('pos.config', [('pricelist_id', '=', self.id)]),
            ('pos.config', [('available_pricelist_ids', 'in', self.ids)]),
            ('pos.order', [('pricelist_id', '=', self.id)]),
        ]
        return res
