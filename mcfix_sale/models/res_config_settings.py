from odoo import api, models, _
from odoo.exceptions import ValidationError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    @api.onchange('company_id')
    def _onchange_company_id(self):
        super(ResConfigSettings, self)._onchange_company_id()
        if self.company_id and self.default_deposit_product_id.company_id and \
                self.default_deposit_product_id.company_id != self.company_id:
            self.default_deposit_product_id = False

    @api.multi
    @api.constrains('company_id', 'default_deposit_product_id')
    def _check_company_id_default_deposit_product_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.default_deposit_product_id.company_id \
                    and rec.company_id != rec.default_deposit_product_id.\
                    company_id:
                raise ValidationError(
                    _('The Company in the Res Config Settings and in '
                      'Product Product must be the same.'))
