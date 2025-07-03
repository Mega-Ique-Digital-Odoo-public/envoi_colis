# my_module/models/conteneur.py
from odoo import fields, models, api

class MyConteneur(models.Model):
    _name = 'my.conteneur'
    _description = 'Mon Conteneur Personnalisé'

    name = fields.Char(string="Nom du Conteneur", required=True)
    status = fields.Selection([
        ('brouillon', 'Brouillon'),
        ('en_cours', 'En Cours'),
        ('termine', 'Terminé'),
        ('annule', 'Annulé'),
    ], string="Statut", default='brouillon', required=True)
    client_id = fields.Many2one('res.partner', string="Client")
    description = fields.Text(string="Description")

    @api.multi # Pour Odoo 14+ (ou @api.onchange, mais write est plus robuste pour la persistance)
    def write(self, vals):
        # Récupère l'ancien statut avant la mise à jour
        old_statuses = {record.id: record.status for record in self}

        # Appelle la méthode write originale pour effectuer la mise à jour
        res = super(MyConteneur, self).write(vals)

        # Vérifie si le statut a changé et est devenu 'termine'
        if 'status' in vals and vals['status'] == 'termine':
            for record in self:
                # S'assure que le statut a réellement changé pour ce record
                if record.status == 'termine' and old_statuses.get(record.id) != 'termine':
                    # Vérifie si un client est lié et a une adresse email
                    if record.client_id and record.client_id.email:
                        # Cherche le template d'email par son ID externe
                        template = self.env.ref('my_module.email_template_conteneur_status_change')
                        if template:
                            # Envoie l'email en utilisant le template
                            template.send_mail(record.id, force_send=True)
                            self.env.user.notify_success(
                                message=f"Email de notification envoyé au client {record.client_id.name} pour le conteneur {record.name}."
                            )
                        else:
                            self.env.user.notify_warning(
                                message="Le template d'email de notification de statut n'a pas été trouvé."
                            )
                    else:
                        self.env.user.notify_warning(
                            message=f"Impossible d'envoyer l'email pour le conteneur {record.name}: aucun client ou email client trouvé."
                        )
        return res

    # Exemple de méthode pour un bouton ou autre, si vous ne voulez pas utiliser write
    def send_status_email(self):
        self.ensure_one() # S'assure qu'il n'y a qu'un seul enregistrement
        if self.client_id and self.client_id.email:
            template = self.env.ref('my_module.email_template_conteneur_status_change')
            if template:
                template.send_mail(self.id, force_send=True)
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'message': f"Email de notification envoyé au client {self.client_id.name}.",
                        'type': 'success',
                        'sticky': False,
                    }
                }
            else:
                raise UserError("Le template d'email de notification de statut n'a pas été trouvé.")
        else:
            raise UserError("Aucun client ou adresse email client trouvée pour envoyer la notification.")