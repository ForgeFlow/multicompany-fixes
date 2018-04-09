.. image:: https://img.shields.io/badge/license-LGPL--3-blue.png
   :target: https://www.gnu.org/licenses/lgpl
   :alt: License: LGPL-3

===================
Mcfix Point of Sale
===================

This module is part of a set of modules that are intended to make sure that
the multi-company functionality is consistent.

* You cannot modify the company of company-dependent objects that have been
  created out of a POS Order, and refer to it: invoices, pickings, moves,..

* You cannot change the company of taxes, product, stock location,
  pricelists, fiscal positions, if these elements are already referenced
  in POS orders that are assigned to another company.

* You cannot change the company of pricelists, fiscal positions,
  sequences if these elements are already referenced in POS configs
  that are assigned to another company.

* You cannot change the company of a POS Session once it has created a bank
  statement.




* You cannot change the company of an invoice if it originated from a
  POS order that belongs to another company.

* You cannot change the company of a picking if it originated from a POS order
  that belongs to another company.

*



Usage
=====

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/133/11.0


Credits
=======

Contributors
------------

* Enric Tobella <etobella@creublanca.es>
* Jordi Ballester <jordi.ballester@eficent.com>
* Miquel Raïch <miquel.raich@eficent.com>

Do not contact contributors directly about support or help with technical issues.


Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
