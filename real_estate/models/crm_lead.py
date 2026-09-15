from odoo import models, fields
from odoo.addons.crm.populate.crm_lead import CrmLead


class CrmLead(models.Model):
    _inherit = 'crm.lead'
    _description = 'CRM Lead Extension for Real Estate'
    property_id = fields.Many2one('real_estate.property', string='Property')
    property_type = fields.Selection([
        ('apartment', 'Apartment'),
        ('house', 'House'),
        ('villa', 'Villa'),
        ('commercial', 'Commercial'),
    ], string='Property Type', required=True) 

    def get_name(self):
            """Get the name of the lead"""
            for record in self:
               record.write({'description':record.name })

    def write(self, vals):
        print("vals:", vals.get('name'))
        if vals.get('expected_revenue') > 5000:
            vals['description'] = "This is a high-value lead with expected revenue greater than 5000."
        else:
             raise ValueError("Expected revenue must be greater than 5000.")    
        return super(CrmLead, self).write(vals)              
    

 