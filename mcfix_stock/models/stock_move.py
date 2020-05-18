from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'
    _check_company_auto = True

    warehouse_id = fields.Many2one(check_company=True)
    partner_id = fields.Many2one(check_company=True)

    @api.depends('company_id')
    def name_get(self):
        names = super(StockMove, self).name_get()
        res = self.add_company_suffix(names)
        return res

    @api.model
    def create(self, vals):
        # If we did not get the company, try to derive from the picking
        if vals.get('picking_id') and not vals.get('company_id'):
            picking = self.env['stock.picking'].browse(vals['picking_id'])
            vals['company_id'] = \
                picking.picking_type_id.warehouse_id.company_id.id

        # If we did not get the company or picking, try to derive
        # from either the source or destination location.
        if not vals.get('picking_id') and not vals.get('company_id'):
            location = self.env['stock.location'].browse(vals['location_id'])
            location_dest = self.env['stock.location'].browse(
                vals['location_dest_id'])
            company = location.company_id or location_dest.company_id
            if company:
                vals['company_id'] = company.id
        return super(StockMove, self).create(vals)

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if not self.origin_returned_move_id:
            if not self.picking_id.check_company(self.company_id):
                self.picking_id.company_id = self.company_id
            if not self.restrict_partner_id.check_company(self.company_id):
                self.restrict_partner_id = False
            if not self.location_id.check_company(self.company_id):
                self.location_id = self.picking_id.location_id
            if not self.partner_id.check_company(self.company_id):
                self.partner_id = self.picking_id.partner_id
            if not self.location_dest_id.check_company(self.company_id):
                self.location_dest_id = self.picking_id.location_dest_id
            if not self.inventory_id.check_company(self.company_id):
                self.inventory_id = False
            if not self.rule_id.check_company(self.company_id):
                self.rule_id = False
    #         if not self.move_orig_ids.check_company(self.company_id):
    #             self.move_orig_ids = self.env['stock.move'].search(
    #                 [('move_dest_ids', 'in', [self.id]),
    #                  ('company_id', '=', False),
    #                  ('company_id', '=', self.company_id.id)])
    #         if not self.move_dest_ids.check_company(self.company_id):
    #             self.move_dest_ids = self.env['stock.move'].search(
    #                 [('move_orig_ids', 'in', [self.id]),
    #                  ('company_id', '=', False),
    #                  ('company_id', '=', self.company_id.id)])
    #
    #
    # @api.constrains('company_id', 'move_orig_ids')
    # def _check_company_id_move_orig_ids(self):
    #     for rec in self.sudo():
    #         for line in rec.move_orig_ids:
    #             if not line.check_company(rec.company_id):
    #                 raise ValidationError(
    #                     _('The Company in the Stock Move and in '
    #                       'Stock Move (%s) must be the same.'
    #                       ) % line.name_get()[0][1])
    #
    # @api.constrains('company_id', 'move_dest_ids')
    # def _check_company_id_move_dest_ids(self):
    #     for rec in self.sudo():
    #         for line in rec.move_dest_ids:
    #             if not line.check_company(rec.company_id):
    #                 raise ValidationError(
    #                     _('The Company in the Stock Move and in '
    #                       'Stock Move (%s) must be the same.'
    #                       ) % line.name_get()[0][1])

    @api.constrains('company_id')
    def _check_company_id_out_model(self):
        self._check_company_id_base_model()

    def _check_company_id_fields(self):
        res = super()._check_company_id_fields()
        res += [
            self.move_orig_ids, self.move_dest_ids,
            self.returned_move_ids, self.move_line_ids,
            self.move_line_nosuggest_ids, self.scrap_ids,
        ]
        return res


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    # company_id = fields.Many2one(
    #     'res.company', compute='_compute_company_id', string='Company',
    #     readonly=True, store=True)
    #
    # @api.depends('move_id')
    # def _compute_company_id(self):
    #     for line in self:
    #         if line.move_id:
    #             line.company_id = line.move_id.company_id
    #         else:
    #             line.company_id = line.env.user.company_id
