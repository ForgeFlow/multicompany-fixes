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
        if not self.env.context.get('bypass_company_validation', False):
            for rec in self:
                if not rec.company_id:
                    continue
                field = self.env['account.tax.template'].search(
                    [('chart_template_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Account Chart Template is assigned to '
                          'Account Tax Template (%s)'
                          '.' % field.name_get()[0][1]))
                field = self.search(
                    [('parent_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Account Chart Template is assigned to '
                          'Account Chart Template (%s)'
                          '.' % field.name_get()[0][1]))


class WizardMultiChartsAccounts(models.TransientModel):
    _inherit = 'wizard.multi.charts.accounts'

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if self.company_id and self.chart_template_id.company_id and \
                self.chart_template_id.company_id != self.company_id:
            self.chart_template_id = self.company_id.chart_template_id
        if self.company_id and self.sale_tax_id.company_id and \
                self.sale_tax_id.company_id != self.company_id:
            self.sale_tax_id = False
        if self.company_id and self.purchase_tax_id.company_id and \
                self.purchase_tax_id.company_id != self.company_id:
            self.purchase_tax_id = False

    @api.multi
    @api.constrains('company_id', 'sale_tax_id')
    def _check_company_id_sale_tax_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.sale_tax_id.company_id and\
                    rec.company_id != rec.sale_tax_id.company_id:
                raise ValidationError(
                    _('The Company in the Wizard Multi Charts Accounts and in '
                      'Account Tax Template must be the same.'))

    @api.multi
    @api.constrains('company_id', 'purchase_tax_id')
    def _check_company_id_purchase_tax_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.purchase_tax_id.company_id and\
                    rec.company_id != rec.purchase_tax_id.company_id:
                raise ValidationError(
                    _('The Company in the Wizard Multi Charts Accounts and in '
                      'Account Tax Template must be the same.'))

    @api.multi
    @api.constrains('company_id', 'chart_template_id')
    def _check_company_id_chart_template_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.chart_template_id.company_id and\
                    rec.company_id != rec.chart_template_id.company_id:
                raise ValidationError(
                    _('The Company in the Wizard Multi Charts Accounts and in '
                      'Account Chart Template must be the same.'))
