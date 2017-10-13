# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import ValidationError


class AccountBudgetPost(models.Model):
    _inherit = 'account.budget.post'

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        res = []
        names = super(AccountBudgetPost, self).name_get()
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
        self.account_ids = False

    @api.multi
    @api.constrains('account_ids', 'company_id')
    def _check_company_account_ids(self):
        for budget_post in self.sudo():
            for account in budget_post.account_ids:
                if budget_post.company_id and account.company_id and \
                        budget_post.company_id != account.company_id:
                    raise ValidationError(
                        _('The Company in the Budget Post and in '
                          'Account must be the same.'))
        return True


class CrossoveredBudget(models.Model):
    _inherit = 'crossovered.budget'

    def name_get(self):
        res = []
        names = super(CrossoveredBudget, self).name_get()
        multicompany_group = self.env.ref('base.group_multi_company')
        if multicompany_group not in self.env.user.groups_id:
            return names
        for name in names:
            rec = self.browse(name[0])
            name = '%s [%s]' % (name[1], rec.company_id.name) if \
                rec.company_id else name[1]
            res += [(rec.id, name)]
        return res

    @api.multi
    @api.onchange('company_id')
    def onchange_company_id(self):
        res = {}
        for budget in self:
            user = self.env['res.users'].\
                search([('company_id', '=', budget.company_id.id)], limit=1)
            budget.creating_user_id = user
        return res

    @api.constrains('creating_user_id', 'company_id')
    def _check_company_creating_user(self):
        for budget in self:
            if budget.company_id and budget.creating_user_id.company_id and\
                    budget.company_id != budget.creating_user_id.company_id:
                raise ValidationError(
                    _('The Company in the Budget '
                      'and in person responsible'
                      'must be the same.'))
        return True


class CrossoveredBudgetLines(models.Model):
    _inherit = 'crossovered.budget.lines'

    @api.multi
    @api.constrains('analytic_account_id', 'company_id')
    def _check_company_analytic_account(self):
        for budget in self:
            if budget.company_id and budget.analytic_account_id.company_id and\
                    budget.company_id != budget.analytic_account_id.company_id:
                raise ValidationError(_('The Company in the Budget '
                                        'and in Analytic Account must '
                                        'be the same.'))
        return True

    @api.multi
    @api.constrains('general_budget_id', 'company_id')
    def _check_company_general_budget(self):
        for budget in self:
            if budget.company_id and budget.general_budget_id.company_id and\
                    budget.company_id != budget.general_budget_id.company_id:
                raise ValidationError(_('The Company in the Budget '
                                        'and in Budgetary Position must '
                                        'be the same.'))
        return True
