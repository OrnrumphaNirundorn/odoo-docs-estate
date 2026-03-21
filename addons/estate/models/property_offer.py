from odoo import models, fields, api
from datetime import timedelta
from odoo.exceptions import UserError

class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Property Offer"
    _order = "price desc"

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

    property_type_id = fields.Many2one(
        'estate.property.type',
        related='property_id.property_type_id',
        store=True,
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
            existing = record.property_id.offer_ids.filtered(
                lambda o: o.status == 'accepted' and o.id != record.id
            )

            if existing:
                raise UserError("Only one offer can be accepted.")

            record.status = 'accepted'

            record.property_id.selling_price = record.price
            record.property_id.buyer_id = record.partner_id
            record.property_id.state = 'offer_accepted'

            # return {'type': 'ir.actions.client', 'tag': 'reload'}

    def action_refuse(self):
        for record in self:
            record.status = 'refused'

            # return {'type': 'ir.actions.client', 'tag': 'reload'}

    _check_price_sql = models.Constraint(
        'CHECK(price > 0)',
        'The offer price must be strictly positive.'
    )
    
    # @api.model
    # def create(self, vals):
    #     offer = super().create(vals)

    #     if offer.property_id:
    #         offer.property_id.state = 'offer_received'
        
    #     return offer
    
    @api.model
    def create(self, vals_list):
        for vals in vals_list:
            property_id = self.env['estate.property'].browse(vals.get('property_id'))

            if property_id.offer_ids:
                max_price = max(property_id.offer_ids.mapped('price'))
                if vals.get('price') <= max_price:
                    raise UserError("Offer must be higher than existing offers.")

        offers = super().create(vals_list)

        for offer in offers:
            if offer.property_id:
                offer.property_id.state = 'offer_received'

        return offers