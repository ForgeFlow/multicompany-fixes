from odoo import api, models, _
from odoo.exceptions import ValidationError


class StockLocation(models.Model):
    _inherit = "stock.location"

    @api.onchange('company_id')
    def _onchange_company_id(self):
        super(StockLocation, self)._onchange_company_id()
        if not self.valuation_in_account_id.check_company(self.company_id):
            self.valuation_in_account_id = self.location_id.\
                valuation_in_account_id
        if not self.valuation_out_account_id.check_company(self.company_id):
            self.valuation_out_account_id = self.location_id.\
                valuation_out_account_id

    @api.multi
    @api.constrains('company_id', 'valuation_in_account_id')
    def _check_company_id_valuation_in_account_id(self):
        for rec in self.sudo():
            if not rec.valuation_in_account_id.check_company(
                rec.company_id
            ):
                raise ValidationError(
                    _('The Company in the Stock Location and in '
                      'Account Account must be the same.'))

    @api.multi
    @api.constrains('company_id', 'valuation_out_account_id')
    def _check_company_id_valuation_out_account_id(self):
        for rec in self.sudo():
            if not rec.valuation_out_account_id.check_company(
                rec.company_id
            ):
                raise ValidationError(
                    _('The Company in the Stock Location and in '
                      'Account Account must be the same.'))
