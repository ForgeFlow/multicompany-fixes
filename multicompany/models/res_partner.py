from odoo import fields, models, api


class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = ['res.partner', 'multicompany.abstract']

    @api.one
    def get_properties(self):
        self.property = self.env['res.partner.property'].search(
            [('partner_id', '=', self.id), ('company_id', '=', self.current_company_id.id)], limit=1)

    property = fields.Many2one(
        comodel_name='res.partner.property',
        default=get_properties,
        compute='get_properties',
        store=False
    )

    property_ids = fields.One2many(
        comodel_name='res.partner.property',
        inverse_name='partner_id',
        string='Properties'
    )


class ResPartnerProperties(models.Model):
    _name = 'res.partner.property'

    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        required=True
    )

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partner'
    )

    _sql_constraints = [('company_partner_unique',
                         'UNIQUE(company_id, partner_id)',
                         "The company must be unique"),
                        ]
