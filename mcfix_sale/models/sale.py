from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    partner_id = fields.Many2one(check_company=True)
    partner_invoice_id = fields.Many2one(check_company=True)
    partner_shipping_id = fields.Many2one(check_company=True)
    invoice_ids = fields.Many2many(check_company=True)
    order_line = fields.One2many(check_company=True)

    def default_analytic_account(self):
        return False

    @api.onchange("company_id")
    def _onchange_company_id(self):
        if not self.analytic_account_id.check_company(self.company_id):
            self.analytic_account_id = self.default_analytic_account()
        if not self.partner_id.check_company(self.company_id):
            self.partner_id = False
        if not self.team_id.check_company(self.company_id):
            self.team_id = False
        if not self.partner_invoice_id.check_company(self.company_id):
            self.partner_invoice_id = False
        if not self.partner_shipping_id.check_company(self.company_id):
            self.partner_shipping_id = False
        if not self.fiscal_position_id.check_company(self.company_id):
            self.fiscal_position_id = False
        if not self.pricelist_id.check_company(self.company_id):
            self.pricelist_id = False
        if not self.payment_term_id.check_company(self.company_id):
            self.payment_term_id = False
        self.onchange_partner_shipping_id()
        self.order_line.change_company_id()

    @api.onchange("partner_id")
    def onchange_partner_id(self):
        company_id = self.company_id.id or self.env.user.company_id.id
        super(
            SaleOrder, self.with_context(force_company=company_id)
        ).onchange_partner_id()

    @api.constrains("company_id")
    def _check_company_id_out_model(self):
        self._check_company_id_base_model()


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    order_id = fields.Many2one(check_company=True)
    invoice_lines = fields.Many2many(check_company=True)
    tax_id = fields.Many2many(check_company=True)

    @api.depends("company_id")
    def name_get(self):
        names = super(SaleOrderLine, self).name_get()
        res = self.add_company_suffix(names)
        return res

    def change_company_id(self):
        for line in self:
            line._compute_tax_id()

    def _prepare_invoice_line(self):
        company_id = self.company_id.id or self.env.user.company_id.id
        return super(
            SaleOrderLine, self.with_context(force_company=company_id)
        )._prepare_invoice_line()

    @api.constrains("company_id")
    def _check_company_id_out_model(self):
        self._check_company_id_base_model()

    def _check_company_id_search(self):
        res = super()._check_company_id_search()
        res += [
            ("account.analytic.line", [("so_line", "=", self.id)]),
            ("account.move.line", [("sale_line_ids", "in", self.ids)]),
        ]
        return res
