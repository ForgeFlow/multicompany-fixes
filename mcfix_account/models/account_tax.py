# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import ValidationError


class AccountTax(models.Model):
    _inherit = 'account.tax'

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        res = []
        names = super(AccountTax, self).name_get()
        multicompany_group = self.env.ref('base.group_multi_company')
        if multicompany_group not in self.env.user.groups_id:
            return names
        for name in names:
            rec = self.browse(name[0])
            name = "%s [%s]" % (name[1], name.company_id.name) if \
                name.company_id else name[1]
            res += [(rec.id, name)]
        return res

    @api.onchange('company_id')
    def onchange_company_id(self):
        self.account_id = False
        self.refund_account_id = False
        self.children_tax_ids = False

    def write(self, vals):
        if 'company_id' in vals:
            if not self.env.context.get('bypass_company_validation', False):
                for rec in self:

                    # Invoice
                    invoice = self.env['account.invoice'].search(
                        [('invoice_line_tax_ids', 'in', [rec.id]),
                         ('company_id', '!=', vals['company_id'])], limit=1)
                    if invoice:
                        raise ValidationError(
                            _('You cannot change the company, as this '
                              'tax is assigned to invoice %s.' %
                              invoice.name))
                    invoice_tax = self.env['account.invoice.tax'].search(
                        [('tax_id', '=', rec.id),
                         ('company_id', '!=', vals['company_id'])], limit=1)
                    if invoice_tax:
                        raise ValidationError(
                            _('You cannot change the company, as this '
                              'tax is assigned to invoice tax %s in invoice '
                              '%s.' % (invoice_tax.name,
                                       invoice_tax.invoice_id.name)))

                    # Account Tax
                    parent_tax = self.search(
                        [('children_tax_ids', 'in', [rec.id]),
                         ('company_id', '!=', vals['company_id'])], limit=1)
                    if parent_tax:
                        raise ValidationError(
                            _('You cannot change the company, as this '
                              'tax is child tax of Tax %s.' %
                              parent_tax.name))
                    second_tax = self.search(
                        [('second_tax_id', '=', [rec.id]),
                         ('company_id', '!=', vals['company_id'])], limit=1)
                    if second_tax:
                        raise ValidationError(
                            _('You cannot change the company, as this '
                              'tax is Second Tax of Tax %s.' %
                              parent_tax.name))

                    # Account Move Line
                    aml = self.env['account.move.line'].search(
                        [('tax_ids', 'in', [rec.id]),
                         ('company_id', '!=', vals['company_id'])], limit=1)
                    if aml:
                        raise ValidationError(
                            _('You cannot change the company, as this '
                              'tax is assigned to account move line %s of '
                              'move %s.' % (aml.name, aml.move_id.name)))
                    aml = self.env['account.move.line'].search(
                        [('tax_line_id', '=', [rec.id]),
                         ('company_id', '!=', vals['company_id'])], limit=1)
                    if aml:
                        raise ValidationError(
                            _('You cannot change the company, as this '
                              'tax is assigned to account move line %s of '
                              'move %s.' % (aml.name, aml.move_id.name)))

                    # Account Fiscal Position Tax
                    fp_tax = self.env['account.fiscal.position.tax'].search(
                        [('tax_src_id', '=', [rec.id]),
                         ('company_id', '!=', vals['company_id'])], limit=1)
                    if fp_tax:
                        raise ValidationError(
                            _('You cannot change the company, as this '
                              'tax is assigned as Tax on Product in Fiscal '
                              'Position Tax %s of Fiscal Position %s.' %
                              (fp_tax.name, fp_tax.position_id.name)))

                    fp_tax = self.env['account.fiscal.position.tax'].search(
                        [('tax_dest_id', '=', [rec.id]),
                         ('company_id', '!=', vals['company_id'])], limit=1)
                    if fp_tax:
                        raise ValidationError(
                            _('You cannot change the company, as this '
                              'tax is assigned as Tax to Apply in Fiscal '
                              'Position Tax %s of Fiscal Position %s.' %
                              (fp_tax.name, fp_tax.position_id.name)))

                    # Product Template
                    pt = self.env['product.template'].search(
                        [('taxes_id', 'in', [rec.id]),
                         ('company_id', '!=', vals['company_id'])], limit=1)
                    if pt:
                        raise ValidationError(
                            _('You cannot change the company, as this '
                              'tax is assigned as Customer Taxes of Product '
                              'Template %s.' % pt.name))
                    pt = self.env['product.template'].search(
                        [('supplier_taxes_id', 'in', [rec.id]),
                         ('company_id', '!=', vals['company_id'])], limit=1)
                    if pt:
                        raise ValidationError(
                            _('You cannot change the company, as this '
                              'tax is assigned as Supplier Taxes of Product '
                              'Template %s.' % pt.name))

        return super(AccountTax, self).write(vals)
