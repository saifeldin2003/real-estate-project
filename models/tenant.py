from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
class Tenant(models.Model):
    _name = 'real_estate.tenant'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'Real Estate Tenant'
    _order = 'name asc'
    
    # === CORE FIELDS ===
    name = fields.Char(string='Tenant Name', required=True, index=True, tracking = True)
    email = fields.Char(string='Email', required=True, index=True, tracking = True)
    phone = fields.Char(string='Phone Number', tracking = True)
    mobile = fields.Char(string='Mobile Number', tracking = True)
    city = fields.Char(string='City', tracking = True)
    date_joined = fields.Date(string='Date Joined', default=fields.Date.today, readonly=True)
    date_of_birth = fields.Date(string='Date of Birth')
    age = fields.Integer(string='Age', compute='_compute_age')
    notes = fields.Text(string='Notes',)
    active = fields.Boolean(string='Active', default=True)
    user_id = fields.Many2one('res.users', string='Related User', index=True)
    lease_ids = fields.One2many(
            'real_estate.lease',
            'tenant_id',
            string='Leases',
            required=True,
            ondelete='cascade',  # If property deleted, delete lease too
            index=True
        )
    maintenance_ids = fields.One2many(
                'maintenance.request',
                'tenant_id',
                string='Leases',
                required=True,
                ondelete='cascade',  # If property deleted, delete lease too
                index=True
            )
    crm_lead_id = fields.Many2one('crm.lead', string='CRM Lead', ondelete='set null', index=True) 
    age_category = fields.Selection([
        ('a', 'From 1 to 20'),
        ('b', 'From 21 to 40'),
        ('c', 'From 41 to 60'),], string='Age Group',)

    tenant_status = fields.Selection(
    [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
        ('no_lease', 'No Lease'),
    ],
    string='Tenant Status',
    compute='_compute_tenant_status',
    store=True
    )
    lease_count = fields.Integer(compute="_compute_lease_count")
    maintenance_count = fields.Integer(compute="_compute_maintenance_count")

    _sql_constraints = [
        ('email_unique', 'UNIQUE(email)', 'Email must be unique! This email is already registered.'),
    ]
    
    @api.constrains('date_of_birth',)
    def _check_date_of_birth(self):
        """Ensure date of birth is not in the future"""
        if self.date_of_birth > fields.Date.today():
            raise ValidationError("Date of birth cannot be in the future")

    @api.depends('date_of_birth')
    def _compute_age(self):
        today = fields.Date.today()
        for record in self:
            if record.date_of_birth:
                age = today.year - record.date_of_birth.year - ((today.month, today.day) < (record.date_of_birth.month, record.date_of_birth.day))
                record.age = age
            else:
                record.age = 0

    @api.depends('lease_ids')
    def _compute_lease_count(self):
            for record in self:
                record.lease_count = len(record.lease_ids)
    @api.depends('maintenance_ids')
    def _compute_maintenance_count(self):
            for record in self:
                record.maintenance_count = len(record.maintenance_ids)
                print(record.maintenance_count)            

    def action_view_leases (self):
        return {
                'type': 'ir.actions.act_window',
                'name': 'Leases',
                'res_model': 'real_estate.lease',
                'view_mode': 'tree',
                'domain': [
                    ('tenant_id', '=', self.id)
                ],
            }
    def action_view_maintenance (self):
        return {
                'type': 'ir.actions.act_window',
                'name': 'Maintenance Requests',
                'res_model': 'maintenance.request',
                'view_mode': 'tree',
                'domain': [
                    ('tenant_id', '=', self.id)
                ],
            }

    @api.depends('lease_ids.state')
    def _compute_tenant_status(self):
      for tenant in self:
            active_lease = tenant.lease_ids.filtered(
                lambda lease: lease.state == 'active'
            )
            if active_lease:
                tenant.tenant_status = 'active'
            elif tenant.lease_ids:
                # لو مفيش active، ناخد حالة آخر Lease
                tenant.tenant_status = tenant.lease_ids[-1].state
            else:
                tenant.tenant_status = 'no_lease'

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
                