from django.contrib.auth.models import User
from django.db import models

class Farm(models.Model):
    farm_name = models.CharField(max_length=200, blank=True, default="")
    location = models.CharField(max_length=200, blank=True, default="")
    contact_number = models.CharField(max_length=20, blank=True, default="")
    registration_id = models.CharField(max_length=100, unique=True)
    cattle_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    ai_verified = models.BooleanField(default=False)
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.farm_name or f"Farm {self.id}"

    def __str__(self):
        return self.name    

    @property
    def name(self):
        return self.farm_name

    @name.setter
    def name(self, value):
        self.farm_name = value


class Breed(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class HealthCase(models.Model):
    SEVERITY_CHOICES = (
        ("LOW", "Low"),
        ("MEDIUM", "Medium"),
        ("HIGH", "High"),
        ("EMERGENCY", "Emergency"),
    )

    cattle = models.ForeignKey("Cattle", on_delete=models.CASCADE)
    reported_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    symptoms = models.TextField(blank=True, default="")
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default="LOW")
    ai_suggestion = models.CharField(max_length=255, blank=True, default="")
    vet = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_vet")
    vet_diagnosis = models.TextField(blank=True, default="")
    treatment_plan = models.TextField(blank=True, default="")
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Case for {self.cattle.tag_id}"


class report_health(models.Model):
    cattle = models.ForeignKey("Cattle", on_delete=models.CASCADE)
    symptoms = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report for {self.cattle.tag_id}"


class worker_login(models.Model):
    LANGUAGE_CHOICES = [
        ("en", "English"),
        ("hi", "Hindi"),
        ("ta", "Tamil"),
        ("ur", "Urdu"),
        ("ml", "Malayalam"),
        ("kn", "Kannada"),
    ]

    full_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, unique=True)
    preferred_language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES, default="en")
    photo = models.ImageField(upload_to="worker_photos/", blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} ({self.phone_number})"


class Emergency(models.Model):
    farm = models.ForeignKey("Farm", on_delete=models.CASCADE)
    alert_type = models.CharField(max_length=200)
    status = models.CharField(max_length=50, default="active")
    created_at = models.DateTimeField(auto_now_add=True)


class Vet(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    )

    name = models.CharField(max_length=200)
    license_number = models.CharField(max_length=100, unique=True)
    location = models.CharField(max_length=200, blank=True, default="")
    experience_years = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    email = models.EmailField(blank=True, default="")
    specialization = models.CharField(max_length=100, blank=True, default="")
    submitted_date = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def __str__(self):
        return self.name

    def __str__(self):
        return self.name


class EmergencyAlert(models.Model):
    PRIORITY_CHOICES = [
        ("high", "High"),
        ("medium", "Medium"),
        ("low", "Low"),
        ("resolved", "Resolved"),
    ]

    cattle = models.ForeignKey("Cattle", on_delete=models.CASCADE)
    farm = models.ForeignKey("Farm", on_delete=models.CASCADE)
    alert_type = models.CharField(max_length=200)
    ai_prediction = models.CharField(max_length=255, blank=True, default="")
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default="medium")
    is_assigned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.cattle.tag_id} - {self.alert_type}"

class EmergencyCases(models.Model):
    cattle_id = models.CharField(max_length=50)
    farm_name = models.CharField(max_length=100)
    description = models.TextField(blank=True, default="")
    severity = models.CharField(max_length=20, choices=[("Critical", "Critical"), ("Urgent", "Urgent"), ("Normal", "Normal")])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.cattle_id


class TreatmentReport(models.Model):
    cattle_id = models.CharField(max_length=50)
    diagnosis = models.TextField(blank=True, default="")
    status = models.CharField(max_length=20, choices=[("Resolved", "Resolved"), ("Ongoing", "Ongoing"), ("Done", "Done")])
    visit_date = models.DateField()

    def __str__(self):
        return self.cattle_id


