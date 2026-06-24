"""
Script de création des données de démonstration pour HotelBookCI (version Sénégal - RIU Baobab, 3 offres).
Lance avec: python manage.py shell < create_demo_data.py
OU: python create_demo_data.py (depuis le dossier backend)
"""
import os
import sys
# pyrefly: ignore [missing-import]
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hotelbookci.settings')
os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

# pyrefly: ignore [missing-import]
from django.contrib.auth import get_user_model
from apps.rooms.models import RoomCategory, Room, SeasonalRate
import datetime

User = get_user_model()

print("=== Creation des donnees de demonstration (Senegal - RIU Baobab - 3 categories) ===")

# ---- Superuser Admin ----
if not User.objects.filter(username='admin').exists():
    admin = User.objects.create_superuser(
        username='admin',
        email='abdoulaye.ndiaye@hotelbookci.sn',
        password='Admin1234!',
        first_name='Abdoulaye',
        last_name='Ndiaye',
        role='admin',
        is_staff=True,
    )
    print("Admin cree: admin / Admin1234! (Abdoulaye Ndiaye)")
else:
    print("Admin existe deja")

# ---- Réceptionniste ----
if not User.objects.filter(username='receptionniste').exists():
    recept = User.objects.create_user(
        username='receptionniste',
        email='fatou.diop@hotelbookci.sn',
        password='Recept1234!',
        first_name='Fatou',
        last_name='Diop',
        role='receptionist',
        phone='+221 77 123 45 67',
    )
    print("Receptionniste cree: receptionniste / Recept1234! (Fatou Diop)")

# ---- Client de test ----
if not User.objects.filter(username='client1').exists():
    client = User.objects.create_user(
        username='client1',
        email='moustapha.sow@yahoo.sn',
        password='Client1234!',
        first_name='Moustapha',
        last_name='Sow',
        role='client',
        phone='+221 76 987 65 43',
    )
    print("Client cree: client1 / Client1234! (Moustapha Sow)")

# ---- Catégories de chambres ----
categories_data = [
    {
        'name': 'Chambre Double Standard',
        'description': 'Chambre confortable avec balcon ou terrasse, parfaite pour un sejour detendu a Pointe Sarene.',
        'max_occupancy': 2,
        'base_price': 55000,
        'amenities': ['WiFi Gratuit', 'Climatisation', 'Mini-bar', 'TV Satellite', 'Coffre-fort'],
    },
    {
        'name': 'Double Standard Vue Mer',
        'description': 'Offrez-vous une vue imprenable sur l ocean Atlantique depuis votre balcon prive.',
        'max_occupancy': 2,
        'base_price': 75000,
        'amenities': ['WiFi Premium', 'Climatisation', 'Mini-bar', 'TV 55"', 'Vue sur Ocean', 'Machine a cafe'],
    },
    {
        'name': 'Suite Swim-Up Vue Mer',
        'description': 'Le summum de l exclusivite. Acces direct a la piscine privee et vue panoramique spectaculaire sur la plage.',
        'max_occupancy': 3,
        'base_price': 280000,
        'amenities': ['Piscine Privee Connectee', 'WiFi Premium', 'Climatisation', 'Salon Separe', 'Baignoire Hydromassage', 'Service Premium'],
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
        print(f"Categorie creee: {cat.name}")

# ---- Chambres ----
rooms_data = [
    # Double Standard (étage 1)
    {'number': '101', 'floor': 1, 'category': 'Chambre Double Standard'},
    {'number': '102', 'floor': 1, 'category': 'Chambre Double Standard'},
    {'number': '103', 'floor': 1, 'category': 'Chambre Double Standard'},
    # Double Standard Vue Mer (étage 2)
    {'number': '201', 'floor': 2, 'category': 'Double Standard Vue Mer'},
    {'number': '202', 'floor': 2, 'category': 'Double Standard Vue Mer'},
    {'number': '203', 'floor': 2, 'category': 'Double Standard Vue Mer'},
    # Suite Swim-Up Vue Mer (étage 3)
    {'number': '301', 'floor': 3, 'category': 'Suite Swim-Up Vue Mer'},
    {'number': '302', 'floor': 3, 'category': 'Suite Swim-Up Vue Mer'},
    {'number': 'SU1', 'floor': 4, 'category': 'Suite Swim-Up Vue Mer'},
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
        print(f"Chambre creee: {room.number} ({data['category']})")

# ---- Tarifs saisonniers ----
rates_data = [
    {
        'category': 'Chambre Double Standard',
        'name': 'Haute Saison (Hivernage)',
        'start_date': datetime.date(2025, 7, 1),
        'end_date': datetime.date(2025, 8, 31),
        'price_per_night': 65000,
    },
    {
        'category': 'Double Standard Vue Mer',
        'name': 'Haute Saison (Hivernage)',
        'start_date': datetime.date(2025, 7, 1),
        'end_date': datetime.date(2025, 8, 31),
        'price_per_night': 90000,
    },
    {
        'category': 'Suite Swim-Up Vue Mer',
        'name': 'Saison des Fetes (Fin d Annee)',
        'start_date': datetime.date(2025, 12, 20),
        'end_date': datetime.date(2026, 1, 5),
        'price_per_night': 350000,
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
        print(f"Tarif cree: {rate.name} - {cat.name}")

print("\n" + "="*50)
print("Donnees de demonstration Senegaleses creees !")
print("="*50)
print("Comptes disponibles:")
print("  admin         / Admin1234!   (Abdoulaye Ndiaye)")
print("  receptionniste / Recept1234! (Fatou Diop)")
print("  client1       / Client1234!  (Moustapha Sow)")
print("="*50)
