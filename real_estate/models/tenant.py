from odoo import models, fields, api

class Tenant(models.Model):
    _name = 'real_estate.tenant'
    _description = 'Real Estate Tenant'
    _order = 'name asc'
    
    # === CORE FIELDS ===
    name = fields.Char(string='Tenant Name', required=True, index=True)
    email = fields.Char(string='Email', required=True, index=True)
    phone = fields.Char(string='Phone Number')
    mobile = fields.Char(string='Mobile Number')
    city = fields.Char(string='City')
    date_joined = fields.Date(string='Date Joined', default=fields.Date.today, readonly=True)
    date_of_birth = fields.Date(string='Date of Birth')
    notes = fields.Text(string='Notes')
    active = fields.Boolean(string='Active', default=True)
    crm_lead_id = fields.Many2one('crm.lead', string='CRM Lead', ondelete='set null', index=True) 

    def set_name_notes(self):
        """Set the name and notes of the tenant"""
        for record in self:
            record.write({'notes': 'This is a note about ' + record.name + '.'})
    def get_lead_name(self):
        """Get the name of the associated CRM lead"""
        for record in self:
            if record.crm_lead_id:
                lead_name = record.crm_lead_id.name
                record.write({'notes': 'Associated CRM Lead: ' + lead_name})
            else:
                record.write({'notes': 'No associated CRM Lead.'})        
