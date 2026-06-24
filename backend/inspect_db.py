import os, django
os.environ['DJANGO_SETTINGS_MODULE'] = 'hotelbookci.settings'
django.setup()

from apps.accounts.models import User
from apps.rooms.models import RoomCategory, Room, SeasonalRate
from apps.reservations.models import Reservation, Payment, CheckIn
from django.db import connection

print("=== ETAT DE LA BASE DE DONNEES ===")
print(f"Utilisateurs  : {User.objects.count()}")
print(f"  clients      : {User.objects.filter(role='client').count()}")
print(f"  receptionist : {User.objects.filter(role='receptionist').count()}")
print(f"  admins       : {User.objects.filter(role='admin').count()}")
print()
print(f"Categories    : {RoomCategory.objects.count()}")
for c in RoomCategory.objects.all():
    print(f"  {c.name}: {c.base_price} FCFA/nuit | {c.rooms.count()} chambre(s)")
print()
print(f"Chambres      : {Room.objects.count()}")
print(f"Tarifs saison : {SeasonalRate.objects.count()}")
for r in SeasonalRate.objects.all():
    print(f"  {r.name} | {r.category.name} | {r.start_date} -> {r.end_date} | {r.price_per_night} FCFA")
print()
print(f"Reservations  : {Reservation.objects.count()}")
print(f"Paiements     : {Payment.objects.count()}")
print(f"CheckIn       : {CheckIn.objects.count()}")
print()
print("Tables SQL creees dans db.sqlite3:")
tables = connection.introspection.table_names()
for t in sorted(tables):
    print(f"  - {t}")
