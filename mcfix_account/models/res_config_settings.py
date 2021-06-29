from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    chart_template_id = fields.Many2one(check_company=True)

    @api.onchange("company_id")
    def _onchange_company_id(self):
        super(ResConfigSettings, self)._onchange_company_id()
        if not self.chart_template_id.check_company(self.company_id):
            self.chart_template_id = self.company_id.chart_template_id
        if not self.sale_tax_id.check_company(self.company_id):
            self.sale_tax_id = False
        if not self.purchase_tax_id.check_company(self.company_id):
            self.purchase_tax_id = False
