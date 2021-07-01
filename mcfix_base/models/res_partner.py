# Copyright 2018 Creu Blanca
# Copyright 2018 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo import api, fields, models


class Partner(models.Model):
    _inherit = "res.partner"
    _check_company_auto = True

    parent_id = fields.Many2one(check_company=True)
    child_ids = fields.One2many(check_company=True)
    commercial_partner_id = fields.Many2one(check_company=True)
    commercial_child_ids = fields.One2many(
        "res.partner", inverse_name="commercial_partner_id", check_company=True
    )

    @api.depends("company_id")
    def name_get(self):
        names = super(Partner, self).name_get()
        res = self.add_company_suffix(names)
        return res

    @api.depends("is_company", "name", "parent_id.name", "type", "company_name")
    def _compute_display_name(self):
        # ugly change to ensure that the display name is correctly stored.
        # See https://github.com/odoo/odoo/issues/6276
        for rec in self:
            other = rec.with_context(not_display_company=True)
            super(Partner, other)._compute_display_name()
            rec.display_name = other.display_name

    @api.model_create_multi
    def create(self, vals_list):
        """We need this to ensure that when the partner is created,
        associated to a company, we want to override the default company and
        take instead what the forced company if provided. Otherwise the
        partner of a company was being created inconsistent with the company
        that the partner belongs to."""
        for vals in vals_list:
            if "company_id" in self.env.context and "company_id" not in vals:
                vals["company_id"] = self.env.context["company_id"]
        return super(Partner, self).create(vals_list)

    def _get_top_parent(self):
        parent = self.env["res.partner"]
        for partner in self:
            if partner.parent_id:
                parent |= partner.parent_id._get_top_parent()
            else:
                parent |= self
        return parent

    def _get_all_children(self):
        childs = self
        for partner in self:
            if partner.child_ids:
                childs |= partner.child_ids._get_all_children()
        return childs

    def write(self, vals):
        """The partner hierarchy needs to be consistent company-wise. As a
        consequence, when a user changes the company of one partner, we will
        make sure that the whole partner hierarchy is updated with the new
        company."""
        # https://github.com/odoo/odoo/pull/21219
        company = False
        check_company = False
        if "company_id" in vals and not self.env.context.get("stop_recursion_company"):
            company = vals["company_id"]
            check_company = True
            del vals["company_id"]
        result = super(Partner, self).write(vals)
        if check_company and not self.env.context.get("stop_recursion_company"):
            top_partner = self._get_top_parent()
            partners = top_partner._get_all_children()
            partners = partners.filtered(lambda p: p.company_id)
            partners |= self
            result = result and partners.with_context(
                stop_recursion_company=True
            ).write({"company_id": company})
        return result

    @api.constrains("company_id")
    def _check_company_id_out_model(self):
        self._check_company_id_base_model()
