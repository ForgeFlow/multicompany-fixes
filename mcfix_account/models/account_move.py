# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import UserError, ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        res = []
        names = super(AccountMove, self).name_get()
        multicompany_group = self.env.ref('base.group_multi_company')
        if multicompany_group not in self.env.user.groups_id:
            return names
        for name in names:
            rec = self.browse(name[0])
            name = "%s [%s]" % (name[1], name.company_id.name) if \
                name.company_id else name[1]
            res += [(rec.id, name)]
        return res

    @api.onchange('company_id')
    def onchange_company_id(self):
        self.journal_id = False
        self.line_ids = False
        self.dummy_account_id = False

    @api.multi
    def _get_default_journal(self):
        if self.env.context.get('default_journal_type'):
            return self.env['account.journal'].search(
                [('type', '=', self.env.context['default_journal_type']),
                 ('company_id', '=', self.env.user.company_id)],
                limit=1).id

    @api.constrains('company_id')
    def _check_company_id(self):
        for rec in self:
            for line in rec.line_ids:
                if line.account_id.company_id.id != rec.company_id.id:
                    raise UserError(
                        _('Company must be the same for all account move '
                          'lines.'))
            move_line = self.env['account.move.line'].search(
                [('move_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if move_line:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Journal Entry is assigned to Move Line '
                      '%s of Move %s.' % (move_line.name,
                                          move_line.move_id.name)))
            invoice = self.env['account.invoice'].search(
                [('move_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if invoice:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Journal Entry is assigned to Invoice '
                      '%s.' % invoice.name))

    @api.multi
    @api.constrains('journal_id', 'company_id')
    def _check_company_journal_id(self):
        for move in self.sudo():
            if move.company_id and move.journal_id and \
                    move.company_id != move.journal_id.company_id:
                raise ValidationError(_('The Company in the Move and in '
                                        'Journal must be the same.'))
        return True

    @api.multi
    @api.constrains('line_ids', 'company_id')
    def _check_company_line_ids(self):
        for move in self.sudo():
            for line in move.line_ids:
                if move.company_id and \
                        move.company_id != line.company_id:
                    raise ValidationError(
                        _('The Company in the Move and in Journal Item %s '
                          'must be the same.') % line.name)
        return True

    @api.multi
    @api.constrains('dummy_account_id', 'company_id')
    def _check_company_dummy_account_id(self):
        for move in self.sudo():
            if move.company_id and move.dummy_account_id and \
                    move.company_id != move.dummy_account_id.company_id:
                raise ValidationError(_('The Company in the Move and in '
                                        'Account must be the same.'))
        return True


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        res = []
        names = super(AccountMoveLine, self).name_get()
        multicompany_group = self.env.ref('base.group_multi_company')
        if multicompany_group not in self.env.user.groups_id:
            return names
        for name in names:
            rec = self.browse(name[0])
            name = "%s [%s]" % (name[1], name.company_id.name)
            res += [(rec.id, name)]
        return res

    @api.onchange('company_id')
    def onchange_company_id(self):
        self.account_id = False
        self.move_id = False
        self.statement_id = False
        self.matched_debit_ids = False
        self.matched_credit_ids = False
        self.journal_id = False
        self.tax_ids = False
        self.tax_line_id = False
        self.invoice_id = False

    def auto_reconcile_lines(self):
        return super(AccountMoveLine, self.with_context(
            check_move_validity=False)).auto_reconcile_lines()

    @api.model
    def _add_company_name_to_rows(self, rows):
        for row in rows:
            if 'account_code' in row:
                row['account_code'] = '%s (%s)' % (
                    row['account_code'], self.env['account.account'].browse(
                        row['account_id']).company_id.name)
        return True

    @api.model
    def get_data_for_manual_reconciliation(self, res_type, res_ids=None,
                                           account_type=None):
        # Code is the same as original method, but we use it to compute for
        # the child_companies
        prev_rows = super(
            AccountMoveLine, self).get_data_for_manual_reconciliation(
            res_type, res_ids, account_type)
        self._add_company_name_to_rows(prev_rows)
        child_companies = self.env.user.company_id.child_ids
        if not child_companies:
            return prev_rows

        if res_ids is not None and len(res_ids) == 0:
            return []
        res_ids = res_ids and tuple(res_ids)

        assert res_type in ('partner', 'account')
        assert account_type in ('payable', 'receivable', None)
        is_partner = res_type == 'partner'
        res_alias = is_partner and 'p' or 'a'
        child_company_ids = child_companies and tuple(child_companies.ids)

        query = ("""
            SELECT {0} account_id, account_name, account_code, max_date,
                   to_char(last_time_entries_checked, 'YYYY-MM-DD')
                   AS last_time_entries_checked
            FROM (
                    SELECT {1}
                        {res_alias}.last_time_entries_checked
                        AS last_time_entries_checked,
                        a.id AS account_id,
                        a.name AS account_name,
                        a.code AS account_code,
                        MAX(l.write_date) AS max_date
                    FROM
                        account_move_line l
                        RIGHT JOIN account_account a
                        ON (a.id = l.account_id)
                        RIGHT JOIN account_account_type at
                        ON (at.id = a.user_type_id)
                        {2}
                    WHERE
                        a.reconcile IS TRUE
                        AND l.full_reconcile_id is NULL
                        {3}
                        {4}
                        {5}
                        AND l.company_id in {6}
                        AND EXISTS (
                            SELECT NULL
                            FROM account_move_line l
                            WHERE l.account_id = a.id
                            {7}
                            AND l.amount_residual > 0
                        )
                        AND EXISTS (
                            SELECT NULL
                            FROM account_move_line l
                            WHERE l.account_id = a.id
                            {7}
                            AND l.amount_residual < 0
                        )
                    GROUP BY {8} a.id, a.name, a.code,
                    {res_alias}.last_time_entries_checked
                    ORDER BY {res_alias}.last_time_entries_checked
                ) as s
            WHERE (last_time_entries_checked IS NULL
            OR max_date > last_time_entries_checked)
        """.format(
            is_partner and 'partner_id, partner_name,' or ' ',
            is_partner and 'p.id AS partner_id, p.name '
                           'AS partner_name,' or ' ',
            is_partner and 'RIGHT JOIN res_partner p '
                           'ON (l.partner_id = p.id)' or ' ',
            is_partner and ' ' or "AND at.type <> 'payable' "
                                  "AND at.type <> 'receivable'",
            account_type and "AND at.type = %(account_type)s" or '',
            res_ids and 'AND ' + res_alias + '.id in %(res_ids)s' or '',
            child_company_ids and '%(child_company_ids)s' or '',
            is_partner and 'AND l.partner_id = p.id' or ' ',
            is_partner and 'l.partner_id, p.id,' or ' ',
            res_alias=res_alias
        ))
        self.env.cr.execute(query, locals())

        # Apply ir_rules by filtering out
        rows = self.env.cr.dictfetchall()
        ids = [x['account_id'] for x in rows]
        allowed_ids = set(self.env['account.account'].browse(ids).ids)
        rows = [row for row in rows if row['account_id'] in allowed_ids]
        if is_partner:
            ids = [x['partner_id'] for x in rows]
            allowed_ids = set(self.env['res.partner'].browse(ids).ids)
            rows = [row for row in rows if row['partner_id'] in allowed_ids]

        # Fetch other data
        for row in rows:
            account = self.env['account.account'].browse(row['account_id'])
            row['currency_id'] = account.currency_id.id or \
                account.company_id.currency_id.id
            partner_id = is_partner and row['partner_id'] or None
            row['reconciliation_proposition'] = \
                self.get_reconciliation_proposition(account.id, partner_id)
        self._add_company_name_to_rows(rows)
        total_rows = rows + prev_rows
        return total_rows

    @api.multi
    @api.constrains('account_id', 'company_id')
    def _check_company_account_id(self):
        for move_line in self.sudo():
            if move_line.company_id and move_line.account_id and \
                    move_line.company_id != move_line.account_id.company_id:
                raise ValidationError(_('The Company in the Move Line and in '
                                        'Account must be the same.'))
        return True

    @api.multi
    @api.constrains('move_id', 'company_id')
    def _check_company_move_id(self):
        for move_line in self.sudo():
            if move_line.company_id and move_line.move_id and \
                    move_line.company_id != move_line.move_id.company_id:
                raise ValidationError(_('The Company in the Move Line and in '
                                        'Journal Entry must be the same.'))
        return True

    @api.multi
    @api.constrains('statement_id', 'company_id')
    def _check_company_statement_id(self):
        for move_line in self.sudo():
            if move_line.company_id and move_line.statement_id and \
                    move_line.company_id != move_line.statement_id.company_id:
                raise ValidationError(_('The Company in the Move Line and in '
                                        'Statement must be the same.'))
        return True

    @api.multi
    @api.constrains('matched_debit_ids', 'company_id')
    def _check_company_matched_debit_ids(self):
        for move_line in self.sudo():
            for account in move_line.matched_debit_ids:
                if move_line.company_id and \
                        move_line.company_id != account.company_id:
                    raise ValidationError(
                        _('The Company in the Move Line and in  '
                          'must be the same.'))
        return True

    @api.multi
    @api.constrains('matched_credit_ids', 'company_id')
    def _check_company_matched_credit_ids(self):
        for move_line in self.sudo():
            for matched_credit in move_line.matched_credit_ids:
                if move_line.company_id and move_line.company_id != \
                        matched_credit.company_id:
                    raise ValidationError(
                        _('The Company in the Move Line and in Journal %s'
                          'must be the same.') % matched_credit.name)
        return True

    @api.multi
    @api.constrains('journal_id', 'company_id')
    def _check_company_journal_id(self):
        for move_line in self.sudo():
            if move_line.company_id and move_line.journal_id and \
                    move_line.company_id != move_line.journal_id.company_id:
                raise ValidationError(_('The Company in the Move Line and in '
                                        'Journal must be the same.'))
        return True

    @api.multi
    @api.constrains('tax_ids', 'company_id')
    def _check_company_tax_ids(self):
        for move_line in self.sudo():
            for tax in move_line.tax_ids:
                if move_line.company_id and \
                        move_line.company_id != tax.company_id:
                    raise ValidationError(
                        _('The Company in the Move Line and in Tax %s'
                          'must be the same.') % tax.name)
        return True

    @api.multi
    @api.constrains('tax_line_id', 'company_id')
    def _check_company_tax_line_id(self):
        for move_line in self.sudo():
            if move_line.company_id and move_line.tax_line_id and \
                    move_line.company_id != move_line.tax_line_id.company_id:
                raise ValidationError(_('The Company in the Move Line and in '
                                        'Originator tax must be the same.'))
        return True

    @api.multi
    @api.constrains('invoice_id', 'company_id')
    def _check_company_invoice_id(self):
        for move_line in self.sudo():
            if move_line.company_id and move_line.invoice_id and \
                    move_line.company_id != move_line.invoice_id.company_id:
                raise ValidationError(_('The Company in the Move Line and in '
                                        'Partner must be the same.'))
        return True

    @api.constrains('company_id')
    def _check_company_id(self):
        for rec in self:
            move = self.env['account.move'].search(
                [('line_ids', 'in', [rec.id]),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if move:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Journal Item is assigned to Move '
                      '%s.' % move.name))
            invoice = self.env['account.invoice'].search(
                [('payment_move_line_ids', 'in', [rec.id]),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if invoice:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Payment Move Line is assigned to Invoice '
                      '%s.' % invoice.name))
            partial_reconcile = self.env['account.partial.reconcile'].search(
                [('debit_move_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if partial_reconcile:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'line is assigned to Partial Reconcile '
                      '%s.' % partial_reconcile.name))
            partial_reconcile = self.env['account.partial.reconcile'].search(
                [('credit_move_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if partial_reconcile:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'line is assigned to Partial Reconcile '
                      '%s.' % partial_reconcile.name))
            bank_statement = self.env['account.bank.statement'].search(
                [('move_line_ids', 'in', [rec.id]),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if bank_statement:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'line is assigned to Bank Statement '
                      '%s.' % bank_statement.name))


class AccountMoveLineReconcile(models.TransientModel):
    _inherit = 'account.move.line.reconcile'

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        res = []
        names = super(AccountMoveLineReconcile, self).name_get()
        multicompany_group = self.env.ref('base.group_multi_company')
        if multicompany_group not in self.env.user.groups_id:
            return names
        for name in names:
            rec = self.browse(name[0])
            name = '%s [%s]' % (name[1], name.company_id.name) if \
                name.company_id else name[1]
            res += [(rec.id, name)]
        return res
