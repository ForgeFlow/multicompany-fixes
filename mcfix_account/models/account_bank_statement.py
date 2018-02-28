from odoo import api, models, _
from odoo.exceptions import ValidationError


class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"

    @api.multi
    def reconciliation_widget_preprocess(self):
        # This is the same code as the original method except for the fact
        # that here will fetch bank statement data for the child companies
        res = super(AccountBankStatement,
                    self).reconciliation_widget_preprocess()
        statements = self
        sql_query = """SELECT stl.id
                        FROM account_bank_statement_line stl
                        WHERE account_id IS NULL AND stl.amount != 0.0 AND
                        not exists (select 1 from account_move_line aml where
                        aml.statement_line_id = stl.id)
                            AND company_id = %s
                            """
        company_id = statements.mapped('company_id').ids[0]
        params = (company_id,)  # All statements have same company
        if statements:
            sql_query += 'AND stl.statement_id IN %s'
            params += (tuple(statements.ids),)
        sql_query += ' ORDER BY stl.id'
        self.env.cr.execute(sql_query, params)
        st_lines_left = self.env['account.bank.statement.line'].browse(
            [line.get('id') for line in self.env.cr.dictfetchall()])

        # try to assign partner to bank_statement_line
        stl_to_assign = st_lines_left.filtered(lambda stl: not stl.partner_id)
        refs = set(stl_to_assign.mapped('name'))
        if stl_to_assign and refs \
                and st_lines_left[0].journal_id.default_credit_account_id \
                and st_lines_left[0].journal_id.default_debit_account_id:

            sql_query = """SELECT aml.partner_id, aml.ref, stl.id
                            FROM account_move_line aml
                                JOIN account_account acc
                                ON acc.id = aml.account_id
                                JOIN account_bank_statement_line stl
                                ON aml.ref = stl.name
                            WHERE (aml.company_id = %s
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
            params = (company_id, (
                st_lines_left[0].journal_id.default_credit_account_id.id,
                st_lines_left[0].journal_id.default_debit_account_id.id),
                tuple(refs))
            if statements:
                sql_query += 'AND stl.id IN %s'
                params += (tuple(stl_to_assign.ids),)
            self.env.cr.execute(sql_query, params)
            results = self.env.cr.dictfetchall()
            st_line = self.env['account.bank.statement.line']
            for line in results:
                st_line.browse(line.get('id')).write(
                    {'partner_id': line.get('partner_id')})

        res['st_lines_ids'] = st_lines_left.ids
        return res

    @api.multi
    @api.constrains('company_id', 'journal_id')
    def _check_company_id_journal_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.journal_id.company_id and\
                    rec.company_id != rec.journal_id.company_id:
                raise ValidationError(
                    _('The Company in the Account Bank Statement and in '
                      'Account Journal must be the same.'))

    @api.constrains('company_id')
    def _check_company_id_out_model(self):
        if not self.env.context.get('bypass_company_validation', False):
            for rec in self:
                if not rec.company_id:
                    continue
                field = self.env['account.move.line'].search(
                    [('statement_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Account Bank Statement is assigned to '
                          'Account Move Line (%s).' % field.name_get()[0][1]))
                field = self.env['account.bank.statement.line'].search(
                    [('statement_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Account Bank Statement is assigned to '
                          'Account Bank Statement Line (%s)'
                          '.' % field.name_get()[0][1]))


class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    def get_move_lines_for_reconciliation(
            self, partner_id=None, excluded_ids=None, str=False,
            offset=0, limit=None, additional_domain=None,
            overlook_partner=False):
        res = super(AccountBankStatementLine,
                    self).get_move_lines_for_reconciliation(
            partner_id=partner_id, excluded_ids=excluded_ids, str=str,
            offset=offset, limit=limit, additional_domain=additional_domain,
            overlook_partner=overlook_partner)
        return res.filtered(lambda x: x.company_id == self.company_id)

    def get_statement_line_for_reconciliation_widget(self):
        data = super(AccountBankStatementLine, self).\
            get_statement_line_for_reconciliation_widget()
        data['company_id'] = self.company_id.id
        return data

    @api.multi
    @api.constrains('company_id', 'partner_id')
    def _check_company_id_partner_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.partner_id.company_id and\
                    rec.company_id != rec.partner_id.company_id:
                raise ValidationError(
                    _('The Company in the Account Bank Statement Line and in '
                      'Res Partner must be the same.'))

    @api.multi
    @api.constrains('company_id', 'journal_id')
    def _check_company_id_journal_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.journal_id.company_id and\
                    rec.company_id != rec.journal_id.company_id:
                raise ValidationError(
                    _('The Company in the Account Bank Statement Line and in '
                      'Account Journal must be the same.'))

    @api.multi
    @api.constrains('company_id', 'statement_id')
    def _check_company_id_statement_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.statement_id.company_id and\
                    rec.company_id != rec.statement_id.company_id:
                raise ValidationError(
                    _('The Company in the Account Bank Statement Line and in '
                      'Account Bank Statement must be the same.'))

    @api.multi
    @api.constrains('company_id', 'bank_account_id')
    def _check_company_id_bank_account_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.bank_account_id.company_id and\
                    rec.company_id != rec.bank_account_id.company_id:
                raise ValidationError(
                    _('The Company in the Account Bank Statement Line and in '
                      'Res Partner Bank must be the same.'))

    @api.multi
    @api.constrains('company_id', 'account_id')
    def _check_company_id_account_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.account_id.company_id and\
                    rec.company_id != rec.account_id.company_id:
                raise ValidationError(
                    _('The Company in the Account Bank Statement Line and in '
                      'Account Account must be the same.'))

    @api.constrains('company_id')
    def _check_company_id_out_model(self):
        if not self.env.context.get('bypass_company_validation', False):
            for rec in self:
                if not rec.company_id:
                    continue
                field = self.env['account.move.line'].search(
                    [('statement_line_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Account Bank Statement Line is assigned to '
                          'Account Move Line (%s).' % field.name_get()[0][1]))
