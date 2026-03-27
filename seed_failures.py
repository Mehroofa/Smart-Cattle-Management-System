import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'Cattle_Farm.settings'
import django
django.setup()

from django.contrib.auth.models import User
from systemapp.models import Cattle, PurchaseRequest, BuyerProfile

# Get the buyer user
buyer = User.objects.get(username='philip@gmail.com')
print(f"Buyer: {buyer.username}")

# Get some cattle
cattle_list = list(Cattle.objects.filter(is_for_sale=True)[:3])
print(f"Cattle count: {len(cattle_list)}")

# === CASE 1: Duplicate Detection ===
# Create a pending purchase request so when the user tries again, it triggers duplicate detection
c1 = cattle_list[0]
pr1, created = PurchaseRequest.objects.get_or_create(
    buyer=buyer, cattle=c1, status='pending',
    defaults={'ai_score': 0.5}
)
if created:
    print(f"Created DUPLICATE case: PurchaseRequest for {c1.tag_id} ({c1.breed}) - status=pending")
    print(f"  -> When user tries to buy {c1.tag_id} again, they'll see the duplicate_detection page")
else:
    print(f"Exists: PurchaseRequest for {c1.tag_id}")

# === CASE 2: Purchase Restriction ===
# Create an approved purchase request with negative ai_score (flagged as fake)
c2 = cattle_list[1]
pr2, created = PurchaseRequest.objects.get_or_create(
    buyer=buyer, cattle=c2, status='approved',
    defaults={'ai_score': -5.0}
)
if created:
    print(f"Created RESTRICTION case: PurchaseRequest for {c2.tag_id} ({c2.breed}) - ai_score=-5.0")
    print(f"  -> When user tries to place_order for this, they'll see the purchase_restriction page")
else:
    # Update the existing one to have negative ai_score
    pr2.ai_score = -5.0
    pr2.save()
    print(f"Updated RESTRICTION case: PurchaseRequest for {c2.tag_id} - ai_score=-5.0")

print("\nSample data ready!")
print(f"  Duplicate detection: Try buying cattle {c1.tag_id} ({c1.breed}) at /systemapp/purchase/{c1.id}/")
print(f"  Purchase restriction: Try placing order at /systemapp/order/{pr2.id}/")
