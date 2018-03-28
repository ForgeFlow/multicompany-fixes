from odoo import api, models, _
from odoo.exceptions import ValidationError


class AccountTax(models.Model):
    _inherit = 'account.tax'

    @api.multi
    def _get_family(self):
        taxes = self
        for tax in self:
            children = tax.children_tax_ids
            context = self._context.get('search_tax_parents')
            if context:
                children = children.filtered(lambda c: c.id not in context)
            if children:
                taxes |= children.\
                    with_context(search_tax_children=tax.ids).\
                    _get_family()
            parents = self.search(
                [('children_tax_ids', 'in', [tax.id])])
            context = self._context.get('search_tax_children')
            if context:
                parents = parents.filtered(lambda p: p.id not in context)
            if parents:
                taxes |= parents.\
                    with_context(search_tax_parents=tax.ids).\
                    _get_family()
        return taxes

    @api.multi
    def write(self, vals):
        company = False
        if vals.get('company_id') and \
                not self._context.get('stop_recursion_company'):
            company = vals['company_id']
            del vals['company_id']
        result = super(AccountTax, self).write(vals)
        if company and not self._context.get('stop_recursion_company'):
            taxes = self._get_family()
            taxes = taxes.filtered(lambda t: t.company_id)
            taxes |= self
            result = result and taxes.with_context(
                stop_recursion_company=True).write(
                {'company_id': company})
        return result

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if not self.account_id.check_company(self.company_id):
            self.account_id = False
        if not self.refund_account_id.check_company(self.company_id):
            self.refund_account_id = False
        if not self.cash_basis_account.check_company(self.company_id):
            self.cash_basis_account = False

    @api.multi
    @api.constrains('company_id', 'cash_basis_account')
    def _check_company_id_cash_basis_account(self):
        for rec in self.sudo():
            if not rec.cash_basis_account.company_id.check_company(
                    rec.company_id):
                raise ValidationError(
                    _('The Company in the Account Tax and in '
                      'Account Account must be the same.'))

    @api.multi
    @api.constrains('company_id', 'refund_account_id')
    def _check_company_id_refund_account_id(self):
        for rec in self.sudo():
            if not rec.refund_account_id.company_id.check_company(
                    rec.company_id):
                raise ValidationError(
                    _('The Company in the Account Tax and in '
                      'Account Account must be the same.'))

    @api.multi
    @api.constrains('company_id', 'children_tax_ids')
    def _check_company_id_children_tax_ids(self):
        for rec in self.sudo():
            for line in rec.children_tax_ids:
                if not line.check_company(rec.company_id):
                    raise ValidationError(
                        _('The Company in the Account Tax and in '
                          'Account Tax (%s) must be the same'
                          '.') % line.name_get()[0][1])

    @api.multi
    @api.constrains('company_id', 'account_id')
    def _check_company_id_account_id(self):
        for rec in self.sudo():
            if not rec.account_id.company_id.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Account Tax and in '
                      'Account Account must be the same.'))

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
            ('account.invoice.line',
             [('invoice_line_tax_ids', 'in', self.ids)]),
            ('account.invoice.tax', [('tax_id', '=', self.id)]),
            ('account.move.line', [('tax_ids', 'in', self.ids)]),
            ('account.move.line', [('tax_line_id', '=', self.id)]),
            ('account.reconcile.model', [('second_tax_id', '=', self.id)]),
            ('account.reconcile.model', [('tax_id', '=', self.id)]),
            ('account.tax', [('children_tax_ids', 'in', self.ids)]),
            ('product.template', [('taxes_id', 'in', self.ids)]),
            ('product.template', [('supplier_taxes_id', 'in', self.ids)]),
        ]
        return res
