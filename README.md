# 🏥 MediLink - Plateforme Médicale Intelligente

**MediLink** est une application web de gestion médicale intégrant l'IA pour la détection précoce du cancer de la peau. La plateforme permet la gestion des patients, médecins, rendez-vous et offre un système d'analyse d'images dermatoscopiques utilisant le deep learning.

## 📋 Fonctionnalités

- **Gestion multi-rôles** : Patients, Médecins, Administrateurs avec authentification sécurisée
- **Détection IA du cancer de la peau** : Pipeline 3 étapes (ResNet-152, U-Net, EfficientNet-B4)
- **Système de rendez-vous** : Calendrier interactif, gestion des disponibilités
- **Chatbot médical** : Assistant intelligent basé sur Google Gemini API
- **Gestion des dossiers médicaux** : Historique complet, consultation sécurisée
- **Tableaux de bord** : Statistiques et visualisations pour chaque rôle

## 🛠️ Technologies

| Catégorie | Technologies |
|-----------|-------------|
| **Backend** | Django 4.0+, Python, SQLite, Django Signals |
| **Frontend** | HTML5/CSS3, Bootstrap 5, JavaScript, FullCalendar.js |
| **IA/ML** | TensorFlow, Keras, OpenCV, NumPy, ResNet-152, U-Net, EfficientNet-B4 |
| **APIs** | Google Gemini API, REST API |

## 📊 Architecture

Pipeline IA de détection : **Upload** → **Preprocessing** → **Skin Detection** → **Segmentation** → **Classification** → **Résultats**

## 🚀 Installation

### Prérequis

- Python 3.8+
- pip

### Étapes

1. **Cloner le projet**
   ```bash
   git clone <url-du-repo>
   cd medical2
   ```

2. **Créer un environnement virtuel**
   ```bash
   python -m venv venv
   venv\Scripts\activate   # Windows
   ```

3. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configuration**  
   Créer un fichier `.env` (ou configurer) avec la clé API Google Gemini pour le chatbot :
   ```
   GEMINI_API_KEY=votre_cle_api
   ```

5. **Migrations de la base de données**
   ```bash
   cd medical
   python manage.py migrate
   ```

6. **Créer un superutilisateur** (optionnel)
   ```bash
   python manage.py createsuperuser
   ```

7. **Lancer le serveur**
   ```bash
   python manage.py runserver
   ```

L'application est accessible à l'adresse : **http://127.0.0.1:8000/**

## 📁 Structure du projet

```
medical2/
├── medical/           # Configuration Django
├── users/             # Gestion utilisateurs (patients, médecins, admins)
├── dossiers/          # Dossiers médicaux
├── gestion_medecins/  # Gestion des médecins
├── rendezvous/        # Système de rendez-vous
├── disponibilite/     # Gestion des disponibilités
├── dashboard/         # Tableaux de bord
├── chatbot/           # Assistant IA (Gemini)
├── skin_cancer/       # Détection cancer de la peau (IA)
└── templates/         # Templates HTML partagés
```

## 📌 Applications principales

| URL | Description |
|-----|-------------|
| `/` | Accueil et authentification |
| `/admin/` | Interface d'administration Django |
| `/dossiers/` | Dossiers médicaux |
| `/medecins/` | Gestion des médecins |
| `/rendezvous/` | Prise de rendez-vous |
| `/dashboard/` | Tableaux de bord |
| `/chatbot/` | Chatbot médical |
| `/skin-cancer/` | Détection IA du cancer de la peau |

---

*Développé avec Django, TensorFlow et les dernières technologies web*