class Customer(models.Model):
    PURPOSE_CHOICES = [
        ("Dairy Expansion", "Dairy Expansion"),
        ("Breeding", "Breeding"),
        ("Pedigree Breeding", "Pedigree Breeding"),
    ]
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Approved", "Approved"),
        ("Blocked", "Blocked"),
    ]
    RISK_LEVEL = [
        ("Low", "Low"),
        ("Medium", "Medium"),
        ("High", "High"),
    ]

    name = models.CharField(max_length=150)
    purpose = models.CharField(max_length=50, choices=PURPOSE_CHOICES, default="Dairy Expansion")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    risk_level = models.CharField(max_length=20, choices=RISK_LEVEL, default="Low")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class WorkerProfile(models.Model):
    LANGUAGE_CHOICES = [
        ("en", "English"),
        ("hi", "Hindi"),
        ("ml", "Malayalam"),
        ("ur", "Urdu"),
        ("ta", "Tamil"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    preferred_language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES, default="en")
    role = models.CharField(max_length=100,default="General Worker")
    approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} ({self.preferred_language})"


class CleaningRecord(models.Model):
    worker = models.ForeignKey(User, on_delete=models.CASCADE)
    area_cleaned = models.CharField(max_length=100)
    status = models.CharField(max_length=30, default="completed")
    created_at = models.DateTimeField(auto_now_add=True)


class Task(models.Model):
    worker = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class ActivityRecord(models.Model):
    worker = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    cattle = models.ForeignKey("Cattle", on_delete=models.SET_NULL, null=True, blank=True)
    activity = models.CharField(max_length=255)
    time = models.DateTimeField(auto_now_add=True)


class AIProductionPrediction(models.Model):
    cattle = models.ForeignKey("Cattle", on_delete=models.CASCADE)
    predicted_milk_liters = models.FloatField()
    feed_efficiency = models.IntegerField()
    nutrient_absorption = models.IntegerField()
    suggestion = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prediction for {self.cattle.tag_id}"


class CleaningLog(models.Model):
    AREA_CHOICES = [
        ("Stall", "Stall/Cubicle"),
        ("Milking", "Milking Parlor"),
        ("Feeding", "Feeding Trough"),
        ("Watering", "Watering System"),
        ("Quarantine", "Quarantine Zone"),
    ]
    METHOD_CHOICES = [
        ("Dry", "Dry Scrape"),
        ("Pressure", "Pressure Wash"),
        ("Steam", "Steam Clean"),
        ("Chemical", "Chemical Sanitize"),
    ]
    DISINFECTANT_CHOICES = [
        ("Chlorine", "Chlorine Based"),
        ("Iodine", "Iodine Based"),
        ("Peracetic", "Peracetic Acid"),
        ("Quaternary", "Quaternary Ammonium"),
    ]

    cattle = models.ForeignKey("Cattle", on_delete=models.CASCADE)
    worker = models.ForeignKey(User, on_delete=models.CASCADE)
    cleaning_time = models.TimeField()
    cleaning_area = models.CharField(max_length=50, choices=AREA_CHOICES)
    method = models.CharField(max_length=50, choices=METHOD_CHOICES)
    disinfectant = models.CharField(max_length=50, choices=DISINFECTANT_CHOICES)
    cross_contamination_check = models.BooleanField(default=False)
    deep_disinfection = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class AISanitationPrediction(models.Model):
    cattle = models.ForeignKey("Cattle", on_delete=models.CASCADE)
    health_risk_index = models.IntegerField()
    prevention_score = models.FloatField()
    pathogen_suppression = models.IntegerField()
    hygiene_longevity_hours = models.IntegerField()
    suggestion = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class IssueReport(models.Model):
    ISSUE_TYPE_CHOICES = [
        ("injury", "Physical Injury / Trauma"),
        ("illness", "Behavioral Illness / Fever"),
        ("infrastructure", "Fence or Water Break"),
        ("calving", "Emergency Calving"),
    ]
    SEVERITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("emergency", "Emergency"),
    ]

    cattle = models.ForeignKey("Cattle", on_delete=models.CASCADE, null=True, blank=True)
    reported_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    worker = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="worker_issue_reports")

    issue_type = models.CharField(max_length=50, choices=ISSUE_TYPE_CHOICES, blank=True, default="illness")
    voice_transcription = models.TextField(blank=True, default="")

    original_text = models.TextField(blank=True, default="")
    translated_text = models.TextField(blank=True, default="")
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, blank=True, default="low")

    selected_cattle = models.ManyToManyField("Cattle", blank=True, related_name="issue_reports")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Issue #{self.id}"


