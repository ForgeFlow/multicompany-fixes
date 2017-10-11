# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import ValidationError


class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        res = []
        names = super(AccountBankStatement, self).name_get()
        multicompany_group = self.env.ref('base.group_multi_company')
        if multicompany_group not in self.env.user.groups_id:
            return names
        for name in names:
            rec = self.browse(name[0])
            name = "%s [%s]" % (name[1], rec.company_id.name) if \
                rec.company_id else name[1]
            res += [(rec.id, name)]
        return res

    @api.onchange('company_id')
    def onchange_company_id(self):
        self.journal_id = False

    def reconciliation_widget_preprocess(self):
        # This is the same code as the original method except for the fact
        # that here will fetch bank statement data for the child companies
        res = super(AccountBankStatement,
                    self).reconciliation_widget_preprocess()
        statements = self
        child_companies = self.env.user.company_id.child_ids
        child_company_ids = child_companies and tuple(child_companies.ids)

        sql_query = """SELECT stl.id
                        FROM account_bank_statement_line stl
                        WHERE account_id IS NULL AND not exists
                        (select 1 from account_move m where
                        m.statement_line_id = stl.id)
                            AND company_id in %s
                """
        params = (child_company_ids,)
        if statements:
            sql_query += ' AND stl.statement_id IN %s'
            params += (tuple(statements.ids),)
        sql_query += ' ORDER BY stl.id'
        self.env.cr.execute(sql_query, params)
        st_lines_left = self.env['account.bank.statement.line'].browse(
            [line.get('id') for line in self.env.cr.dictfetchall()])

        # try to assign partner to bank_statement_line
        stl_to_assign_partner = [stl.id for stl in st_lines_left if
                                 not stl.partner_id]
        refs = list(set([st.name for st in st_lines_left
                         if not stl.partner_id]))
        if st_lines_left and stl_to_assign_partner and refs \
                and st_lines_left[0].journal_id.default_credit_account_id \
                and st_lines_left[0].journal_id.default_debit_account_id:

            sql_query = """SELECT aml.partner_id, aml.ref, stl.id
                            FROM account_move_line aml
                                JOIN account_account acc
                                ON acc.id = aml.account_id
                                JOIN account_bank_statement_line stl
                                ON aml.ref = stl.name
                            WHERE (aml.company_id in %s
                                AND aml.partner_id IS NOT NULL)
                                AND (
                                    (aml.statement_id IS NULL
                                    AND aml.account_id IN %s)
                                    OR
                                    (acc.internal_type IN
                                    ('payable', 'receivable')
                                    AND aml.reconciled = false)
                                    )
                                AND aml.ref IN %s
                                """
            params = (child_company_ids, (
                st_lines_left[0].journal_id.default_credit_account_id.id,
                st_lines_left[0].journal_id.default_debit_account_id.id),
                tuple(refs))
            if statements:
                sql_query += 'AND stl.id IN %s'
                params += (tuple(stl_to_assign_partner),)
            self.env.cr.execute(sql_query, params)
            results = self.env.cr.dictfetchall()
            st_line = self.env['account.bank.statement.line']
            for line in results:
                st_line.browse(line.get('id')).write(
                    {'partner_id': line.get('partner_id')})

        res['st_lines_ids'] += st_lines_left.ids
        return res

    @api.multi
    @api.constrains('journal_id', 'company_id')
    def _check_company_journal_id(self):
        for bank_statement in self.sudo():
            if bank_statement.company_id and bank_statement.journal_id.\
                    company_id and bank_statement.company_id != bank_statement\
                    .journal_id.company_id:
                raise ValidationError(
                    _('The Company in the Bank Statement and in '
                      'Journal must be the same.'))
        return True

    @api.constrains('company_id')
    def _check_company_id(self):
        for rec in self:
            move_line = self.env['account.move.line'].search(
                [('statement_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if move_line:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Statement is assigned to Move Line '
                      '%s of Move %s.' % (move_line.name,
                                          move_line.move_id.name)))
            bank_statement_line = self.env[
                'account.bank.statement.line'].search(
                [('statement_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if bank_statement_line:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Statement is assigned to Bank Statement Line '
                      '%s in Bank Statement %s.' % (
                          bank_statement_line.name,
                          bank_statement_line.statement_id.name)))


class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    @api.depends('company_id')
    def name_get(self):
        res = []
        names = super(AccountBankStatementLine, self).name_get()
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
        self.account_id = False
        self.statement_id = False
        self.journal_id = False

    @api.multi
    @api.constrains('account_id', 'company_id')
    def _check_company_account_id(self):
        for bank_statement_line in self.sudo():
            if bank_statement_line.company_id and bank_statement_line.\
                    account_id.company_id and bank_statement_line.\
                    company_id != bank_statement_line.account_id.company_id:
                raise ValidationError(
                    _('The Company in the Bank Statement Line and in '
                      'Counterpart Account must be the same.'))
        return True

    @api.multi
    @api.constrains('statement_id', 'company_id')
    def _check_company_statement_id(self):
        for bank_statement_line in self.sudo():
            if bank_statement_line.company_id and bank_statement_line.\
                    statement_id.company_id and bank_statement_line.\
                    company_id != bank_statement_line.statement_id.company_id:
                raise ValidationError(
                    _('The Company in the Bank Statement Line and in '
                      'Bank Statement must be the same.'))
        return True

    @api.multi
    @api.constrains('journal_id', 'company_id')
    def _check_company_journal_id(self):
        for bank_statement_line in self.sudo():
            if bank_statement_line.company_id and bank_statement_line.\
                    journal_id.company_id and bank_statement_line.\
                    company_id != bank_statement_line.journal_id.company_id:
                raise ValidationError(
                    _('The Company in the Bank Statement Line and in '
                      'Journal must be the same.'))
        return True

    @api.constrains('company_id')
    def _check_company_id(self):
        for rec in self:
            if not rec.company_id:
                continue
            move = self.env['account.move'].search(
                [('statement_line_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)],
                limit=1)
            if move:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Bank statement line is assigned to Move '
                      '%s.' % move.name))
