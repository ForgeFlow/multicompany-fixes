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
        if self.company_id and self.account_id.company_id and \
                self.account_id.company_id != self.company_id:
            self.account_id = False
        if self.company_id and self.refund_account_id.company_id and \
                self.refund_account_id.company_id != self.company_id:
            self.refund_account_id = False
        if self.company_id and self.cash_basis_account.company_id and \
                self.cash_basis_account.company_id != self.company_id:
            self.cash_basis_account = False

    @api.multi
    @api.constrains('company_id', 'cash_basis_account')
    def _check_company_id_cash_basis_account(self):
        for rec in self.sudo():
            if rec.company_id and rec.cash_basis_account.company_id and\
                    rec.company_id != rec.cash_basis_account.company_id:
                raise ValidationError(
                    _('The Company in the Account Tax and in '
                      'Account Account must be the same.'))

    @api.multi
    @api.constrains('company_id', 'refund_account_id')
    def _check_company_id_refund_account_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.refund_account_id.company_id and\
                    rec.company_id != rec.refund_account_id.company_id:
                raise ValidationError(
                    _('The Company in the Account Tax and in '
                      'Account Account must be the same.'))

    @api.multi
    @api.constrains('company_id', 'children_tax_ids')
    def _check_company_id_children_tax_ids(self):
        for rec in self.sudo():
            for line in rec.children_tax_ids:
                if rec.company_id and line.company_id and\
                        rec.company_id != line.company_id:
                    raise ValidationError(
                        _('The Company in the Account Tax and in '
                          'Account Tax (%s) must be the same'
                          '.') % line.name_get()[0][1])

    @api.multi
    @api.constrains('company_id', 'account_id')
    def _check_company_id_account_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.account_id.company_id and\
                    rec.company_id != rec.account_id.company_id:
                raise ValidationError(
                    _('The Company in the Account Tax and in '
                      'Account Account must be the same.'))

    @api.constrains('company_id')
    def _check_company_id_out_model(self):
        if not self.env.context.get('bypass_company_validation', False):
            for rec in self:
                if not rec.company_id:
                    continue
                field = self.env['account.invoice.line'].search(
                    [('invoice_line_tax_ids', 'in', [rec.id]),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Account Tax is assigned to Account Invoice Line '
                          '(%s).' % field.name_get()[0][1]))
                field = self.env['product.template'].search(
                    [('taxes_id', 'in', [rec.id]),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Account Tax is assigned to Product Template '
                          '(%s).' % field.name_get()[0][1]))
                field = self.env['product.template'].search(
                    [('supplier_taxes_id', 'in', [rec.id]),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Account Tax is assigned to Product Template '
                          '(%s).' % field.name_get()[0][1]))
                field = self.env['account.account'].search(
                    [('tax_ids', 'in', [rec.id]),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Account Tax is assigned to Account Account '
                          '(%s).' % field.name_get()[0][1]))
                field = self.env['account.invoice.tax'].search(
                    [('tax_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Account Tax is assigned to Account Invoice Tax '
                          '(%s).' % field.name_get()[0][1]))
                field = self.env['account.reconcile.model'].search(
                    [('tax_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Account Tax is assigned to Account Reconcile Model '
                          '(%s).' % field.name_get()[0][1]))
                field = self.env['account.reconcile.model'].search(
                    [('second_tax_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Account Tax is assigned to Account Reconcile Model '
                          '(%s).' % field.name_get()[0][1]))
                field = self.env['account.move.line'].search(
                    [('tax_line_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Account Tax is assigned to Account Move Line '
                          '(%s).' % field.name_get()[0][1]))
                field = self.env['account.move.line'].search(
                    [('tax_ids', 'in', [rec.id]),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Account Tax is assigned to Account Move Line '
                          '(%s).' % field.name_get()[0][1]))
                field = self.search(
                    [('children_tax_ids', 'in', [rec.id]),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Account Tax is assigned to Account Tax '
                          '(%s).' % field.name_get()[0][1]))
