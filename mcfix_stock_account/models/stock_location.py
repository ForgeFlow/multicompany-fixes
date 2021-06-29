from odoo import api, fields, models


class StockLocation(models.Model):
    _inherit = "stock.location"

    valuation_in_account_id = fields.Many2one(check_company=True)
    valuation_out_account_id = fields.Many2one(check_company=True)

    @api.onchange("company_id")
    def _onchange_company_id(self):
        super(StockLocation, self)._onchange_company_id()
        if not self.valuation_in_account_id.check_company(self.company_id):
            self.valuation_in_account_id = self.location_id.valuation_in_account_id
        if not self.valuation_out_account_id.check_company(self.company_id):
            self.valuation_out_account_id = self.location_id.valuation_out_account_id
