from odoo import models, fields, api
from datetime import timedelta
from odoo.exceptions import UserError

class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Property Offer"

    price = fields.Float()
    status = fields.Selection(
        [
            ('accepted', 'Accepted'),
            ('refused', 'Refused'),
        ], 
        copy=False
    )

    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        required=True
    )

    property_id = fields.Many2one(
        'estate.property',
        string='Property',
        required=True
    )

    validity = fields.Integer(
        default=7,
    )

    date_deadline = fields.Date(
        compute='_compute_date_deadline',
        inverse='_inverse_date_deadline',
    )

    @api.depends("create_date", "validity")
    def _compute_date_deadline(self):
        for record in self:
            if record.create_date:
                record.date_deadline = record.create_date.date() + timedelta(days=record.validity)
            else:
                record.date_deadline = fields.Date.today() + timedelta(days=record.validity)
    
    def _inverse_date_deadline(self):
        for record in self:
            if record.create_date and record.date_deadline:
                record.validity = (record.date_deadline - record.create_date.date()).days

    def action_accept(self):
        for record in self:
            existing = record.property_id.offer_ids.filtered(lambda o: o.status == 'accepted')
            if existing:
                raise UserError("Only one offer can be accepted.")

            record.status = 'accepted'

            record.property_id.selling_price = record.price
            record.property_id.buyer_id = record.partner_id
            record.property_id.state = 'offer_accepted'

    def action_refuse(self):
        for record in self:
            record.status = 'refused'

    _check_price_sql = models.Constraint(
        'CHECK(price > 0)',
        'The offer price must be strictly positive.'
    )