class EmergencyDispatch(models.Model):
    issue = models.OneToOneField(IssueReport, on_delete=models.CASCADE)
    vet = models.ForeignKey("Vet", on_delete=models.SET_NULL, null=True, blank=True)
    dispatch_id = models.CharField(max_length=20)
    eta_minutes = models.IntegerField(default=0)
    admin_notified = models.BooleanField(default=False)
    vet_notified = models.BooleanField(default=False)
    status = models.CharField(max_length=50, default="En Route")
    created_at = models.DateTimeField(auto_now_add=True)


class AISeverityAnalysis(models.Model):
    SEVERITY_LEVELS = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("emergency", "Emergency"),
    ]

    issue = models.OneToOneField(IssueReport, on_delete=models.CASCADE)
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS)
    confidence_score = models.FloatField(default=0)
    automatic_action_taken = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class Practitioner(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    application_id = models.CharField(max_length=20, unique=True)
    full_name = models.CharField(max_length=200)
    specialty = models.CharField(max_length=200)
    state = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    risk_level = models.CharField(max_length=20, default="Low")
    ai_confidence = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name


class VerificationDocument(models.Model):
    practitioner = models.ForeignKey("Practitioner", on_delete=models.CASCADE)
    document_type = models.CharField(max_length=100)
    file = models.FileField(upload_to="verification_docs/")
    uploaded_at = models.DateTimeField(auto_now_add=True)


class AIVerification(models.Model):
    practitioner = models.OneToOneField(Practitioner, on_delete=models.CASCADE)
    ocr_accuracy = models.FloatField(default=0)
    database_match = models.BooleanField(default=False)
    security_check_passed = models.BooleanField(default=False)
    extracted_license_number = models.CharField(max_length=50, blank=True, default="")
    extracted_expiry = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class AdminNote(models.Model):
    practitioner = models.ForeignKey("Practitioner", on_delete=models.CASCADE)
    admin = models.ForeignKey(User, on_delete=models.CASCADE)
    note = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class ActionHistory(models.Model):
    practitioner = models.ForeignKey("Practitioner", on_delete=models.CASCADE)
    action = models.CharField(max_length=200)
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)


class Reports(models.Model):
    vet = models.ForeignKey(User, on_delete=models.CASCADE)
    farm = models.ForeignKey("Farm", on_delete=models.CASCADE)
    cattle = models.ForeignKey("Cattle", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    findings = models.TextField(blank=True)

    def __str__(self):
        return f"Report {self.id}"


from django.db import models
from django.contrib.auth.models import User

class Diagnosis(models.Model):

    CONDITION_TYPES = [
        ('respiratory', 'Respiratory Distress'),
        ('digestive', 'Digestive / Bloat'),
        ('lameness', 'Lameness / Pododermatitis'),
        ('reproductive', 'Reproductive Health'),
        ('metabolic', 'Metabolic Disorder'),
    ]

    issue_report = models.ForeignKey(
        'IssueReport',
        on_delete=models.CASCADE,
        related_name='diagnoses'
    )

    cattle = models.ForeignKey(
        'Cattle',
        on_delete=models.CASCADE
    )

    observed_date = models.DateField()

    condition_category = models.CharField(
        max_length=50,
        choices=CONDITION_TYPES
    )

    observation_notes = models.TextField()

    prescription_file = models.FileField(
        upload_to='prescriptions/',
        blank=True,
        null=True
    )

    is_emergency = models.BooleanField(default=False)

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.cattle.tag_number} - {self.condition_category}"

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Vaccination(models.Model):

    VACCINE_TYPES = [
        ('brucellosis', 'Brucellosis Booster'),
        ('fmd', 'FMD Vaccine'),
        ('anthrax', 'Anthrax Shot'),
        ('hs', 'Hemorrhagic Septicemia'),
        ('bq', 'Black Quarter'),
    ]

    STATUS_CHOICES = [
        ('due_now', 'Due Now'),
        ('upcoming', 'Coming Soon'),
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
    ]

    cattle = models.ForeignKey(
        'Cattle',
        on_delete=models.CASCADE,
        related_name='vaccinations'
    )

    vaccine_type = models.CharField(
        max_length=50,
        choices=VACCINE_TYPES
    )

    due_date = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='upcoming'
    )

    ai_reason = models.TextField(blank=True, null=True)

    scheduled_date = models.DateField(blank=True, null=True)

    completed_date = models.DateField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.cattle.tag_number} - {self.vaccine_type}"
    

