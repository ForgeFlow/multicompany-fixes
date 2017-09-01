# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import ValidationError


class CrossoveredBudget(models.Model):
    _inherit = 'crossovered.budget'

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
            if budget.company_id and budget.creating_user_id and\
                    budget.company_id != budget.creating_user_id.company_id:
                raise ValidationError(_('The Company in the Budget '
                                        'and in person responsible'
                                        'must be the same.'))
        return True


class CrossoveredBudgetLines(models.Model):
    _inherit = 'crossovered.budget.lines'

    @api.multi
    @api.constrains('analytic_account_id', 'company_id')
    def _check_company_analytic_account(self):
        for budget in self:
            if budget.company_id and budget.analytic_account_id and\
                    budget.company_id != budget.analytic_account_id.company_id:
                raise ValidationError(_('The Company in the Budget '
                                        'and in Analytic Account must '
                                        'be the same.'))
        return True

    @api.multi
    @api.constrains('general_budget_id', 'company_id')
    def _check_company_general_budget(self):
        for budget in self:
            if budget.company_id and budget.general_budget_id and\
                    budget.company_id != budget.general_budget_id.company_id:
                raise ValidationError(_('The Company in the Budget '
                                        'and in Budgetary Position must '
                                        'be the same.'))
        return True
