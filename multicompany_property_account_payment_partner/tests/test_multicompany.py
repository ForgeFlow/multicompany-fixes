# Copyright 2017 Creu Blanca
# Copyright 2017 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.addons.multicompany_property_account.tests import test_multicompany


class TestMulticompanyProperty(test_multicompany.TestMulticompanyProperty):
    def test_partner(self):
        super().test_partner()
