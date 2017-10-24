# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import ValidationError


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
            name = '%s [%s]' % (name[1], rec.company_id.name) if \
                rec.company_id else name[1]
            res += [(rec.id, name)]
        return res

    @api.onchange('company_id')
    def onchange_company_id(self):
        self.parent_id = False

    @api.multi
    @api.constrains('parent_id', 'company_id')
    def _check_company_parent_id(self):
        for chart_template in self.sudo():
            if chart_template.company_id and chart_template.parent_id.\
                    company_id and chart_template.company_id != chart_template\
                    .parent_id.company_id:
                raise ValidationError(
                    _('The Company in the Chart Template and in '
                      'Parent Chart Template must be the same.'))
        return True

    @api.constrains('company_id')
    def _check_company_id(self):
        for rec in self:
            if not rec.company_id:
                continue
            tax_template = self.env['account.tax.template'].search(
                [('chart_template_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if tax_template:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Chart Template is assigned to Tax Template '
                      '%s.' % tax_template.name))
            multi_charts_accounts = self.env[
                'wizard.multi.charts.accounts'].search(
                [('chart_template_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if multi_charts_accounts:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'chart template is assigned to Multi Charts Account '
                      '%s.' % multi_charts_accounts.name))
            chart_template = self.search(
                [('parent_id', '=', rec.id),
                 ('company_id', '!=', False),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if chart_template:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'chart template is parent of Chart Template '
                      '%s.' % chart_template.name))
            config_settings = self.env['account.config.settings'].search(
                [('chart_template_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if config_settings:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'chart template is assigned to Config Settings '
                      '%s.' % config_settings.name))
            company = self.env['res.company'].search(
                [('chart_template_id', '=', rec.id),
                 ('company_id', '!=', False),
                 ('parent_id', '!=', rec.company_id.id)], limit=1)
            if company:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'chart template is assigned to Company '
                      '%s.' % company.name))


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
            name = '%s [%s]' % (name[1], rec.company_id.name) if \
                rec.company_id else name[1]
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
            if tax_template.company_id and \
                    tax_template.chart_template_id.company_id and \
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
                if tax_template.company_id and account.company_id and \
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
            config_settings = self.env['account.config.settings'].search(
                [('sale_tax_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if config_settings:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Sales tax is assigned to Config Settings '
                      '%s.' % config_settings.name))
            config_settings = self.env['account.config.settings'].search(
                [('purchase_tax_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if config_settings:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Purchase tax is assigned to Config Settings '
                      '%s.' % config_settings.name))


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
            name = '%s [%s]' % (name[1], rec.company_id.name) if \
                rec.company_id else name[1]
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
                    chart_template_id.company_id and multi_charts_accounts.\
                    company_id != multi_charts_accounts.chart_template_id.\
                    company_id:
                raise ValidationError(
                    _('The Company in the Multi Charts Accounts and in '
                      'Chart Template must be the same.'))
        return True

    @api.multi
    @api.constrains('sale_tax_id', 'company_id')
    def _check_company_sale_tax_id(self):
        for multi_charts_accounts in self.sudo():
            if multi_charts_accounts.company_id and multi_charts_accounts.\
                    sale_tax_id.company_id and multi_charts_accounts.\
                    company_id != multi_charts_accounts.sale_tax_id.company_id:
                raise ValidationError(
                    _('The Company in the Multi Charts Accounts and in '
                      'Default Sales Tax must be the same.'))
        return True

    @api.multi
    @api.constrains('purchase_tax_id', 'company_id')
    def _check_company_purchase_tax_id(self):
        for multi_charts_accounts in self.sudo():
            if multi_charts_accounts.company_id and multi_charts_accounts.\
                    purchase_tax_id.company_id and multi_charts_accounts.\
                    company_id != multi_charts_accounts.purchase_tax_id.\
                    company_id:
                raise ValidationError(
                    _('The Company in the Multi Charts Accounts and in '
                      'Default Purchase Tax must be the same.'))
        return True
