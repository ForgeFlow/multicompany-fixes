from odoo import api, models, _
from odoo.exceptions import ValidationError


class AccountChartTemplate(models.Model):
    _inherit = "account.chart.template"

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        names = super(AccountChartTemplate, self).name_get()
        res = self.add_company_suffix(names)
        return res

    @api.multi
    def _get_top_parent(self):
        parent = self.env['account.chart.template']
        for chart in self:
            if chart.parent_id:
                parent |= chart.parent_id._get_top_parent()
            else:
                parent |= self
        return parent

    @api.multi
    def _get_all_children(self):
        childs = self
        for chart in self:
            child_ids = self.search(
                [('parent_id', '=', chart.id)])
            if child_ids:
                childs |= child_ids._get_all_children()
        return childs

    @api.multi
    def write(self, vals):
        company = False
        if vals.get('company_id') and \
                not self._context.get('stop_recursion_company'):
            company = vals['company_id']
            del vals['company_id']
        result = super(AccountChartTemplate, self).write(vals)
        if company and not self._context.get('stop_recursion_company'):
            top_parent = self._get_top_parent()
            charts = top_parent._get_all_children()
            charts = charts.filtered(lambda c: c.company_id)
            charts |= self
            result = result and charts.with_context(
                stop_recursion_company=True).write(
                {'company_id': company})
        return result

    @api.multi
    @api.constrains('company_id', 'parent_id')
    def _check_company_id_parent_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.parent_id.company_id and\
                    rec.company_id != rec.parent_id.company_id:
                raise ValidationError(
                    _('The Company in the Account Chart Template and in '
                      'Account Chart Template must be the same.'))

    @api.constrains('company_id')
    def _check_company_id_out_model(self):
        self._check_company_id_base_model()

    def _check_company_id_search(self):
        res = super()._check_company_id_search()
        res = res + [
            ('account.tax.template', [('chart_template_id', '=', self.id)]),
            ('account.chart.template', [('parent_id', '=', self.id)]),
        ]
        return res


class WizardMultiChartsAccounts(models.TransientModel):
    _inherit = 'wizard.multi.charts.accounts'

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if not self.chart_template_id.check_company(self.company_id):
            self.chart_template_id = self.company_id.chart_template_id
        if not self.sale_tax_id.check_company(self.company_id):
            self.sale_tax_id = False
        if not self.purchase_tax_id.check_company(self.company_id):
            self.purchase_tax_id = False

    @api.multi
    @api.constrains('company_id', 'sale_tax_id')
    def _check_company_id_sale_tax_id(self):
        for rec in self.sudo():
            if not rec.sale_tax_id.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Wizard Multi Charts Accounts and in '
                      'Account Tax Template must be the same.'))

    @api.multi
    @api.constrains('company_id', 'purchase_tax_id')
    def _check_company_id_purchase_tax_id(self):
        for rec in self.sudo():
            if not rec.purchase_tax_id.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Wizard Multi Charts Accounts and in '
                      'Account Tax Template must be the same.'))

    @api.multi
    @api.constrains('company_id', 'chart_template_id')
    def _check_company_id_chart_template_id(self):
        for rec in self.sudo():
            if not rec.chart_template_id.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Wizard Multi Charts Accounts and in '
                      'Account Chart Template must be the same.'))
