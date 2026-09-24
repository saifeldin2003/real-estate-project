from odoo import models, fields, api
# from odoo.exceptions import UserError


class Property(models.Model):
    _name = 'real_estate.property'
    _description = 'Real Estate Property'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Property Name', tracking=True,
                       required=True, index=True)
    description = fields.Text(string='Description')
    price = fields.Float(string='Monthly Rent', required=True)
    bedrooms = fields.Integer(string='Bedrooms', required=True)
    available = fields.Boolean(string='Available', default=True, index=True)
    maintenance_ids = fields.One2many(
        'maintenance.request',
        'property_id',
        string='Maintenance'
    )
    lease_ids = fields.One2many(
        'real_estate.lease',
        'property_id',
        string='Property',
        required=True,
        ondelete='cascade',  # If property deleted, delete lease too
        index=True
    )
    agent_id = fields.Many2one('res.users', string='Sales Person')
    property_image = fields.Image(
        string="Property Image", max_width=1920, max_height=1920)
    discount = fields.Float(
        string='Discount', help='Discount percentage for the property', default=0.0)
    property_status = fields.Selection([
        ('draft', 'Draft'),
        ('available', 'Available'),
        ('reserved', 'Reserved'),
        ('occupied', 'Occupied'),
        ('canceled', 'Canceled'),], string='Property Status', default='draft')
    property_type = fields.Selection([
        ('apartment', 'Apartment'),
        ('house', 'House'),
        ('villa', 'Villa'),
        ('commercial', 'Commercial'),], string='Property Type', required=True)
    deposite = fields.Float(
        string='Deposit', help='Deposit amount for the property', required=True)
    lease_count = fields.Integer(compute="_compute_lease_count")
    maintenance_count = fields.Integer(compute="_compute_maintenance_count")

    @api.depends('lease_ids')
    def _compute_lease_count(self):
        for record in self:
            record.lease_count = len(record.lease_ids)

    @api.depends('maintenance_ids')
    def _compute_maintenance_count(self):
        for record in self:
            record.maintenance_count = len(record.maintenance_ids)

# mark as available > reseve > available
# mark as occupied > as canceled
    def action_view_leases(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Leases',
            'res_model': 'real_estate.lease',
            'view_mode': 'tree',
            'domain': [
                ('property_id', '=', self.id)
            ],
        }

    def action_view_maintenances(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Leases',
            'res_model': 'maintenance.request',
            'view_mode': 'tree',
            'domain': [
                ('property_id', '=', self.id)
            ],
        }

    def mark_as_occupied(self):
        """Mark property as no longer available"""
        for record in self:
            record.write({
                'available': False,
                'property_status': 'occupied',
            })

    def mark_as_available(self):
        """Mark property as available"""
        for record in self:
            record.write({
                'available': True,
                'property_status': 'available',
            })

    def mark_as_reserved(self):
        for record in self:
            record.write({
                'available': False,
                'property_status': 'reserved',
            })

    def mark_as_canceled(self):
        for record in self:
            record.write({
                'available': False,
                'property_status': 'canceled',
            })

    def _cron_auto_show_property(self):
        print("here cron action in property.py in line 114")
        # property = self.search([], limit=1)
        # if property:
        #     property.message_post(
        #         body="🔥 Auto Show Property Cron is working!",
        #         subject="Auto Show Property",
        #         partner_ids=[self.env.user.partner_id.id],
        #         message_type='notification',
        #     )
        # self.env['mail.activity'].create({
        #     'activity_type_id': self.env.ref(
        #         'mail.mail_activity_data_todo'
        #     ).id,
        #     'summary': 'Auto Show Property',
        #     'note': 'Cron executed successfully.',
        #     'user_id': self.env.user.id,
        #     'res_model_id': self.env['ir.model']._get_id(
        #         'real_estate.property'
        #     ),
        #     'res_id': self.search([], limit=1).id,
        # })

    # def get_agent_name(self):
    #     """Change the property type"""
    #     for record in self:
    #             if record.agent_id.name :
    #                 record.write({'description':"Name of Sales Person: " + record.agent_id.name + '\n' +"Email: "+ record.agent_id.login})
    #             else:
    #                 record.write({'description':'No Agent Assigned'})
    # def write(self, vals):
    #     if 'available' in vals and vals['available'] == False:
    #         if 'bedrooms' in vals:
    #             raise UserError("Cannot Change Bedrooms it is unavailable.")
    #     return super(Property, self).write(vals)
