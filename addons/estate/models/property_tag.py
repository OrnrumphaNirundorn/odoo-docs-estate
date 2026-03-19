from odoo import models, fields

class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Real Estate Property Tag"

    name = fields.Char(required=True)

    _check_name_unique_sql = models.Constraint(
        'UNIQUE(name)',
        'The tag name must be unique.'
    )