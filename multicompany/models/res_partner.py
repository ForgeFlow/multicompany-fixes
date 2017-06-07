from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    property_ids = fields.One2many(
        comodel_name='res.partner.property',
        inverse_name='partner_id',
        string='Properties'
    )


class ResPartnerProperties(models.Model):
    _name = 'res.partner.property'
    _inherit = 'multicompany.property.abstract'

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partner'
    )

    _sql_constraints = [('company_partner_unique',
                         'UNIQUE(company_id, partner_id)',
                         "The company must be unique"),
                        ]

    @api.model
    def create(self, vals):
        self.set_properties(self.env['res.partner'].browse(vals.get('partner_id', False)), vals,
                            self.env['ir.property'].with_context(force_company=self.company_id.id))
        return super(ResPartnerProperties, self).create(vals)

    @api.multi
    def write(self, vals):
        for record in self:
            record.set_properties(record.partner_id, vals,
                                  self.env['ir.property'].with_context(force_company=record.company_id.id))
        return super(ResPartnerProperties, self).write(vals)

    @api.model
    def set_properties(self, object, vals, properties=False):
        return
