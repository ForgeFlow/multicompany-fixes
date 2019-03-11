# Copyright 2018 Creu Blanca
# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class PosSession(models.Model):
    _inherit = 'pos.session'

    company_id = fields.Many2one('res.company', string='Company',
                                 related='config_id.company_id', store=True,
                                 readonly=True)

    @api.model
    def create(self, values):
        # Here we have to redefine the logic to obtain pos_config.journal_ids
        # because in the core odoo it does not take into account the company.
        config_id = values.get('config_id') or \
            self.env.context.get('default_config_id')
        if not config_id:
            raise UserError(
                _("You should assign a Point of Sale to your session."))
        pos_config = self.env['pos.config'].browse(config_id)
        ctx = dict(self.env.context, company_id=pos_config.company_id.id)
        if not pos_config.journal_ids:
            journal_model = self.env['account.journal']
            journals = journal_model.with_context(ctx).search(
                [('journal_user', '=', True), ('type', '=', 'cash'),
                 ('company_id', '=', pos_config.company_id.id)])
            if not journals:
                journals = journal_model.with_context(ctx).search(
                    [('type', '=', 'cash'),
                     ('company_id', '=', pos_config.company_id.id)])
                if not journals:
                    journals = journal_model.with_context(ctx).search(
                        [('journal_user', '=', True),
                         ('company_id', '=', pos_config.company_id.id)])
            journals.sudo().write({'journal_user': True})
            pos_config.sudo().write({'journal_ids': [(6, 0, journals.ids)]})

        return super(PosSession, self).create(values)

    @api.multi
    @api.constrains('config_id')
    def _check_company_id_config_id(self):
        for rec in self.sudo():
            for config in rec.config_id:
                if not config.check_company(rec.company_id):
                    raise ValidationError(
                        _('The Company in the POS Session and in '
                          'POS Config (%s) must be the same.'
                          ) % config.name_get()[0][1])
