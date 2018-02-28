from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    company_id = fields.Many2one(
        readonly=False, states={'posted': [('readonly', True)]}, related=False)

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        names = super(AccountMove, self).name_get()
        res = self.add_company_suffix(names)
        return res

    @api.model
    def create(self, vals):
        if self._context.get('company_id'):
            vals['company_id'] = self._context.get('company_id')
        move = super(AccountMove, self).create(vals)
        return move

    @api.multi
    @api.onchange('company_id')
    def _onchange_company_id(self):
        default = self.env.context['default_journal_type']
        for record in self:
            record.journal_id = self.env['account.journal'].search([
                ('company_id', '=', record.company_id.id),
                ('type', '=', default)
            ], limit=1).id
            record.line_ids = False

    @api.multi
    @api.constrains('company_id', 'partner_id')
    def _check_company_id_partner_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.partner_id.company_id and\
                    rec.company_id != rec.partner_id.company_id:
                raise ValidationError(
                    _('The Company in the Account Move and in '
                      'Res Partner must be the same.'))

    @api.multi
    @api.constrains('company_id', 'tax_cash_basis_rec_id')
    def _check_company_id_tax_cash_basis_rec_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.tax_cash_basis_rec_id.company_id and\
                    rec.company_id != rec.tax_cash_basis_rec_id.company_id:
                raise ValidationError(
                    _('The Company in the Account Move and in '
                      'Account Partial Reconcile must be the same.'))

    @api.multi
    @api.constrains('company_id', 'dummy_account_id')
    def _check_company_id_dummy_account_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.dummy_account_id.company_id and\
                    rec.company_id != rec.dummy_account_id.company_id:
                raise ValidationError(
                    _('The Company in the Account Move and in '
                      'Account Account must be the same.'))

    @api.multi
    @api.constrains('company_id', 'journal_id')
    def _check_company_id_journal_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.journal_id.company_id and\
                    rec.company_id != rec.journal_id.company_id:
                raise ValidationError(
                    _('The Company in the Account Move and in '
                      'Account Journal must be the same.'))

    @api.constrains('company_id')
    def _check_company_id_out_model(self):
        if not self.env.context.get('bypass_company_validation', False):
            for rec in self:
                if not rec.company_id:
                    continue
                field = self.env['account.invoice'].search(
                    [('move_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Account Move is assigned to Account Invoice '
                          '(%s).' % field.name_get()[0][1]))
                field = self.env['account.move.line'].search(
                    [('move_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Account Move is assigned to Account Move Line '
                          '(%s).' % field.name_get()[0][1]))


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        names = super(AccountMoveLine, self).name_get()
        res = self.add_company_suffix(names)
        return res

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
        # pylint: disable=E8103
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
    def prepare_move_lines_for_reconciliation_widget(
            self, target_currency=False, target_date=False):
        ret = super(AccountMoveLine, self).\
            prepare_move_lines_for_reconciliation_widget(
            target_currency=target_currency, target_date=target_date)
        for ret_line in ret:
            for line in self:
                if ret_line['id'] == line.id:
                    ret_line['company_id'] = line.company_id.id
        return ret

    @api.multi
    @api.constrains('company_id', 'tax_line_id')
    def _check_company_id_tax_line_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.tax_line_id.company_id and\
                    rec.company_id != rec.tax_line_id.company_id:
                raise ValidationError(
                    _('The Company in the Account Move Line and in '
                      'Account Tax must be the same.'))

    @api.multi
    @api.constrains('company_id', 'product_id')
    def _check_company_id_product_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.product_id.company_id and\
                    rec.company_id != rec.product_id.company_id:
                raise ValidationError(
                    _('The Company in the Account Move Line and in '
                      'Product Product must be the same.'))

    @api.multi
    @api.constrains('company_id', 'statement_line_id')
    def _check_company_id_statement_line_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.statement_line_id.company_id and\
                    rec.company_id != rec.statement_line_id.company_id:
                raise ValidationError(
                    _('The Company in the Account Move Line and in '
                      'Account Bank Statement Line must be the same.'))

    @api.multi
    @api.constrains('company_id', 'tax_ids')
    def _check_company_id_tax_ids(self):
        for rec in self.sudo():
            for line in rec.tax_ids:
                if rec.company_id and line.company_id and\
                        rec.company_id != line.company_id:
                    raise ValidationError(
                        _('The Company in the Account Move Line and in '
                          'Account Tax (%s) must be the same'
                          '.') % line.name_get()[0][1])

    @api.multi
    @api.constrains('company_id', 'payment_id')
    def _check_company_id_payment_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.payment_id.company_id and\
                    rec.company_id != rec.payment_id.company_id:
                raise ValidationError(
                    _('The Company in the Account Move Line and in '
                      'Account Payment must be the same.'))

    @api.multi
    @api.constrains('company_id', 'invoice_id')
    def _check_company_id_invoice_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.invoice_id.company_id and\
                    rec.company_id != rec.invoice_id.company_id:
                raise ValidationError(
                    _('The Company in the Account Move Line and in '
                      'Account Invoice must be the same.'))

    @api.multi
    @api.constrains('company_id', 'partner_id')
    def _check_company_id_partner_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.partner_id.company_id and\
                    rec.company_id != rec.partner_id.company_id:
                raise ValidationError(
                    _('The Company in the Account Move Line and in '
                      'Res Partner must be the same.'))

    @api.multi
    @api.constrains('company_id', 'move_id')
    def _check_company_id_move_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.move_id.company_id and\
                    rec.company_id != rec.move_id.company_id:
                raise ValidationError(
                    _('The Company in the Account Move Line and in '
                      'Account Move must be the same.'))

    @api.multi
    @api.constrains('company_id', 'account_id')
    def _check_company_id_account_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.account_id.company_id and\
                    rec.company_id != rec.account_id.company_id:
                raise ValidationError(
                    _('The Company in the Account Move Line and in '
                      'Account Account must be the same.'))

    @api.multi
    @api.constrains('company_id', 'statement_id')
    def _check_company_id_statement_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.statement_id.company_id and\
                    rec.company_id != rec.statement_id.company_id:
                raise ValidationError(
                    _('The Company in the Account Move Line and in '
                      'Account Bank Statement must be the same.'))

    @api.multi
    @api.constrains('company_id', 'analytic_account_id')
    def _check_company_id_analytic_account_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.analytic_account_id.company_id and\
                    rec.company_id != rec.analytic_account_id.company_id:
                raise ValidationError(
                    _('The Company in the Account Move Line and in '
                      'Account Analytic Account must be the same.'))

    @api.multi
    @api.constrains('company_id', 'journal_id')
    def _check_company_id_journal_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.journal_id.company_id and\
                    rec.company_id != rec.journal_id.company_id:
                raise ValidationError(
                    _('The Company in the Account Move Line and in '
                      'Account Journal must be the same.'))

    @api.constrains('company_id')
    def _check_company_id_out_model(self):
        if not self.env.context.get('bypass_company_validation', False):
            for rec in self:
                if not rec.company_id:
                    continue
                field = self.env['account.invoice'].search(
                    [('payment_move_line_ids', 'in', [rec.id]),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Account Move Line is assigned to Account Invoice '
                          '(%s).' % field.name_get()[0][1]))
                field = self.env['account.analytic.line'].search(
                    [('move_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Account Move Line is assigned to '
                          'Account Analytic Line (%s)'
                          '.' % field.name_get()[0][1]))
                field = self.env['account.partial.reconcile'].search(
                    [('credit_move_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Account Move Line is assigned to '
                          'Account Partial Reconcile (%s)'
                          '.' % field.name_get()[0][1]))
                field = self.env['account.partial.reconcile'].search(
                    [('debit_move_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Account Move Line is assigned to '
                          'Account Partial Reconcile (%s)'
                          '.' % field.name_get()[0][1]))
