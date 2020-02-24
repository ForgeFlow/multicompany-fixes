from odoo import api, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    @api.onchange('company_id')
    def _onchange_company_id(self):
        super(ResConfigSettings, self)._onchange_company_id()
        if not self.deposit_default_product_id.check_company(self.company_id):
            self.deposit_default_product_id = False
