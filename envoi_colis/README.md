# 📦 Cargo Fusion – Module Odoo de gestion de colis consolidés

**Cargo Fusion** est un module Odoo développé par **Mega-Ique Digital** pour la gestion des envois groupés (colis consolidés). Il permet d’enregistrer, organiser, suivre et préparer des expéditions de plusieurs colis regroupés par client ou par destination.

---

## 🎯 Objectif du module

Permettre à une entreprise de logistique ou de transport d'optimiser :
- la gestion de colis entrants,
- leur regroupement en envois consolidés,
- le suivi logistique,
- et la préparation à l’expédition et à la facturation.

---

## ⚙️ Fonctionnalités principales

- Interface web intégrée (inspirée de `index.html`)
- Ajout et gestion des colis individuels
- Création de groupes de colis (expéditions consolidées)
- Association des colis à des destinataires Odoo (`res.partner`)
- Suivi de statut (en attente, prêt à expédier, expédié)
- Historique des mouvements
- Intégration possible avec la facturation Odoo (optionnel)

---

## 🧩 Structure du module

```
cargo_fusion/
├── __manifest__.py
├── models/
│   └── fusion.py
├── views/
│   ├── fusion_views.xml
│   └── templates.xml
├── static/
│   └── src/
│       └── html/
│           └── index.html (version intégrée)
├── security/
│   └── ir.model.access.csv
├── controllers/
│   └── main.py (optionnel)
├── README.md
```

---

## 🚀 Installation

1. Placer le dossier `cargo_fusion` dans le répertoire `addons` de votre instance Odoo.
2. Redémarrer le serveur Odoo (`./odoo-bin -d <your_db> -u cargo_fusion`).
3. Activer le mode développeur dans Odoo.
4. Installer le module via l’interface ou le menu des modules.

---

## 🧑‍🎓 Contributeur

Développeurs de Mega-Ique Digital

---

## 🔧 Technologies utilisées

- Odoo 15 Community
- Python 3 (ORM Odoo)
- HTML5/CSS3 pour l’interface embarquée
- Docker (pour l’environnement de développement local)

---

## 📝 Licence

Développement interne Mega-Ique Digital UG – Toute reproduction, distribution ou usage commercial nécessite une autorisation écrite.

---