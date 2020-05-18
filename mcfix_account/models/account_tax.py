from odoo import api, fields, models


class AccountTax(models.Model):
    _inherit = 'account.tax'
    _check_company_auto = True

    children_tax_ids = fields.Many2many(check_company=True)
    cash_basis_transition_account_id = fields.Many2one(
        check_company=True,
        domain="[('deprecated', '=', False), ('company_id', '=', company_id)]")
    cash_basis_base_account_id = fields.Many2one(
        check_company=True,
        domain="[('deprecated', '=', False), ('company_id', '=', company_id)]")

    # def _get_family(self):
    #     taxes = self
    #     for tax in self:
    #         children = tax.children_tax_ids
    #         context = self._context.get('search_tax_parents')
    #         if context:
    #             children = children.filtered(lambda c: c.id not in context)
    #         if children:
    #             taxes |= children.\
    #                 with_context(search_tax_children=tax.ids).\
    #                 _get_family()
    #         parents = self.search(
    #             [('children_tax_ids', 'in', [tax.id])])
    #         context = self._context.get('search_tax_children')
    #         if context:
    #             parents = parents.filtered(lambda p: p.id not in context)
    #         if parents:
    #             taxes |= parents.\
    #                 with_context(search_tax_parents=tax.ids).\
    #                 _get_family()
    #     return taxes
    #
    # def write(self, vals):
    #     company = False
    #     if vals.get('company_id') and \
    #             not self._context.get('stop_recursion_company'):
    #         company = vals['company_id']
    #         del vals['company_id']
    #     result = super(AccountTax, self).write(vals)
    #     if company and not self._context.get('stop_recursion_company'):
    #         taxes = self._get_family()
    #         taxes = taxes.filtered(lambda t: t.company_id)
    #         taxes |= self
    #         result = result and taxes.with_context(
    #             stop_recursion_company=True).write(
    #             {'company_id': company})
    #     return result

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if not self.cash_basis_base_account_id.check_company(self.company_id):
            self.cash_basis_base_account_id = False

    @api.constrains('company_id')
    def _check_company_id_out_model(self):
        self._check_company_id_base_model()

    def _check_company_id_fields(self):
        res = super()._check_company_id_fields()
        res += [self.children_tax_ids, ]
        return res

    def _check_company_id_search(self):
        res = super()._check_company_id_search()
        res += [
            ('account.account', [('tax_ids', 'in', self.ids)]),
            ('account.move.line', [('tax_ids', 'in', self.ids)]),
            ('account.reconcile.model', [('second_tax_ids', 'in', self.ids)]),
            ('account.reconcile.model', [('tax_ids', 'in', self.ids)]),
            ('account.tax', [('children_tax_ids', 'in', self.ids)]),
            ('product.template', [('taxes_id', 'in', self.ids)]),
            ('product.template', [('supplier_taxes_id', 'in', self.ids)]),
        ]
        return res


class AccountTaxRepartitionLine(models.Model):
    _inherit = "account.tax.repartition.line"
    _check_company_auto = True

    account_id = fields.Many2one(
        domain="[('deprecated', '=', False), ('company_id', '=', company_id),"
               " ('internal_type', 'not in', ('receivable', 'payable'))]",
        check_company=True)
    invoice_tax_id = fields.Many2one(check_company=True)
    refund_tax_id = fields.Many2one(check_company=True)
    company_id = fields.Many2one(
        required=False, compute="_compute_company", store=True)

    @api.depends('invoice_tax_id.company_id', 'refund_tax_id.company_id')
    def _compute_company(self):
        for record in self:
            record.company_id = \
                record.invoice_tax_id and \
                record.invoice_tax_id.company_id.id or \
                record.refund_tax_id.company_id.id

    @api.constrains('company_id')
    def _check_company_id_out_model(self):
        self._check_company_id_base_model()

    def _check_company_id_search(self):
        res = super()._check_company_id_search()
        res += [
            ('account.move.line', [('tax_repartition_line_id', '=', self.id)]),
        ]
        return res
