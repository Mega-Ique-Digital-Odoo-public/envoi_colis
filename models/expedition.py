from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import UserError
import random
import string
import logging
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)


class Expedition(models.Model):
    _name = 'envoi.colis.expedition'
    _description = 'Expédition de colis'
    _rec_name = 'display_name'
    #_inherit = 'account.move'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.model
    def _generate_expedition_id(self):
        now = datetime.now()
        return now.strftime("%y%m%d%H%M")

    @api.model
    def _generate_security_code(self):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))

    display_name = fields.Char(string='Nom d\'affichage', compute='_compute_display_name', store=True, readonly=False)
    expedition_id = fields.Char(string='ID Expédition', default=_generate_expedition_id, readonly=True)
    code_securite = fields.Char(string='Code de sécurité', default=_generate_security_code, readonly=True)
    conteneur_id = fields.Many2one('envoi.colis.conteneur', string='Conteneur', required=True, readonly=True,
                                   default=lambda self: self._default_conteneur_id())
    client_id = fields.Many2one('res.partner', string='Client', required=True)
    #payment_id = fields.One2many('account.move', copy=False, readonly=True, string='Facture', inverse_name=None)
    payment_id = fields.Many2one('account.move', string='Facture', copy=False, readonly=True)
    transport = fields.Selection(selection= [('1', 'Maritime'), ('2', 'Aerien'), ('3', 'Terrestre')], 
                                 string='Moyen de transport', default='Maritime')
    colis_id = fields.One2many('envoi.colis.colis', 'expedition_id', string='Colis')
    nombre_colis = fields.Integer(string='Nombre de colis', compute='_compute_nombre_colis', store=True)

    state = fields.Selection (selection=[
        ('default', 'Default'),
        ('pending', 'Pending'), 
        ('confirme', 'Confirme')], string='Suivi du statut', tracking=True, default='default')
    

    @api.depends('expedition_id')
    def _compute_display_name(self):
        for record in self:
            if record.expedition_id:
                record.display_name = f"Expédition {record.expedition_id} - {record.client_id.name}"
            else:
                record.display_name = f"New Expedition"
    

    def _default_conteneur_id(self):
        return self.env.context.get('active_id')

    @api.depends('colis_id')
    def _compute_nombre_colis(self):
        for record in self:
            record.nombre_colis = len(record.colis_id)

    @api.depends('colis_id.cout')
    def _compute_cout_initial(self):
        for record in self:
            record.cout_initial = sum(colis.cout for colis in record.colis_id)

    @api.depends('cout_initial', 'remise_pourcentage', 'remise_montant')
    def _compute_cout_final(self):
        for record in self:
            if record.remise_pourcentage > 0:
                record.remise_montant = 0
                record.cout_final = record.cout_initial * (1 - record.remise_pourcentage / 100)
            elif record.remise_montant > 0:
                record.remise_pourcentage = 0
                record.cout_final = record.cout_initial - record.remise_montant
            else:
                record.cout_final = record.cout_initial


    @api.onchange('remise_pourcentage')
    def _onchange_remise_pourcentage(self):
        if self.remise_pourcentage > 0:
            self.remise_montant = 0

    @api.onchange('remise_montant')
    def _onchange_remise_montant(self):
        if self.remise_montant > 0:
            self.remise_pourcentage = 0

    
    def _send_status_email(self):
        template = self.env.ref('envoi_colis.email_expedition_status')
        for expedition in self:
            template.send_mail(expedition.expedition_id, force_send=True)


    def action_create_colis(self):
        return {
            'name': 'Nouveau Colis',
            'type': 'ir.actions.act_window',
            'res_model': 'envoi.colis.colis',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_expedition_id': self.id},
        }


    def action_view_colis(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Colis',
            'view_mode': 'tree,form',
            'res_model': 'envoi.colis.colis',
            'domain': [('expedition_id', '=', self.id)],
            'context': {'default_expedition_id': self.id},
        }
    
    def action_prepare_expedition(self):
        _logger.info(msg="***************** start prepare expedition *****************")
        self.ensure_one()
        if self.state == 'default' and self.nombre_colis >= 1:
            self.write({'state': 'pending'})
        else:
            raise UserError(_("L'expedition doit contenir au moins un colis."))



    def action_confirme(self):
        for expedition in self:
            # Create invoice before changing state
            invoice = expedition.create_invoice()
            if invoice:
                expedition.payment_id = invoice.id
                # Change state to 'confirme'
                expedition.state = 'confirme'
                # self._send_status_email()
            else:
                raise UserError(_("Failed to create invoice for expedition %s") % expedition.expedition_id)

            expedition.state = 'confirme'
            #self._send_status_email()
        return True

    
   
    def create_invoice(self):
        self.ensure_one()
        if not self.payment_id:
            product_id = None
            income_account = None
            # Prepare invoice lines based on colis
            invoice_lines = []

            # Calculate total price from all colis
            total_price = sum(colis.cout for colis in self.colis_id) if self.colis_id else 0

            # Search for products in the 'envoi_colis' category
            products = self.env['product.product'].search([('categ_id.name', '=', 'envoi_colis')], limit=1)
            if products:
                product = products[0]

                #Get product ID
                product_id = product.id

                # Get the income account from the product's category
                income_account = product.categ_id.property_account_income_categ_id

                # Now you can use these values
                _logger.info(f"Product ID: {product_id}")
                _logger.info(f"Income Account ID: {income_account.id if income_account else 'Not set'}")
            else:
                raise UserError(_("No product found in the 'envoi_colis' category."))
            
            invoice_lines.append((0, 0, {
                'product_id': product_id,
                'name': f"Expedition {self.expedition_id} - {len(self.colis_id)} colis",
                'quantity': 1,
                'price_unit': total_price,
                'account_id': income_account.id,
            }))

            # Create the invoice
            invoice = self.env['account.move'].create({
                'move_type': 'out_invoice',
                'partner_id': self.client_id.id,
                'invoice_line_ids': invoice_lines,
                'invoice_origin': f"{self.expedition_id}",
            })

            return invoice
        return False