class RegionalAlert(models.Model):

    alert_type = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    severity_level = models.IntegerField(default=1)
    active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.alert_type} - {self.region}"
    
    

from django.db import models
from django.contrib.auth.models import User


class PurchaseRequest(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]

    buyer = models.ForeignKey(User, on_delete=models.CASCADE)
    cattle = models.ForeignKey('Cattle', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    ai_score = models.FloatField(default=0)  # For AI insights
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.buyer.username} - {self.cattle.name}"


class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cattle = models.ForeignKey('Cattle', on_delete=models.CASCADE)
    bid_amount = models.DecimalField(max_digits=10, decimal_places=2)
    placed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.cattle.name}"


from django.db import models
from django.contrib.auth.models import User


class UserVerification(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    verified_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.status}"



from django.db import models

class Cattle(models.Model):

    CATTLE_TYPE_CHOICES = [
        ("COW", "Cow"),
        ("BUFFALO", "Buffalo"),
    ]

    HEALTH_STATUS_CHOICES = [
        ("HEALTHY", "Healthy"),
        ("SICK", "Sick"),
        ("QUARANTINE", "Quarantine"),
        ("PENDING", "Pending"),
    ]

    SALE_STATUS_CHOICES = [
        ("available", "Available"),
        ("sold", "Sold"),
    ]

    # Farm Relation
    farm = models.ForeignKey("Farm", on_delete=models.CASCADE, related_name="cattles")

    # Identity
    tag_id = models.CharField(max_length=100, unique=True)
    tag_number = models.CharField(max_length=100, blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True)

    # Classification
    cattle_type = models.CharField(max_length=20, choices=CATTLE_TYPE_CHOICES, default="COW")
    species = models.CharField(max_length=50, blank=True, null=True)
    group = models.CharField(max_length=100, blank=True, null=True)
    breed = models.CharField(max_length=100, blank=True, null=True)

    # Physical Info
    age_months = models.IntegerField(default=0)
    weight_lbs = models.IntegerField(blank=True, null=True)
    age = models.PositiveIntegerField(default=0)

    # Health
    health_status = models.CharField(max_length=20, choices=HEALTH_STATUS_CHOICES, default="HEALTHY")
    is_sick = models.BooleanField(default=False)
    last_visit = models.DateField(blank=True, null=True)
    ai_alert = models.CharField(max_length=255, blank=True, null=True)

    # Marketplace
    is_for_sale = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    sale_status = models.CharField(max_length=20, choices=SALE_STATUS_CHOICES, default="available")
    is_active = models.BooleanField(default=True)
    image = models.ImageField(upload_to="cattle_images/", blank=True, null=True)

    # Purchase / provenance (admin-entered)
    purchased_from_name = models.CharField(max_length=200, blank=True, default="")
    purchased_from_contact = models.CharField(max_length=50, blank=True, default="")
    purchased_from_location = models.CharField(max_length=200, blank=True, default="")
    purchased_from_address = models.TextField(blank=True, default="")
    purchase_notes = models.TextField(blank=True, default="")
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="added_cattles")
    added_via = models.CharField(max_length=255, blank=True, default="")

    # System
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.tag_id


class AdminSettings(models.Model):
    """
    Singleton row (pk=1) for admin-configurable system credentials/settings.
    """

    id = models.PositiveSmallIntegerField(primary_key=True, default=1, editable=False)

    # Payment (used by payment_setup page)
    payee_name = models.CharField(max_length=200, blank=True, default="")
    upi_id = models.CharField(max_length=200, blank=True, default="")
    currency = models.CharField(max_length=10, blank=True, default="INR")
    bank_name = models.CharField(max_length=200, blank=True, default="")
    bank_account_number = models.CharField(max_length=50, blank=True, default="")
    bank_ifsc = models.CharField(max_length=50, blank=True, default="")

    # Basic contact (optional)
    support_email = models.EmailField(blank=True, default="")
    support_phone = models.CharField(max_length=50, blank=True, default="")

    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="admin_settings_updates")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Admin Settings"
    



