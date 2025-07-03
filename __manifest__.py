{
    'name': 'Envoi Colis',
    'version': '1.0',
    'summary': 'Gestion des envois de colis par conteneurs',
    'description': """
        Module de gestion d'envoi de colis via des conteneurs
        avec suivi des expéditions, clients et coûts.
    """,
    'author': 'MEGA-IQUE DIGITAL',
    'category': 'Logistique',
    'depends': ['base', 'contacts', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'views/conteneur.xml',
        'views/expedition.xml',
        'views/colis.xml',
        'views/menu.xml',
        'data/email_conteneur_template.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}