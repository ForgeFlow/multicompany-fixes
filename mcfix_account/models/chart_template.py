# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import ValidationError


# class AccountAccountTemplate(models.Model):
#     _inherit = "account.account.template"
#
#
class AccountChartTemplate(models.Model):
    _inherit = "account.chart.template"

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        res = []
        names = super(AccountChartTemplate, self).name_get()
        multicompany_group = self.env.ref('base.group_multi_company')
        if multicompany_group not in self.env.user.groups_id:
            return names
        for name in names:
            rec = self.browse(name[0])
            name = '%s [%s]' % (name[1], name.company_id.name) if \
                name.company_id else name[1]
            res += [(rec.id, name)]
        return res

    @api.onchange('company_id')
    def onchange_company_id(self):
        self.parent_id = False
        self.tax_template_ids = False

    @api.multi
    @api.constrains('parent_id', 'company_id')
    def _check_company_parent_id(self):
        for chart_template in self.sudo():
            if chart_template.company_id and chart_template.parent_id and \
                    chart_template.company_id != chart_template.\
                    parent_id.company_id:
                raise ValidationError(
                    _('The Company in the Chart Template and in '
                      'Parent Chart Template must be the same.'))
        return True

    @api.multi
    @api.constrains('tax_template_ids', 'company_id')
    def _check_company_tax_template_ids(self):
        for chart_template in self.sudo():
            for tax_template in chart_template.tax_template_ids:
                if chart_template.company_id and \
                        chart_template.company_id != tax_template.\
                        company_id:
                    raise ValidationError(
                        _('The Company in the Chart Template and in '
                          'Tax Template List %s must be the same.'
                          ) % tax_template.name)
        return True


class AccountTaxTemplate(models.Model):
    _inherit = 'account.tax.template'

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        res = []
        names = super(AccountTaxTemplate, self).name_get()
        multicompany_group = self.env.ref('base.group_multi_company')
        if multicompany_group not in self.env.user.groups_id:
            return names
        for name in names:
            rec = self.browse(name[0])
            name = '%s [%s]' % (name[1], name.company_id.name) if \
                name.company_id else name[1]
            res += [(rec.id, name)]
        return res

    @api.onchange('company_id')
    def onchange_company_id(self):
        self.chart_template_id = False
        self.children_tax_ids = False

    @api.multi
    @api.constrains('chart_template_id', 'company_id')
    def _check_company_chart_template_id(self):
        for tax_template in self.sudo():
            if tax_template.company_id and tax_template.chart_template_id and \
                    tax_template.company_id != tax_template.\
                    chart_template_id.company_id:
                raise ValidationError(
                    _('The Company in the Tax Template and in '
                      'Chart Template must be the same.'))
        return True

    @api.multi
    @api.constrains('children_tax_ids', 'company_id')
    def _check_company_children_tax_ids(self):
        for tax_template in self.sudo():
            for account in tax_template.children_tax_ids:
                if tax_template.company_id and \
                        tax_template.company_id != account.company_id:
                    raise ValidationError(
                        _(
                            'The Company in the Tax Template and in '
                            'Children Taxes must be the same.'))
        return True

    @api.constrains('company_id')
    def _check_company_id(self):
        for rec in self:
            tax_template = self.search(
                [('children_tax_ids', 'in', [rec.id]),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if tax_template:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'tax is child tax of Tax %s.' % tax_template.name))
            multi_charts_accounts = self.env[
                'wizard.multi.charts.accounts'].search(
                [('sale_tax_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if multi_charts_accounts:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Sales Tax is assigned to Multi Charts Account '
                      '%s.' % multi_charts_accounts.name))
            multi_charts_accounts = self.env[
                'wizard.multi.charts.accounts'].search(
                [('purchase_tax_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if multi_charts_accounts:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Purchase Tax is assigned to Multi Charts Account '
                      '%s.' % multi_charts_accounts.name))
            chart_template = self.env['account.chart.template'].search(
                [('tax_template_ids', 'in', [rec.id]),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if chart_template:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Tax Template is assigned to Chart Template '
                      '%s.' % chart_template.name))


class WizardMultiChartsAccounts(models.TransientModel):
    _inherit = 'wizard.multi.charts.accounts'

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        res = []
        names = super(WizardMultiChartsAccounts, self).name_get()
        multicompany_group = self.env.ref('base.group_multi_company')
        if multicompany_group not in self.env.user.groups_id:
            return names
        for name in names:
            rec = self.browse(name[0])
            name = '%s [%s]' % (name[1], name.company_id.name) if \
                name.company_id else name[1]
            res += [(rec.id, name)]
        return res

    @api.onchange('company_id')
    def onchange_company_id(self):
        self.chart_template_id = False
        self.sale_tax_id = False
        self.purchase_tax_id = False

    @api.multi
    @api.constrains('chart_template_id', 'company_id')
    def _check_company_chart_template_id(self):
        for multi_charts_accounts in self.sudo():
            if multi_charts_accounts.company_id and multi_charts_accounts.\
                    chart_template_id and multi_charts_accounts.company_id !=\
                    multi_charts_accounts.chart_template_id.company_id:
                raise ValidationError(
                    _('The Company in the Multi Charts Accounts and in '
                      'Chart Template must be the same.'))
        return True

    @api.multi
    @api.constrains('sale_tax_id', 'company_id')
    def _check_company_sale_tax_id(self):
        for multi_charts_accounts in self.sudo():
            if multi_charts_accounts.company_id and multi_charts_accounts.\
                    sale_tax_id and multi_charts_accounts.company_id != \
                    multi_charts_accounts.sale_tax_id.company_id:
                raise ValidationError(
                    _('The Company in the Multi Charts Accounts and in '
                      'Default Sales Tax must be the same.'))
        return True

    @api.multi
    @api.constrains('purchase_tax_id', 'company_id')
    def _check_company_purchase_tax_id(self):
        for multi_charts_accounts in self.sudo():
            if multi_charts_accounts.company_id and multi_charts_accounts.\
                    purchase_tax_id and multi_charts_accounts.company_id != \
                    multi_charts_accounts.purchase_tax_id.company_id:
                raise ValidationError(
                    _('The Company in the Multi Charts Accounts and in '
                      'Default Purchase Tax must be the same.'))
        return True
