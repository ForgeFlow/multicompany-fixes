from odoo import api, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        names = super(ResConfigSettings, self).name_get()
        res = self.add_company_suffix(names)
        return res
