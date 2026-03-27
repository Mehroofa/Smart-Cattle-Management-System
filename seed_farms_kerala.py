import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Cattle_Farm.settings")

import django

django.setup()

from systemapp.models import Farm


def main() -> None:
    # Kerala-themed demo farms (unique registration IDs)
    farms_data = [
        ("Nila Dairy Estate", "Palakkad, Kerala", "9990010001", "FARM-KER-NILA-2026"),
        ("Kuttanad Cattle Haven", "Alappuzha, Kerala", "9990010002", "FARM-KER-KUTT-2026"),
        ("Malabar Meadows Farm", "Kozhikode, Kerala", "9990010003", "FARM-KER-MALA-2026"),
        ("Periyar Greens Livestock", "Idukki, Kerala", "9990010004", "FARM-KER-PERI-2026"),
        ("Vembanad Lakeview Dairy", "Kottayam, Kerala", "9990010005", "FARM-KER-VEMB-2026"),
        ("Wayanad Highland Dairy", "Wayanad, Kerala", "9990010006", "FARM-KER-WAYA-2026"),
        ("Anamudi Pastures", "Ernakulam, Kerala", "9990010007", "FARM-KER-ANAM-2026"),
        ("Pamba Valley Farm", "Pathanamthitta, Kerala", "9990010008", "FARM-KER-PAMB-2026"),
    ]

    created = 0
    for name, location, contact, reg_id in farms_data:
        farm, was_created = Farm.objects.get_or_create(
            registration_id=reg_id,
            defaults={
                "farm_name": name,
                "location": location,
                "contact_number": contact,
                "is_active": True,
                "ai_verified": True,
                "cattle_count": 80,
            },
        )
        if not was_created:
            # Keep existing values, but make sure it's active for demo.
            updates = {}
            if not farm.is_active:
                updates["is_active"] = True
            if farm.cattle_count == 0:
                updates["cattle_count"] = 80
            if updates:
                for k, v in updates.items():
                    setattr(farm, k, v)
                farm.save(update_fields=list(updates.keys()))
        else:
            created += 1

        print(f"{'CREATED' if was_created else 'EXISTS'}: {farm.farm_name} ({farm.location})")

    print(f"\nDone. Newly created farms: {created}")


if __name__ == "__main__":
    main()

