from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountTaxTemplate(models.Model):
    _inherit = 'account.tax.template'

    # We want to force the tax template to be blank always, because multiple
    # companies can potentially use this template to create taxes. We want
    # consistency company-wise.
    company_id = fields.Many2one(default=False, required=False)

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        names = super(AccountTaxTemplate, self).name_get()
        res = self.add_company_suffix(names)
        return res

    @api.multi
    def _get_family(self):
        tax_templates = self
        for tax_template in self:
            children = tax_template.children_tax_ids
            context = self._context.get('search_tax_parents')
            if context:
                children = children.filtered(lambda c: c.id not in context)
            if children:
                tax_templates |= children.\
                    with_context(search_tax_children=tax_template.ids).\
                    _get_family()
            parents = self.search(
                [('children_tax_ids', 'in', [tax_template.id])])
            context = self._context.get('search_tax_children')
            if context:
                parents = parents.filtered(lambda p: p.id not in context)
            if parents:
                tax_templates |= parents.\
                    with_context(search_tax_parents=tax_template.ids).\
                    _get_family()
        return tax_templates

    @api.multi
    def write(self, vals):
        company = False
        if vals.get('company_id') and \
                not self._context.get('stop_recursion_company'):
            company = vals['company_id']
            del vals['company_id']
        result = super(AccountTaxTemplate, self).write(vals)
        if company and not self._context.get('stop_recursion_company'):
            tax_templates = self._get_family()
            tax_templates = tax_templates.filtered(lambda t: t.company_id)
            tax_templates |= self
            result = result and tax_templates.with_context(
                stop_recursion_company=True).write(
                {'company_id': company})
        return result

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if not self.chart_template_id.check_company(self.company_id):
            if self.company_id.chart_template_id:
                self._cache.update(self._convert_to_cache(
                    {'chart_template_id': self.company_id.chart_template_id},
                    update=True))

    @api.multi
    @api.constrains('company_id', 'children_tax_ids')
    def _check_company_id_children_tax_ids(self):
        for rec in self.sudo():
            for line in rec.children_tax_ids:
                if not line.check_company(rec.company_id):
                    raise ValidationError(
                        _('The Company in the Account Tax Template and in '
                          'Account Tax Template (%s) must be '
                          'the same.') % line.name_get()[0][1])

    @api.multi
    @api.constrains('company_id', 'chart_template_id')
    def _check_company_id_chart_template_id(self):
        for rec in self.sudo():
            if not rec.chart_template_id.company_id.check_company(
                    rec.company_id):
                raise ValidationError(
                    _('The Company in the Account Tax Template and in '
                      'Account Chart Template must be the same.'))

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
            ('account.tax.template', [('children_tax_ids', 'in', self.ids)]),
        ]
        return res
