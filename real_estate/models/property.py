from odoo import models, fields, api
from odoo.exceptions import UserError

class Property(models.Model):
    _name = 'real_estate.property'
    _description = 'Real Estate Property'

    name = fields.Char(string='Property Name', required=True, index=True)
    description = fields.Text(string='Description')
    price = fields.Float(string='Monthly Rent', required=True)    
    bedrooms = fields.Integer(string='Bedrooms', required=True)
    available = fields.Boolean(string='Available', default=True, index=True)
    agent_id = fields.Many2one('res.users', string='Sales Person')
    property_image = fields.Image(string="Property Image", max_width=1920, max_height=1920)
    discount = fields.Float(string='Discount', help='Discount percentage for the property', default=0.0)
    property_type = fields.Selection([
        ('apartment', 'Apartment'),
        ('house', 'House'),
        ('villa', 'Villa'),
        ('commercial', 'Commercial'),], string='Property Type', required=True)
    deposite = fields.Float(string='Deposit', help='Deposit amount for the property', required=True)

    # def mark_as_occupied(self):
    #     for record in self:
    #         record.available = False
    # def mark_as_available(self):
    #     for record in self:
    #         record.available = True      



    def mark_as_occupied(self):
        """Mark property as no longer available"""
        for record in self:
            record.write({'available': False, 'price': record.price + 1000})
    
    def mark_as_available(self):
        """Mark property as available"""
        for record in self:
            record.write({'available': True})
    def update_description(self):
        """Update the description of the property"""
        for record in self:
            record.write({'description': 'Saif.'})
    def increase_deposite(self):
            """Mark property as no longer available"""
            for record in self:
                record.write({'deposite': record.deposite + 1000}) 
    def add_bedrooms(self):
            """Mark property as no longer available"""
            for record in self:
                record.write({'bedrooms': record.bedrooms + 1}) 
    def change_property_type(self):
        """Change the property type"""
        for record in self:
            if record.available:
                record.write({'property_type': 'villa'})                                         
    def get_agent_name(self):
        """Change the property type"""
        for record in self:
                if record.agent_id.name :
                    record.write({'description':"Name of Sales Person: " + record.agent_id.name + '\n' +"Email: "+ record.agent_id.login})           
                else:
                    record.write({'description':'No Agent Assigned'})  





    def write(self, vals):
        if 'available' in vals and vals['available'] == False:
            if 'bedrooms' in vals:
                raise UserError("Cannot Change Bedrooms it is unavailable.")
        return super(Property, self).write(vals)
        