# MediLink — Intelligent Medical Platform

**MediLink** is a medical management web app that uses artificial intelligence for early skin-cancer detection. It covers multi-role sign-in, appointment booking, medical-record follow-up, and a conversational medical assistant.

<p align="center">
  <img src="docs/screenshots/01-login.png" alt="MediLink sign-in page" width="800"/>
</p>

<p align="center">
  <em>Multi-role sign-in — Patient, Doctor, Administrator</em>
</p>

---

## Features

| Module | Description |
|--------|-------------|
| **Multi-role** | Dedicated Patient, Doctor, and Administrator spaces with secure sign-in |
| **AI detection** | Dermoscopic image analysis (ResNet-152, U-Net, EfficientNet-B4) |
| **Appointments** | Interactive calendar, availability, and status management |
| **Medical chatbot** | Intelligent assistant powered by Google Gemini |
| **Medical records** | Secure history and consultation |
| **Dashboards** | Statistics and charts by role |
| **Notifications** | Real-time alerts (validations, appointment confirmations) |

---

## Interface overview

### Patient space

A personal area for the profile, appointments, the skin scanner, and the chatbot.

| Patient home | My appointments |
|:---------------:|:---------------:|
| <img src="docs/screenshots/02-patient-dashboard.png" width="400" alt="Patient dashboard"/> | <img src="docs/screenshots/03-patient-appointments.png" width="400" alt="My appointments"/> |

| Notifications | Skin scanner |
|:-------------:|:------------:|
| <img src="docs/screenshots/04-patient-notifications.png" width="400" alt="Patient notifications"/> | <img src="docs/screenshots/05-skin-scanner.png" width="400" alt="Skin scanner"/> |

| Scan history | Medical chatbot |
|:--------------------:|:---------------:|
| <img src="docs/screenshots/06-scan-history.png" width="400" alt="Scan history"/> | <img src="docs/screenshots/07-medical-chatbot.png" width="400" alt="Medical chatbot"/> |

### Doctor space

Clinical dashboard, availability calendar, and appointment review.

| Doctor dashboard | Availability calendar |
|:-----------------:|:-----------------------------:|
| <img src="docs/screenshots/08-doctor-dashboard.png" width="400" alt="Doctor dashboard"/> | <img src="docs/screenshots/09-availability-calendar.png" width="400" alt="Availability calendar"/> |

<p align="center">
  <img src="docs/screenshots/10-appointment-management.png" alt="Appointment management" width="700"/>
</p>
<p align="center"><em>Appointment list — confirm, reschedule, or cancel</em></p>

### Administrator space

Doctor approval, overall statistics, and scan supervision.

| Admin home | Statistics |
|:-------------:|:------------:|
| <img src="docs/screenshots/11-admin-dashboard.png" width="400" alt="Administrator dashboard"/> | <img src="docs/screenshots/12-admin-statistics.png" width="400" alt="Admin statistics"/> |

| Doctor approval | Admin notifications |
|:-----------------------:|:-------------------:|
| <img src="docs/screenshots/13-doctor-validation.png" width="400" alt="Doctor approval"/> | <img src="docs/screenshots/14-admin-notifications.png" width="400" alt="Admin notifications"/> |

<p align="center">
  <img src="docs/screenshots/15-admin-scans.png" alt="Administrator scan dashboard" width="700"/>
</p>
<p align="center"><em>Scan dashboard — breakdown by risk level</em></p>

---

## Technologies

| Category | Stack |
|-----------|-------|
| **Backend** | Django 4.0+, Python, SQLite, Django Signals |
| **Frontend** | HTML5, CSS3, Bootstrap 5, JavaScript, FullCalendar.js |
| **AI / ML** | TensorFlow, Keras, OpenCV, NumPy, ResNet-152, U-Net, EfficientNet-B4 |
| **APIs** | Google Gemini API |

### AI detection pipeline

```text
Upload → Preprocessing → Skin Detection → Segmentation → Classification → Results
```

---

## Installation

### Requirements

- Python 3.8+
- pip

### Steps

1. **Clone the repository**

   ```bash
   git clone https://github.com/SalahG005/MediLink.git
   cd MediLink
   ```

2. **Create a virtual environment**

   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS / Linux
   source venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the Gemini API** (chatbot)

   Create a `.env` file at the repository root:

   ```env
   GEMINI_API_KEY=your_api_key
   ```

5. **Apply migrations**

   ```bash
   python manage.py migrate
   ```

6. **Create a superuser** (optional)

   ```bash
   python manage.py createsuperuser
   ```

7. **Start the server**

   ```bash
   python manage.py runserver
   ```

The app is available at **http://127.0.0.1:8000/**

---

## Project structure

```text
MediLink/
├── medical/            # Django configuration
├── users/              # Patients, doctors, administrators
├── dossiers/           # Medical records
├── gestion_medecins/   # Doctor approval and management
├── rendezvous/         # Appointment booking and follow-up
├── disponibilite/      # Doctor availability
├── dashboard/          # Dashboards
├── chatbot/            # Medical assistant (Gemini)
├── specialite/         # Medical specialties
├── templates/          # Shared HTML templates
├── static/             # Static assets
├── docs/screenshots/   # README screenshots
└── requirements.txt
```

---

## Main routes

| URL | Description |
|-----|-------------|
| `/` | Home and sign-in |
| `/admin/` | Django administration |
| `/dossiers/` | Medical records |
| `/medecins/` | Doctor management |
| `/rendezvous/` | Appointments |
| `/dashboard/` | Dashboards |
| `/chatbot/` | Medical chatbot |
| `/skin-cancer/` | AI skin-cancer detection |

---

## Authors

Built as an intelligent medical-platform project.

---

<p align="center">
  <sub>© 2025 MediLink — All rights reserved</sub>
</p>
