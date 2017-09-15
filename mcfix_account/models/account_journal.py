# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    @api.multi
    @api.depends('name', 'currency_id', 'company_id', 'company_id.currency_id')
    def name_get(self):
        res = []
        journal_names = super(AccountJournal, self).name_get()
        multicompany_group = self.env.ref('base.group_multi_company')
        if multicompany_group not in self.env.user.groups_id:
            return journal_names
        for journal_name in journal_names:
            journal = self.browse(journal_name[0])
            name = "%s [%s]" % (journal_name[1], journal.company_id.name)
            res += [(journal.id, name)]
        return res

    @api.multi
    @api.constrains('default_debit_account_id', 'company_id')
    def _check_company_debit_account(self):
        for journal in self:
            if journal.company_id and journal.default_debit_account_id and\
                    journal.company_id != journal.default_debit_account_id.\
                    company_id:
                raise ValidationError(_('The Company in the Journal and in '
                                        'Debit Account must be the same.'))
        return True

    @api.multi
    @api.constrains('default_credit_account_id', 'company_id')
    def _check_company_credit_account(self):
        for journal in self:
            if journal.company_id and journal.default_credit_account_id and\
                    journal.company_id != journal.default_credit_account_id.\
                    company_id:
                raise ValidationError(_('The Company in the Journal and in '
                                        'Credit Account must be the same.'))
        return True

    @api.multi
    @api.depends('company_id')
    def _belong_to_company_or_child(self):
        for journal in self:
            journal.belong_to_company_or_child = len(self.search(
                [('company_id', 'child_of', self.env.user.company_id.id)])) > 0

    @api.multi
    def _search_user_company_and_child_journals(self, operator, value):
        companies = self.env.user.company_id + \
                    self.env.user.company_id.child_ids
        if operator == '=':
            recs = self.search([('company_id', 'in', companies.ids)])
        elif operator == '!=':
            recs = self.search([('company_id', 'not in', companies.ids)])
        else:
            raise UserError(_("Invalid search operator."))

        return [('id', 'in', [x.id for x in recs])]

    belong_to_company_or_child = fields.Boolean(
        'Belong to the user\'s current child company',
        compute="_belong_to_company_or_child",
        search="_search_user_company_and_child_journals")
