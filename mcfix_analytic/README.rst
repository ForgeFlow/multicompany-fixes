.. image:: https://img.shields.io/badge/license-LGPL--3-blue.png
   :target: https://www.gnu.org/licenses/lgpl
   :alt: License: LGPL-3

==============
Mcfix Analytic
==============

This module is part of a set of modules that are intended to make sure that
the multi-company functionality is consistent.

* Adds the company as a suffix to the analytic account when the user
  belongs to the multi-company group.

* When the user creates an analytic account, by default she can only select
  partners that belong to the same company, or have no company associated.

* Link between partner and analytic account does require to be consistent
  company-wise. It is understood that for historical reasons a partner
  now assigned to a certain company might have had contracts with other
  companies in the the past, and these contracts need to remain.


Usage
=====

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/133/13.0


Credits
=======

Contributors
------------

* Enric Tobella <etobella@creublanca.es>
* Jordi Ballester <jordi.ballester@forgeflow.com>
* Miquel Raïch <miquel.raich@forgeflow.com>

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
