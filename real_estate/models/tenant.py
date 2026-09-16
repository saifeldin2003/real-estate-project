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
    user_id = fields.Many2one('res.users', string='Related User', index=True)
    crm_lead_id = fields.Many2one('crm.lead', string='CRM Lead', ondelete='set null', index=True) 
    age_category = fields.Selection([
        ('a', 'From 1 to 20'),
        ('b', 'From 21 to 40'),
        ('c', 'From 41 to 60'),], string='Age Group',)
    def set_name_notes(self):
        """Set the name and notes of the tenant"""
        for record in self:
            record.write({'notes': 'This is a note about ' + record.name + '.'})
    def get_lead_name(self):
        """Get the name of the associated CRM lead"""
        for record in self:
            if record.crm_lead_id.website:
                lead_name = record.crm_lead_id.website
                record.write({'notes': 'Associated CRM Lead: ' + lead_name})
            elif record.crm_lead_id.email_from:
                lead_email = record.crm_lead_id.email_from
                record.write({'notes': 'Associated CRM Lead: ' + lead_email})
            else:
                record.write({'notes': 'No associated CRM Lead found.'})
    def calculate_age_category(self):
        """Calculate the age category based on the date of birth"""
        for record in self:
            if record.date_of_birth:
                today = fields.Date.today()
                age = today.year - record.date_of_birth.year - ((today.month, today.day) < (record.date_of_birth.month, record.date_of_birth.day))
                if 1 <= age <= 20:
                    record.age_category = 'a'
                elif 21 <= age <= 40:
                    record.age_category = 'b'
                elif 41 <= age <= 60:
                    record.age_category = 'c'
                else:
                    record.age_category = False
            else:
                record.age_category = False                
                