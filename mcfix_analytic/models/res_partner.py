from odoo import models


class Partner(models.Model):
    _inherit = 'res.partner'

    def _check_company_id_fields(self):
        res = super()._check_company_id_fields()
        res += [self.contract_ids, ]
        return res
