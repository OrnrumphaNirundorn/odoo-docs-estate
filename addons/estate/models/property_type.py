from odoo import models, fields

class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Property Type"

    sequence = fields.Integer(default=10)
    _order = "sequence, name"

    
    
    name = fields.Char(required=True)

    _check_name_unique_sql = models.Constraint(
        'UNIQUE(name)',
        'The property type name must be unique.'
    )

    property_ids = fields.One2many(
        "estate.property",
        "property_type_id",
        string="Properties"
    )