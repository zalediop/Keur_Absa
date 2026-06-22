# HotelBookCI 🏨

Système complet de réservation d'hôtel avec Django REST Framework et frontend HTML/JS.

## Rôles
- **Client** : consulter les chambres, réserver, payer, gérer ses réservations
- **Réceptionniste** : confirmer les réservations, gérer le check-in/check-out
- **Administrateur** : gérer les chambres, tarifs, utilisateurs

## Stack Technique
- **Backend** : Django 4.2 + Django REST Framework + JWT + drf-spectacular
- **Frontend** : HTML/CSS/JavaScript vanilla
- **Auth** : JWT (access + refresh tokens)
- **Docs API** : Swagger UI (`/api/schema/swagger-ui/`)

## Installation Backend

```bash
cd backend

# Créer l'environnement virtuel
python -m venv venv

# Activer (Windows)
venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Configurer les variables d'environnement
copy .env.example .env
# Éditez .env et remplissez les valeurs (SECRET_KEY obligatoire)

# Migrations
python manage.py migrate

# Créer un superutilisateur admin
python manage.py createsuperuser

# Charger des données de démonstration (optionnel)
python manage.py loaddata fixtures/demo.json

# Lancer le serveur
python manage.py runserver
```

## Accès API
- **Swagger UI** : http://localhost:8000/api/schema/swagger-ui/
- **ReDoc** : http://localhost:8000/api/schema/redoc/
- **Admin Django** : http://localhost:8000/admin/

## Flux JWT
1. `POST /api/auth/login/` → reçoit `{ access, refresh }`
2. Stocké dans `localStorage`
3. Envoyé en header : `Authorization: Bearer <access_token>`
4. Si 401 → `POST /api/auth/token/refresh/` avec le refresh token

## Endpoints Clés (5 par rôle)

| Rôle | Endpoint | Action |
|------|----------|--------|
| Public | `POST /api/auth/register/` | Inscription |
| Client | `POST /api/reservations/` | Créer réservation |
| Client | `PATCH /api/reservations/{id}/cancel/` | Annuler |
| Réceptionniste | `POST /api/reservations/{id}/checkin/` | Check-in |
| Réceptionniste | `POST /api/reservations/{id}/checkout/` | Check-out |
| Admin | `POST /api/rooms/` | Créer chambre |
| Admin | `POST /api/rooms/rates/` | Tarif saisonnier |
| Admin | `GET /api/auth/users/` | Liste utilisateurs |

## Structure du Projet
```
HotelBookCI/
├── backend/
│   ├── hotelbookci/        # Config Django
│   ├── apps/
│   │   ├── accounts/       # Auth + Utilisateurs
│   │   ├── rooms/          # Chambres + Tarifs
│   │   └── reservations/   # Réservations + Paiements
│   ├── manage.py
│   ├── requirements.txt
│   ├── .env.example        ✅ Présent sur GitHub
│   └── .gitignore
└── frontend/               # HTML/CSS/JS
```

> **Note** : Le fichier `.env` et le dossier `venv/` sont exclus du dépôt GitHub via `.gitignore`
