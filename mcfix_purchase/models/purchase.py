from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"
    _check_company_auto = True

    partner_id = fields.Many2one(check_company=True)
    dest_address_id = fields.Many2one(check_company=True)
    invoice_ids = fields.Many2many(check_company=True)
    fiscal_position_id = fields.Many2one(check_company=True)
    payment_term_id = fields.Many2one(check_company=True)

    @api.depends('company_id')
    def name_get(self):
        names = super(PurchaseOrder, self).name_get()
        res = self.add_company_suffix(names)
        return res

    @api.onchange('partner_id', 'company_id')
    def onchange_partner_id(self):
        res = super(PurchaseOrder, self).onchange_partner_id()
        if self.partner_id:
            self.currency_id = self.with_context(
                force_company=self.company_id.id
            ).partner_id.property_purchase_currency_id.id or \
                self.company_id.currency_id.id
        return res

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if not self.partner_id.check_company(self.company_id):
            self.partner_id = False
        if not self.dest_address_id.check_company(self.company_id):
            self.dest_address_id = False

    def _check_company_id_fields(self):
        res = super()._check_company_id_fields()
        res += [self.invoice_ids, self.order_line, ]
        return res

    def _check_company_id_search(self):
        res = super()._check_company_id_search()
        res += [
            ('account.move', [('purchase_id', '=', self.id)]),
        ]
        return res


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    _check_company_auto = True

    taxes_id = fields.Many2many(check_company=True)
    account_analytic_id = fields.Many2one(check_company=True)
    product_id = fields.Many2one(check_company=True)
    order_id = fields.Many2one(check_company=True)

    def _suggest_quantity(self):
        self.taxes_id = self.taxes_id.filtered(
            lambda r: r.company_id == self.order_id.company_id)
        if not self.account_analytic_id:
            self.account_analytic_id = self.default_account_analytic()
        return super()._suggest_quantity()

    @api.model
    def default_account_analytic(self):
        return False

    @api.constrains('company_id')
    def _check_company_id_out_model(self):
        self._check_company_id_base_model()

    def _check_company_id_fields(self):
        res = super()._check_company_id_fields()
        res += [self.invoice_lines, ]
        return res

    @api.onchange('product_id')
    def onchange_product_id(self):
        self.company_id = self.order_id.company_id
        result = super(PurchaseOrderLine, self.with_context(
            not_display_company=True)).onchange_product_id()
        return result
