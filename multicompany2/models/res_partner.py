from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    property_account_payable_id = fields.Many2one(readonly=True)

    property2_ids = fields.One2many(
        comodel_name='res.partner.property2',
        compute='_get_properties',
        inverse='_set_properties',
        string='Properties'
    )

    @api.multi
    def _set_properties(self):
        for record in self:
            for property in record.property2_ids:
                property.set_properties()

    @api.multi
    def _get_properties(self):
        for record in self:
            property_obj = self.env['res.partner.property2']
            values = []
            companies = self.env['res.company'].search([])
            for company in companies:
                val = property_obj.create({
                    'partner_id': record.id,
                    'company_id': company.id
                })
                values.append(val.id)
            record.property2_ids = values


class ResPartnerProperties(models.TransientModel):
    _name = 'res.partner.property2'
    _inherit = 'multicompany.property.abstract'

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partner'
    )

    property_account_payable_id = fields.Many2one(
        comodel_name='account.account',
        string="Account Payable",
        domain="[('internal_type', '=', 'payable'), ('deprecated', '=', False)]",
        help="This account will be used instead of the default one as the payable account for the current partner",
        compute='get_properties',
        store=False,
        readonly=False
    )

    def get_property_value(self, field, object):
        prop_obj = self.env['ir.property'].with_context(force_company=self.company_id.id)
        value = prop_obj.get(field, object._name, (object._name+',%s') % object.id)
        if value:
            return value
        return prop_obj.get(field, object._name)

    @api.one
    def get_properties(self):
        self.property_account_payable_id = self.get_property_value('property_account_payable_id', self.partner_id)

    @api.one
    def set_properties(self):
        self.env['ir.property'].with_context(force_company=self.company_id.id).set_multi(
            'property_account_payable_id', 'res.partner', {self.partner_id.id: self.property_account_payable_id.id})
