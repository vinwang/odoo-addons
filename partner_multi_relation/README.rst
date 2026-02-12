=========================
Partner Multi Relation
=========================

This module provides generic means to model relations between partners.

Examples include 'is sibling of', 'is friend of', 'has contract X with', or 
'is assistant of'. This allows you to encode knowledge about your partners 
directly in your partner list.

Key Features
============

* **Relation Types**: Define bidirectional relation types with names for both sides
* **Partner Types**: Constrain relations to specific partner types (Person/Company)
* **Partner Categories**: Use tags to further specify partner types for relations
* **Reflexive Relations**: Allow partners to have relations with themselves
* **Symmetric Relations**: Relations where both sides have the same meaning
* **Invalid Relation Handling**: Customizable behavior when relations become invalid
* **Search Functionality**: Search partners by their relations
* **Smart Button**: View relations directly from partner form view

Configuration
=============

1. Go to Contacts > Relations > Partner Relations
2. Create relation types with names for both sides
3. Optionally set partner types and categories for constraints

Usage
=====

* Navigate to Contacts > Relations > Relations to search existing relations
* Use the smart button on partner form view to see their relations
* Create relations between partners from either partner's form view

Requirements
============

* Odoo 19.0
* depends: contacts, sales_team

License
=======

AGPL-3