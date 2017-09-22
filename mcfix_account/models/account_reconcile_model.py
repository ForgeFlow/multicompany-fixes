from odoo import api, models, _
from odoo.exceptions import ValidationError


class AccountReconcileModel(models.Model):
    _inherit = "account.reconcile.model"

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        res = []
        names = super(AccountReconcileModel, self).name_get()
        multicompany_group = self.env.ref('base.group_multi_company')
        if multicompany_group not in self.env.user.groups_id:
            return names
        for name in names:
            rec = self.browse(name[0])
            name = "%s [%s]" % (name[1], name.company_id.name) if \
                name.company_id else name[1]
            res += [(rec.id, name)]
        return res

    @api.multi
    @api.onchange('company_id')
    def onchange_company_id(self):
        for reconcile in self:
            reconcile.account_id = False
            reconcile.journal_id = False
            reconcile.tax_id = False
            reconcile.analytic_account_id = False
            reconcile.second_account_id = False
            reconcile.second_journal_id = False
            reconcile.second_tax_id = False
            reconcile.second_analytic_account_id = False

    @api.multi
    @api.constrains('account_id', 'company_id')
    def _check_company_account_id(self):
        for reconcile in self:
            if (
                reconcile.company_id and reconcile.account_id.company_id and
                reconcile.company_id != reconcile.account_id.company_id
            ):
                raise ValidationError(
                    _('The Company in the Reconciliation model and in the '
                      'Account must be the same.'))
        return True

    @api.multi
    @api.constrains('journal_id', 'company_id')
    def _check_company_journal_id(self):
        for reconcile in self:
            if (
                reconcile.company_id and reconcile.journal_id.company_id and
                reconcile.company_id != reconcile.journal_id.company_id
            ):
                raise ValidationError(
                    _('The Company in the Reconciliation model and in the '
                      'Journal must be the same.'))
        return True

    @api.multi
    @api.constrains('tax_id', 'company_id')
    def _check_company_tax_id(self):
        for reconcile in self:
            if (
                reconcile.company_id and reconcile.tax_id.company_id and
                reconcile.company_id != reconcile.tax_id.company_id
            ):
                raise ValidationError(
                    _('The Company in the Reconciliation model and in the '
                      'Tax must be the same.'))
        return True
