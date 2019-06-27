# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class Warehouse(models.Model):
    _inherit = 'stock.warehouse'

    company_id = fields.Many2one(readonly=False)
