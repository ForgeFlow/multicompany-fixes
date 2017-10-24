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
            name = "%s [%s]" % (name[1], rec.company_id.name) if \
                rec.company_id else name[1]
            res += [(rec.id, name)]
        return res

    @api.onchange('company_id')
    def onchange_company_id(self):
        self.account_id = False
        self.refund_account_id = False
        self.children_tax_ids = False

    @api.multi
    @api.constrains('children_tax_ids', 'company_id')
    def _check_company_children_tax_ids(self):
        for tax in self.sudo():
            for children_tax in tax.children_tax_ids:
                if tax.company_id and children_tax.company_id and \
                        tax.company_id != children_tax.company_id:
                    raise ValidationError(
                        _('The Company in the Tax and in Children Tax %s '
                          'must be the same.') % children_tax.name)
        return True

    @api.multi
    @api.constrains('account_id', 'company_id')
    def _check_company_account_id(self):
        for tax in self.sudo():
            if tax.company_id and tax.account_id.company_id and \
                    tax.company_id != tax.account_id.company_id:
                raise ValidationError(_('The Company in the Tax and in '
                                        'Tax Account must be the same.'))
        return True

    @api.multi
    @api.constrains('refund_account_id', 'company_id')
    def _check_company_refund_account_id(self):
        for tax in self.sudo():
            if tax.company_id and tax.refund_account_id.company_id and \
                    tax.company_id != tax.refund_account_id.company_id:
                raise ValidationError(_('The Company in the Tax and in '
                                        'Tax Account on Refunds must be the'
                                        ' same.'))
        return True

    @api.constrains('company_id')
    def _check_company_id(self):
        for rec in self:
            # Invoice
            invoice_tax = self.env['account.invoice.tax'].search(
                [('tax_id', '=', rec.id),
                 ('company_id', '!=', False),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if invoice_tax:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'tax is assigned to Invoice Tax %s in invoice '
                      '%s.' % (invoice_tax.name,
                               invoice_tax.invoice_id.name)))

            invoice_line = self.env['account.invoice.line'].search(
                [('invoice_line_tax_ids', 'in', [rec.id]),
                 ('company_id', '!=', False),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if invoice_line:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'tax is assigned to invoice line %s in invoice '
                      '%s.' % (invoice_line.name,
                               invoice_line.invoice_id.name)))

            # Account Tax
            parent_tax = self.search(
                [('children_tax_ids', 'in', [rec.id]),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if parent_tax:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'tax is child tax of Tax %s.' %
                      parent_tax.name))

            # Account Move Line
            aml = self.env['account.move.line'].search(
                [('tax_ids', 'in', [rec.id]),
                 ('company_id', '!=', False),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if aml:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'tax is assigned to Move Line %s of '
                      'Move %s.' % (aml.name, aml.move_id.name)))

            aml = self.env['account.move.line'].search(
                [('tax_line_id', '=', rec.id),
                 ('company_id', '!=', False),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if aml:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'tax is assigned to Move Line %s of '
                      'Move %s.' % (aml.name, aml.move_id.name)))

            # Account Account
            account = self.env['account.account'].search(
                [('tax_ids', 'in', [rec.id]),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if account:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'tax is assigned to Account '
                      '%s.' % account.name))

            # Account Reconcile Model
            reconcile_model = self.env['account.reconcile.model'].search(
                [('tax_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if reconcile_model:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'tax is assigned to Reconcile Model '
                      '%s.' % reconcile_model.name))

            reconcile_model = self.env['account.reconcile.model'].search(
                [('second_tax_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if reconcile_model:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'tax is assigned to Reconcile Model '
                      '%s.' % reconcile_model.name))

            # Account Config Settings
            config_settings = self.env['account.config.settings'].search(
                [('default_sale_tax_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if config_settings:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'tax is assigned to Config Settings '
                      '%s.' % config_settings.name))

            config_settings = self.env['account.config.settings'].search(
                [('default_purchase_tax_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if config_settings:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'tax is assigned to Config Settings '
                      '%s.' % config_settings.name))

            # Product Template
            template = self.env['product.template'].search(
                [('taxes_id', 'in', [rec.id]),
                 ('company_id', '!=', False),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if template:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'tax is assigned to Product Template '
                      '%s.' % template.name))

            template = self.env['product.template'].search(
                [('supplier_taxes_id', 'in', [rec.id]),
                 ('company_id', '!=', False),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if template:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'tax is assigned to Product Template '
                      '%s.' % template.name))
