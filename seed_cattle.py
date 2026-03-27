import os
from decimal import Decimal

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Cattle_Farm.settings")

import django

django.setup()

from systemapp.models import Cattle, Farm


def main() -> None:
    # Farms
    farms_data = [
        ("Green Valley Dairy", "Punjab Region", "9876543210", "FARM-GVD-2024"),
        ("Sunrise Livestock", "Rajasthan", "9988776655", "FARM-SRL-2024"),
        ("Nandi Cattle Ranch", "Karnataka", "8877665544", "FARM-NCR-2024"),
    ]

    created_farms: list[Farm] = []
    for name, loc, phone, reg_id in farms_data:
        farm, created = Farm.objects.get_or_create(
            farm_name=name,
            defaults={
                "location": loc,
                "contact_number": phone,
                "is_active": True,
                "registration_id": reg_id,
            },
        )
        created_farms.append(farm)
        print(f"{'Created' if created else 'Exists'}: {name}")

    all_farms = list(Farm.objects.all())
    print(f"\nTotal farms: {len(all_farms)}")

    # Cattle data (includes extra PENDING entries so the approval page is full)
    cattle_data = [
        {"farm": all_farms[0], "tag_id": "KF-001", "name": "Lakshmi", "cattle_type": "COW", "breed": "Gir", "age_years": 4, "age_months": 24, "weight_lbs": 900, "price": Decimal("2500.00"), "health_status": "HEALTHY"},
        {"farm": all_farms[0], "tag_id": "KF-002", "name": "Nandini", "cattle_type": "COW", "breed": "Sahiwal", "age_years": 3, "age_months": 18, "weight_lbs": 850, "price": Decimal("3200.00"), "health_status": "HEALTHY"},
        {"farm": all_farms[0], "tag_id": "KF-003", "name": "Thunder", "cattle_type": "BUFFALO", "breed": "Murrah", "age_years": 5, "age_months": 36, "weight_lbs": 1200, "price": Decimal("4500.00"), "health_status": "HEALTHY"},
        {"farm": created_farms[0], "tag_id": "GV-001", "name": "Sundari", "cattle_type": "COW", "breed": "Red Sindhi", "age_years": 2, "age_months": 12, "weight_lbs": 750, "price": Decimal("1800.00"), "health_status": "PENDING"},
        {"farm": created_farms[0], "tag_id": "GV-002", "name": "Raja", "cattle_type": "BUFFALO", "breed": "Jaffarabadi", "age_years": 6, "age_months": 40, "weight_lbs": 1400, "price": Decimal("5500.00"), "health_status": "PENDING"},
        {"farm": created_farms[0], "tag_id": "GV-003", "name": "Priya", "cattle_type": "COW", "breed": "Jersey Cross", "age_years": 3, "age_months": 20, "weight_lbs": 800, "price": Decimal("2800.00"), "health_status": "PENDING"},
        {"farm": created_farms[1], "tag_id": "SL-001", "name": "Desert Star", "cattle_type": "COW", "breed": "Tharparkar", "age_years": 4, "age_months": 29, "weight_lbs": 820, "price": Decimal("2200.00"), "health_status": "PENDING"},
        {"farm": created_farms[1], "tag_id": "SL-002", "name": "Goldie", "cattle_type": "COW", "breed": "Gir", "age_years": 5, "age_months": 30, "weight_lbs": 950, "price": Decimal("3800.00"), "health_status": "PENDING"},
        {"farm": created_farms[1], "tag_id": "SL-003", "name": "Storm", "cattle_type": "BUFFALO", "breed": "Murrah", "age_years": 3, "age_months": 18, "weight_lbs": 1100, "price": Decimal("4000.00"), "health_status": "PENDING"},
        {"farm": created_farms[2], "tag_id": "NC-001", "name": "Kaveri", "cattle_type": "COW", "breed": "Amrit Mahal", "age_years": 4, "age_months": 26, "weight_lbs": 880, "price": Decimal("2600.00"), "health_status": "PENDING"},
        {"farm": created_farms[2], "tag_id": "NC-002", "name": "Champion", "cattle_type": "BUFFALO", "breed": "Bhadawari", "age_years": 7, "age_months": 48, "weight_lbs": 1350, "price": Decimal("6000.00"), "health_status": "PENDING"},
        {"farm": created_farms[2], "tag_id": "NC-003", "name": "Meera", "cattle_type": "COW", "breed": "Sahiwal", "age_years": 2, "age_months": 15, "weight_lbs": 700, "price": Decimal("1500.00"), "health_status": "PENDING"},
        {"farm": created_farms[0], "tag_id": "GV-004", "name": "Maya", "cattle_type": "COW", "breed": "Holstein Friesian", "age_years": 2, "age_months": 22, "weight_lbs": 820, "price": Decimal("4100.00"), "health_status": "PENDING"},
        {"farm": created_farms[0], "tag_id": "GV-005", "name": "Neela", "cattle_type": "COW", "breed": "Jersey", "age_years": 3, "age_months": 28, "weight_lbs": 780, "price": Decimal("3900.00"), "health_status": "PENDING"},
        {"farm": created_farms[1], "tag_id": "SL-004", "name": "Ruby", "cattle_type": "COW", "breed": "Ayrshire", "age_years": 2, "age_months": 19, "weight_lbs": 760, "price": Decimal("3600.00"), "health_status": "PENDING"},
        {"farm": created_farms[1], "tag_id": "SL-005", "name": "Comet", "cattle_type": "COW", "breed": "Guernsey", "age_years": 3, "age_months": 31, "weight_lbs": 840, "price": Decimal("4200.00"), "health_status": "PENDING"},
        {"farm": created_farms[2], "tag_id": "NC-004", "name": "Tulsi", "cattle_type": "COW", "breed": "Hereford", "age_years": 1, "age_months": 12, "weight_lbs": 690, "price": Decimal("2700.00"), "health_status": "PENDING"},
        {"farm": created_farms[2], "tag_id": "NC-005", "name": "Bolt", "cattle_type": "BUFFALO", "breed": "Murrah", "age_years": 4, "age_months": 35, "weight_lbs": 1250, "price": Decimal("5200.00"), "health_status": "PENDING"},
        {"farm": created_farms[0], "tag_id": "GV-006", "name": "Anika", "cattle_type": "COW", "breed": "Angus", "age_years": 2, "age_months": 20, "weight_lbs": 860, "price": Decimal("4300.00"), "health_status": "PENDING"},
        {"farm": created_farms[0], "tag_id": "GV-007", "name": "Sita", "cattle_type": "COW", "breed": "Guernsey", "age_years": 3, "age_months": 32, "weight_lbs": 820, "price": Decimal("4150.00"), "health_status": "PENDING"},
        {"farm": created_farms[0], "tag_id": "GV-008", "name": "Rani", "cattle_type": "COW", "breed": "Ayrshire", "age_years": 2, "age_months": 18, "weight_lbs": 780, "price": Decimal("3550.00"), "health_status": "PENDING"},
        {"farm": created_farms[1], "tag_id": "SL-006", "name": "Nova", "cattle_type": "COW", "breed": "Jersey", "age_years": 1, "age_months": 14, "weight_lbs": 710, "price": Decimal("3050.00"), "health_status": "PENDING"},
        {"farm": created_farms[1], "tag_id": "SL-007", "name": "Kaira", "cattle_type": "COW", "breed": "Holstein Friesian", "age_years": 2, "age_months": 23, "weight_lbs": 900, "price": Decimal("4650.00"), "health_status": "PENDING"},
        {"farm": created_farms[1], "tag_id": "SL-008", "name": "Milan", "cattle_type": "BUFFALO", "breed": "Jaffarabadi", "age_years": 5, "age_months": 44, "weight_lbs": 1420, "price": Decimal("6100.00"), "health_status": "PENDING"},
        {"farm": created_farms[2], "tag_id": "NC-006", "name": "Ganga", "cattle_type": "COW", "breed": "Red Sindhi", "age_years": 3, "age_months": 27, "weight_lbs": 805, "price": Decimal("3450.00"), "health_status": "PENDING"},
        {"farm": created_farms[2], "tag_id": "NC-007", "name": "Veer", "cattle_type": "COW", "breed": "Tharparkar", "age_years": 4, "age_months": 36, "weight_lbs": 880, "price": Decimal("3950.00"), "health_status": "PENDING"},
        {"farm": created_farms[2], "tag_id": "NC-008", "name": "Zara", "cattle_type": "COW", "breed": "Sahiwal", "age_years": 2, "age_months": 16, "weight_lbs": 740, "price": Decimal("3150.00"), "health_status": "PENDING"},
    ]

    seeded_tag_ids = [c["tag_id"] for c in cattle_data]

    for cd in cattle_data:
        cattle, created = Cattle.objects.get_or_create(
            tag_id=cd["tag_id"],
            defaults={
                "farm": cd["farm"],
                "name": cd["name"],
                "cattle_type": cd["cattle_type"],
                "breed": cd["breed"],
                "age": cd["age_years"],
                "age_months": cd.get("age_months") or 0,
                "weight_lbs": cd["weight_lbs"],
                "price": cd["price"],
                "health_status": cd.get("health_status") or "HEALTHY",
                "is_for_sale": True,
                "sale_status": "available",
                "is_active": True,
            },
        )

        # Clear any previously generated demo images (keeps UI using "real" photos via template)
        if cattle.image:
            cattle.image = ""
            cattle.save(update_fields=["image"])

        tag = "CREATED" if created else "EXISTS"
        print(f"  {tag}: {cd['tag_id']} - {cd['name']} ({cd['breed']}) ${cd['price']}")

    # Also clear any images for the seeded items if they existed earlier
    Cattle.objects.filter(tag_id__in=seeded_tag_ids).exclude(image="").update(image="")

    print(f"\nDone! Total cattle for sale: {Cattle.objects.filter(is_for_sale=True).count()}")


if __name__ == "__main__":
    main()
