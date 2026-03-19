from odoo import models, fields

class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Property Type"

    name = fields.Char(required=True)

    _check_name_unique_sql = models.Constraint(
        'UNIQUE(name)',
        'The property type name must be unique.'
    )