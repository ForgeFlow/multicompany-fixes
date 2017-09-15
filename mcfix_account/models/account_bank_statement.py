
from odoo import api, fields, models, _


class AccountBankStatement(models.Model):

    _inherit = "account.bank.statement"

    @api.multi
    def reconciliation_widget_preprocess(self):
        res = super(AccountBankStatement,
                    self).reconciliation_widget_preprocess()
        statements = self
        child_companies = self.env.user.company_id.child_ids
        child_company_ids = child_companies and tuple(child_companies.ids)

        sql_query = """SELECT stl.id 
                        FROM account_bank_statement_line stl  
                        WHERE account_id IS NULL AND not exists (select 1 from account_move m where m.statement_line_id = stl.id)
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
        refs = list(set([st.name for st in st_lines_left if not stl.partner_id]))
        if st_lines_left and stl_to_assign_partner and refs \
                and st_lines_left[0].journal_id.default_credit_account_id \
                and st_lines_left[0].journal_id.default_debit_account_id:

            sql_query = """SELECT aml.partner_id, aml.ref, stl.id
                            FROM account_move_line aml
                                JOIN account_account acc ON acc.id = aml.account_id
                                JOIN account_bank_statement_line stl ON aml.ref = stl.name
                            WHERE (aml.company_id in %s 
                                AND aml.partner_id IS NOT NULL) 
                                AND (
                                    (aml.statement_id IS NULL AND aml.account_id IN %s) 
                                    OR 
                                    (acc.internal_type IN ('payable', 'receivable') AND aml.reconciled = false)
                                    )
                                AND aml.ref IN %s
                                """
            params = (child_company_ids, (
            st_lines_left[0].journal_id.default_credit_account_id.id,
            st_lines_left[0].journal_id.default_debit_account_id.id), tuple(refs))
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
