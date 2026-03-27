import os
from datetime import timedelta

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Cattle_Farm.settings")

import django

django.setup()

from django.contrib.auth.models import User
from django.utils import timezone

from systemapp.models import Cattle, HealthCase, Vaccination


def main() -> None:
    user = User.objects.filter(is_staff=True).first() or User.objects.first()
    if not user:
        user = User.objects.create_user(username="demo_admin", password="demo12345")

    cattles = list(Cattle.objects.all().order_by("tag_id")[:8])
    if not cattles:
        print("No cattle found. Run cattle seeding first.")
        return

    # Pending cases
    pending_specs = [
        ("Reduced appetite, mild fever, low activity", "MEDIUM"),
        ("Coughing with nasal discharge", "LOW"),
        ("Sudden drop in milk yield and lethargy", "HIGH"),
    ]
    created_pending = 0
    for idx, (symptoms, severity) in enumerate(pending_specs):
        cattle = cattles[idx % len(cattles)]
        exists = HealthCase.objects.filter(cattle=cattle, symptoms=symptoms, is_resolved=False).exists()
        if exists:
            continue
        HealthCase.objects.create(
            cattle=cattle,
            reported_by=user,
            symptoms=symptoms,
            severity=severity,
            ai_suggestion="Monitor vitals and hydrate. Consider vet inspection." if severity != "LOW" else "Observe for 24h and keep isolated.",
            is_resolved=False,
        )
        created_pending += 1

    # Resolved cases
    resolved_specs = [
        ("Skin irritation near neck area", "Applied topical antiseptic; improving.", "LOW"),
        ("Minor hoof injury during grazing", "Cleaned wound and prescribed rest.", "MEDIUM"),
    ]
    created_resolved = 0
    for idx, (symptoms, diagnosis, severity) in enumerate(resolved_specs):
        cattle = cattles[(idx + 3) % len(cattles)]
        exists = HealthCase.objects.filter(cattle=cattle, symptoms=symptoms, is_resolved=True).exists()
        if exists:
            continue
        HealthCase.objects.create(
            cattle=cattle,
            reported_by=user,
            symptoms=symptoms,
            severity=severity,
            vet_diagnosis=diagnosis,
            treatment_plan=diagnosis,
            is_resolved=True,
        )
        created_resolved += 1

    # Vaccinations
    today = timezone.now().date()
    vac_specs = [
        ("fmd", today + timedelta(days=0), "due_now"),
        ("brucellosis", today + timedelta(days=5), "upcoming"),
        ("hs", today + timedelta(days=10), "upcoming"),
    ]
    created_vacc = 0
    for idx, (vtype, due, status) in enumerate(vac_specs):
        cattle = cattles[(idx + 5) % len(cattles)]
        exists = Vaccination.objects.filter(cattle=cattle, vaccine_type=vtype, due_date=due).exists()
        if exists:
            continue
        Vaccination.objects.create(
            cattle=cattle,
            vaccine_type=vtype,
            due_date=due,
            status=status,
            ai_reason="Seasonal risk in this region; recommended by AI monitoring.",
        )
        created_vacc += 1

    print(f"Seeded vet dashboard demo data: {created_pending} pending, {created_resolved} resolved, {created_vacc} vaccinations.")


if __name__ == "__main__":
    main()

