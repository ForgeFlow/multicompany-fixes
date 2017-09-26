# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import ValidationError


# class AccountAccountTemplate(models.Model):
#     _inherit = "account.account.template"
#
#
# class AccountChartTemplate(models.Model):
#     _inherit = "account.chart.template"


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


# class AccountFiscalPositionTaxTemplate(models.Model):
#     _inherit = 'account.fiscal.position.tax.template'
#
#
# class AccountFiscalPositionAccountTemplate(models.Model):
#     _inherit = 'account.fiscal.position.account.template'
#
#
# class WizardMultiChartsAccounts(models.TransientModel):
#     _name = 'wizard.multi.charts.accounts'
#     _inherit = 'res.config'
#
#
# class AccountBankAccountsWizard(models.TransientModel):
#     _inherit = 'account.bank.accounts.wizard'
#
#
# class AccountReconcileModelTemplate(models.Model):
#     _inherit = "account.reconcile.model.template"
