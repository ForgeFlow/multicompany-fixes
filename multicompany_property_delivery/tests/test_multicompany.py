# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.addons.multicompany_property_account.tests import test_multicompany


class TestMulticompanyProperty(test_multicompany.TestMulticompanyProperty):
    def test_partner(self):
        super().test_partner()
        carrier = self.env['delivery.carrier'].search([], limit=1)
        self.assertTrue(carrier)
        prop = self.partner.property_ids.filtered(
            lambda r: r.company_id == self.company_1
        )
        prop.write({'property_delivery_carrier_id': carrier.id, })
        self.assertEqual(
            self.partner.with_context(
                force_company=self.company_1.id
            ).property_delivery_carrier_id,
            carrier
        )
        self.partner.property_ids._compute_property_fields()
        self.assertEqual(
            self.partner.with_context(
                force_company=self.company_1.id
            ).property_delivery_carrier_id,
            prop.property_delivery_carrier_id
        )
