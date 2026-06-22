"""
Script de création des données de démonstration pour HotelBookCI.
Lance avec: python manage.py shell < create_demo_data.py
OU: python create_demo_data.py (depuis le dossier backend)
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hotelbookci.settings')
os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth import get_user_model
from apps.rooms.models import RoomCategory, Room, SeasonalRate
import datetime

User = get_user_model()

print("=== Creation des donnees de demonstration HotelBookCI ===")


# ---- Superuser Admin ----
if not User.objects.filter(username='admin').exists():
    admin = User.objects.create_superuser(
        username='admin',
        email='admin@hotelbookci.com',
        password='Admin1234!',
        first_name='Administrateur',
        last_name='Système',
        role='admin',
        is_staff=True,
    )
    print(f"✅ Admin créé: admin / Admin1234!")
else:
    print("ℹ️  Admin existe déjà")

# ---- Réceptionniste ----
if not User.objects.filter(username='receptionniste').exists():
    recept = User.objects.create_user(
        username='receptionniste',
        email='recept@hotelbookci.com',
        password='Recept1234!',
        first_name='Marie',
        last_name='Dupont',
        role='receptionist',
        phone='+225 07 00 00 00',
    )
    print(f"✅ Réceptionniste créé: receptionniste / Recept1234!")

# ---- Client de test ----
if not User.objects.filter(username='client1').exists():
    client = User.objects.create_user(
        username='client1',
        email='client@hotelbookci.com',
        password='Client1234!',
        first_name='Kofi',
        last_name='Mensah',
        role='client',
        phone='+225 05 00 00 00',
    )
    print(f"✅ Client créé: client1 / Client1234!")

# ---- Catégories de chambres ----
categories_data = [
    {
        'name': 'Standard',
        'description': 'Chambre confortable avec tout le nécessaire pour un séjour agréable.',
        'max_occupancy': 2,
        'base_price': 35000,
        'amenities': ['WiFi', 'Climatisation', 'TV', 'Salle de bain privée'],
    },
    {
        'name': 'Deluxe',
        'description': 'Chambre spacieuse avec vue sur le jardin et équipements premium.',
        'max_occupancy': 3,
        'base_price': 65000,
        'amenities': ['WiFi Haut Débit', 'Climatisation', 'TV 55"', 'Minibar', 'Coffre-fort'],
    },
    {
        'name': 'Suite Junior',
        'description': 'Suite avec salon séparé, parfaite pour les voyages d\'affaires.',
        'max_occupancy': 4,
        'base_price': 120000,
        'amenities': ['WiFi Haut Débit', 'Climatisation', 'TV 65"', 'Minibar', 'Baignoire', 'Salon'],
    },
    {
        'name': 'Suite Présidentielle',
        'description': 'Le summum du luxe. Vue panoramique, jacuzzi, butler 24h/24.',
        'max_occupancy': 4,
        'base_price': 250000,
        'amenities': ['WiFi Premium', 'Climatisation Multi-zones', 'Home Cinéma', 'Jacuzzi', 'Butler', 'Terrasse Privée'],
    },
]

categories = {}
for data in categories_data:
    cat, created = RoomCategory.objects.get_or_create(
        name=data['name'],
        defaults=data,
    )
    categories[data['name']] = cat
    if created:
        print(f"✅ Catégorie créée: {cat.name}")

# ---- Chambres ----
rooms_data = [
    # Standard (étage 1)
    {'number': '101', 'floor': 1, 'category': 'Standard'},
    {'number': '102', 'floor': 1, 'category': 'Standard'},
    {'number': '103', 'floor': 1, 'category': 'Standard'},
    # Deluxe (étage 2)
    {'number': '201', 'floor': 2, 'category': 'Deluxe'},
    {'number': '202', 'floor': 2, 'category': 'Deluxe'},
    {'number': '203', 'floor': 2, 'category': 'Deluxe'},
    # Suite Junior (étage 3)
    {'number': '301', 'floor': 3, 'category': 'Suite Junior'},
    {'number': '302', 'floor': 3, 'category': 'Suite Junior'},
    # Suite Présidentielle (étage 4)
    {'number': 'PH1', 'floor': 4, 'category': 'Suite Présidentielle'},
]

for data in rooms_data:
    room, created = Room.objects.get_or_create(
        number=data['number'],
        defaults={
            'floor': data['floor'],
            'category': categories[data['category']],
        },
    )
    if created:
        print(f"✅ Chambre créée: {room.number} ({data['category']})")

# ---- Tarifs saisonniers ----
rates_data = [
    {
        'category': 'Standard',
        'name': 'Haute Saison (Été)',
        'start_date': datetime.date(2025, 7, 1),
        'end_date': datetime.date(2025, 8, 31),
        'price_per_night': 45000,
    },
    {
        'category': 'Deluxe',
        'name': 'Haute Saison (Été)',
        'start_date': datetime.date(2025, 7, 1),
        'end_date': datetime.date(2025, 8, 31),
        'price_per_night': 85000,
    },
    {
        'category': 'Suite Junior',
        'name': 'Noël & Nouvel An',
        'start_date': datetime.date(2025, 12, 20),
        'end_date': datetime.date(2026, 1, 5),
        'price_per_night': 180000,
    },
    {
        'category': 'Suite Présidentielle',
        'name': 'Noël & Nouvel An',
        'start_date': datetime.date(2025, 12, 20),
        'end_date': datetime.date(2026, 1, 5),
        'price_per_night': 380000,
    },
]

for data in rates_data:
    cat = categories[data.pop('category')]
    rate, created = SeasonalRate.objects.get_or_create(
        category=cat,
        name=data['name'],
        defaults={**data},
    )
    if created:
        print(f"✅ Tarif créé: {rate.name} - {cat.name}")

print("\n" + "="*50)
print("🎉 Données de démonstration créées !")
print("="*50)
print("Comptes disponibles:")
print("  admin         / Admin1234!   (Administrateur)")
print("  receptionniste / Recept1234! (Réceptionniste)")
print("  client1       / Client1234!  (Client)")
print("="*50)
print("Swagger UI: http://127.0.0.1:8000/api/schema/swagger-ui/")
print("Admin Django: http://127.0.0.1:8000/admin/")
