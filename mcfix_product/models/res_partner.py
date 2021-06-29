from odoo import fields, models


class Partner(models.Model):
    _inherit = "res.partner"
    _check_company_auto = True

    supplier_info_ids = fields.One2many(
        "product.supplierinfo", inverse_name="name", check_company=True
    )