class FeedingRecord(models.Model):

    FEED_TYPE_CHOICES = [
        ("Silage", "Silage (Corn/Grass)"),
        ("Concentrates", "Concentrates (Grain Mix)"),
        ("Roughage", "Roughage (Hay/Straw)"),
        ("Vitamins", "Vitamins & Additives"),
    ]

    cattle = models.ForeignKey('Cattle', on_delete=models.CASCADE)
    worker = models.ForeignKey(User, on_delete=models.CASCADE)

    feeding_time = models.TimeField()
    feed_type = models.CharField(max_length=50, choices=FEED_TYPE_CHOICES)
    quantity_kg = models.FloatField()
    status = models.CharField(max_length=30,default='completed')

    medication = models.BooleanField(default=False)
    quarantine_feed = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.cattle.tag_id} - {self.feed_type}"



class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cattle = models.ForeignKey('Cattle', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10,decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)

    STATUS_CHOICES = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled'),
        ],
        default='pending'
    )

    order_date = models.DateTimeField(auto_now_add=True)
    estimated_delivery_start = models.DateField()
    estimated_delivery_end = models.DateField()

    def __str__(self):
        return f"Order #{self.id}"



class PaymentSubmission(models.Model):

    METHOD_CHOICES = [
        ("UPI", "UPI"),
        ("BANK", "Bank Transfer"),
    ]

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("submitted", "Submitted"),
        ("verified", "Verified"),
        ("rejected", "Rejected"),
    ]

    order = models.OneToOneField("Order", on_delete=models.CASCADE, related_name="payment_submission")
    method = models.CharField(max_length=20, choices=METHOD_CHOICES, default="UPI")
    transaction_reference = models.CharField(max_length=120, blank=True, default="")
    receipt = models.FileField(upload_to="payment_receipts/", blank=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    submitted_at = models.DateTimeField(null=True, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    admin_notes = models.TextField(blank=True, default="")

    def __str__(self):
        return f"Payment for Order #{self.order_id} ({self.status})"


from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):

    ROLE_CHOICES = [
        ("ADMIN", "Admin"),
        ("VET", "Veterinarian"),
        ("WORKER", "Worker"),
        ("CUSTOMER", "Customer"),
    ]

    APPROVAL_STATUS = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    LANGUAGE_CHOICES = [
        ("en", "English"),
        ("hi", "Hindi"),
        ("ml", "Malayalam"),
        ("ur", "Urdu"),
        ("ta", "Tamil"),
    ]

    # Basic User Link
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Role System
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="CUSTOMER")

    # Farm Relation
    farm = models.ForeignKey(
        "Farm",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users"
    )

    # Approval System
    approval_status = models.CharField(
        max_length=20,
        choices=APPROVAL_STATUS,
        default="pending"
    )

    account_blocked = models.BooleanField(default=False)
    ai_verified = models.BooleanField(default=False)

    # Preferences
    preferred_language = models.CharField(
        max_length=5,
        choices=LANGUAGE_CHOICES,
        default="en"
    )

    # System Tracking
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"



from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile, UserVerification


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def create_user_verification(sender, instance, created, **kwargs):
    if created:
        UserVerification.objects.create(user=instance)


from django.db import models
from django.contrib.auth.models import User


class Worker(models.Model):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    submitted_date = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Buyer(models.Model):
    company_name = models.CharField(max_length=150)
    submitted_date = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.company_name


from django.db import models
from django.contrib.auth.models import User


# Newsletter Model
class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


# Buyer Profile
class BuyerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    approved = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


# Vet Profile
class VetProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    license_number = models.CharField(max_length=100, unique=True)
    license_document = models.FileField(upload_to="vet_licenses/", blank=True, null=True)
    location = models.CharField(max_length=200, blank=True, default="")
    approved = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
