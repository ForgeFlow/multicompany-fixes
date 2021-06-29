from odoo import api, models


class SupplierInfo(models.Model):
    _inherit = "product.supplierinfo"
    _check_company_auto = True

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if "company_id" not in vals:
                if "name" in vals:
                    partner = self.env["res.partner"].browse([vals["name"]])
                    vals["company_id"] = partner.company_id.id
                else:
                    vals["company_id"] = False
        return super(SupplierInfo, self).create(vals_list)
