from django.shortcuts import render, redirect, get_object_or_404
from django.db import models
from .models import HealthCase, Farm, UserProfile
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
import hashlib

@login_required(login_url='/systemapp/vet_login/')
def diagnose_case(request, case_id):
    case = get_object_or_404(HealthCase, id=case_id)

    if request.method == 'POST':
        case.vet = request.user
        case.vet_diagnosis = request.POST.get('diagnosis')
        case.treatment_plan = request.POST.get('treatment')
        case.is_resolved = True
        case.save()
        return redirect('vet_dashboard')

    return render(request, 'systemapp/diagnose_case.html', {'case': case})


@login_required(login_url='/systemapp/vet_login/')
def health_case_detail(request, case_id):
    case = get_object_or_404(
        HealthCase.objects.select_related("cattle", "cattle__farm", "reported_by"),
        id=case_id,
    )
    return render(request, "systemapp/health_case_detail.html", {"case": case})


@login_required(login_url='/systemapp/vet_login/')
def vet_dashboard(request):
    from .models import VetProfile, Vaccination, Diagnosis, Farm
    # Ensure only approved vets can access
    try:
        vet_profile = VetProfile.objects.get(user=request.user)
        if not vet_profile.approved:
            messages.warning(request, "Your vet account is pending admin approval.")
            logout(request)
            return redirect('vet_login')
    except VetProfile.DoesNotExist:
        pass  # Allow superusers or other roles

    pending_cases = HealthCase.objects.filter(is_resolved=False).order_by('-created_at')
    resolved_cases = HealthCase.objects.filter(is_resolved=True).order_by('-created_at')[:5]
    total_farms = Farm.objects.count()
    total_cattle = Cattle.objects.count()
    pending_vaccinations_qs = Vaccination.objects.exclude(status='completed').order_by('due_date')
    pending_vaccinations = pending_vaccinations_qs.count()
    upcoming_vaccinations = pending_vaccinations_qs[:5]
    recent_diagnoses = Diagnosis.objects.order_by('-created_at')[:5]

    context = {
        'cases': pending_cases,
        'resolved_cases': resolved_cases,
        'total_farms': total_farms,
        'total_cattle': total_cattle,
        'pending_cases_count': pending_cases.count(),
        'resolved_cases_count': HealthCase.objects.filter(is_resolved=True).count(),
        'pending_vaccinations': pending_vaccinations,
        'upcoming_vaccinations': upcoming_vaccinations,
        'recent_diagnoses': recent_diagnoses,
    }
    return render(request, 'systemapp/vet_dashboard.html', context)

from .models import Cattle
@login_required(login_url='/systemapp/customer_login/')
def marketplace(request):
    return redirect('olx')

@login_required
def report_health(request):
    if request.method == "POST":
        # process form
        return redirect("portal")
    else:
    # This handles GET request
       return render(request, "systemapp/report_health.html")

def intro(request):
    return render(request, 'systemapp/front.html')

def get_started(request):
    return render(request, 'systemapp/get_started.html')

@login_required
def portal(request):
    return render(request, 'systemapp/portal.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            profile = UserProfile.objects.get(user=user)

            return redirect('portal')

        # if login fails
        return render(request, 'systemapp/login.html', {
            'error': 'Invalid credentials'
        })

    return render(request, 'systemapp/login.html')
from django.contrib.auth.decorators import login_required

@login_required
def marketplaces(request):
    return render(request, 'systemapp/marketplaces.html')

from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def front(request):
    return render(request, 'systemapp/front.html')
from django.shortcuts import render
from .models import Cattle, Breed, Farm

@login_required
def marketplaces(request):
    cattle = Cattle.objects.all()

    # FILTERS
    breed = request.GET.get('breed')
    location = request.GET.get('location')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    if breed:
        cattle = cattle.filter(breed__name=breed)

    if location:
        cattle = cattle.filter(farm__location=location)

    if min_price:
        cattle = cattle.filter(price__gte=min_price)

    if max_price:
        cattle = cattle.filter(price__lte=max_price)

    context = {
        "cattle_list": cattle,
        "breeds": Breed.objects.all(),   # ðŸ‘ˆ FROM ADMIN
        "farms": Farm.objects.all(),     # ðŸ‘ˆ FROM ADMIN
        "total_count": cattle.count()
    }

    return render(request, "systemapp/marketplaces.html", context)

@login_required
def add_cattle(request):
    farms = Farm.objects.all()
    context = {
        "farms": farms,
        "cattle_types": Cattle.CATTLE_TYPE_CHOICES,
        "health_statuses": Cattle.HEALTH_STATUS_CHOICES,
    }

    if request.method == 'POST':
        farm_id = request.POST.get('farm')
        farm = Farm.objects.filter(id=farm_id).first()
        if not farm:
            context['error'] = 'Please select a valid farm.'
            return render(request, "systemapp/add_cattle.html", context)

        tag_id = (request.POST.get('tag_id') or '').strip()
        cattle_type = request.POST.get('cattle_type')
        breed = (request.POST.get('breed') or '').strip()
        age_raw = request.POST.get('age')
        health_status = request.POST.get('health_status')
        is_for_sale = request.POST.get('is_for_sale') == 'on'
        price_raw = (request.POST.get('price') or '').strip()

        try:
            age = int(age_raw)
        except (TypeError, ValueError):
            context['error'] = 'Age must be a whole number.'
            return render(request, "systemapp/add_cattle.html", context)

        if age < 0:
            context['error'] = 'Age cannot be negative.'
            return render(request, "systemapp/add_cattle.html", context)

        if is_for_sale and not price_raw:
            context['error'] = 'Please provide a price when marking cattle for sale.'
            return render(request, "systemapp/add_cattle.html", context)

        price = price_raw if is_for_sale else None

        try:
            Cattle.objects.create(
                farm=farm,
                tag_id=tag_id,
                cattle_type=cattle_type,
                breed=breed,
                age=age,
                health_status=health_status,
                is_for_sale=is_for_sale,
                price=price,
            )
        except Exception:
            context['error'] = 'Unable to add cattle. Check fields and ensure Tag ID is unique.'
            return render(request, "systemapp/add_cattle.html", context)

        return redirect('marketplace')

    return render(request, "systemapp/add_cattle.html", context)

@login_required(login_url='/systemapp/vet_login/')
def vet_dash(request):
    return render(request, "systemapp/vet_dash.html")
def vet_login(request):
    from .models import VetProfile
    from django.conf import settings
    context = {}
    if request.method == 'POST':
        username = " ".join((request.POST.get('username', '') or '').split())
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is None and username:
            # Case-insensitive username fallback (helps when users type different casing).
            try:
                user_obj = User.objects.get(username__iexact=username)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                user = None
        if user is not None:
            # Check if this user has a VetProfile and if it is approved
            try:
                vet_profile = VetProfile.objects.get(user=user)
                if not vet_profile.approved:
                    auto_approve = bool(getattr(settings, "AUTO_APPROVE_VETS", False) or getattr(settings, "DEBUG", False))
                    if auto_approve:
                        vet_profile.approved = True
                        vet_profile.save(update_fields=["approved"])
                    else:
                        context['login_warning'] = 'Your account is pending admin approval. Please wait for the admin to approve your account before you can log in.'
                        return render(request, "systemapp/vet_login.html", context)
            except VetProfile.DoesNotExist:
                context['login_error'] = 'No vet profile found for this account. Please register first.'
                return render(request, "systemapp/vet_login.html", context)
            login(request, user)
            return redirect('vet_dashboard')
        else:
            context['login_error'] = 'Invalid username or password. Please try again.'
    return render(request, "systemapp/vet_login.html", context)

@login_required(login_url='/systemapp/vet_login/')
def medical(request, case_id=None):
    cases = HealthCase.objects.select_related('cattle', 'vet', 'reported_by').order_by('-created_at')
    if case_id is not None:
        case = get_object_or_404(cases, id=case_id)
    else:
        case = cases.filter(is_resolved=True).first() or cases.first()

    if not case:
        return render(request, "systemapp/medical.html", {"case": None})

    hash_seed = f"{case.id}:{case.cattle.tag_id}:{case.created_at.isoformat()}"
    validation_hash = hashlib.sha1(hash_seed.encode("utf-8")).hexdigest()[:12]
    is_verified = bool(case.is_resolved and case.vet_id)

    context = {
        "case": case,
        "is_verified": is_verified,
        "validation_hash": validation_hash,
    }
    return render(request, "systemapp/medical.html", context)

from deep_translator import GoogleTranslator

from django.shortcuts import render, redirect

@login_required
def report_health(request):
    from .models import Reports
    farm_id = request.GET.get('farm_id')
    cattle_id = request.GET.get('cattle_id')
    report_id = request.GET.get('report_id')

    cattle_list = Cattle.objects.all().order_by('tag_id')
    farm = None
    cattle_obj = None
    report = None

    if farm_id:
        farm = Farm.objects.filter(id=farm_id).first()
        if farm:
            cattle_list = Cattle.objects.filter(farm=farm).order_by('tag_id')
    if cattle_id:
        cattle_obj = Cattle.objects.filter(id=cattle_id).first()
    if report_id:
        report = Reports.objects.filter(id=report_id).first()

    if request.method == "POST":
        selected_cattle_id = request.POST.get('cattle')
        symptoms = request.POST.get('symptoms', '')
        if selected_cattle_id and symptoms:
            selected_cattle = Cattle.objects.filter(id=selected_cattle_id).first()
            if selected_cattle:
                HealthCase.objects.create(
                    cattle=selected_cattle,
                    reported_by=request.user,
                    symptoms=symptoms,
                    severity='MEDIUM',
                )
                messages.success(request, 'Health report submitted successfully.')
                return redirect('vet_dashboard')
        messages.error(request, 'Please select cattle and describe the symptoms.')

    context = {
        'cattle_list': cattle_list,
        'farm': farm,
        'cattle_obj': cattle_obj,
        'report': report,
    }
    return render(request, "systemapp/report_health.html", context)

def worker_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        selected_language = request.POST.get('language', 'en')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Save selected language to worker profile
            try:
                profile = WorkerProfile.objects.get(user=user)
                profile.preferred_language = selected_language
                profile.save()
            except WorkerProfile.DoesNotExist:
                pass
            request.session["django_language"] = selected_language
            return redirect('worker_dashboard')
        else:
            messages.error(request, 'Invalid credentials')
    return render(request, "systemapp/worker_login.html")

@login_required(login_url='/systemapp/vet_login/')
def vet_registration(request):
    return render(request, "systemapp/vet_registration.html")
@login_required(login_url='/systemapp/worker_login/')
def worker_reg(request):
    from .forms import WorkerRegistryForm
    from .models import worker_login as WorkerLogin

    if request.method == "POST":
        form = WorkerRegistryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Worker registered successfully.")
            return redirect("worker_reg")
        messages.error(request, "Please fix the errors and try again.")
    else:
        form = WorkerRegistryForm(initial={"is_active": True})

    recent_workers = WorkerLogin.objects.order_by("-created_at")[:5]
    return render(request, "systemapp/worker_reg.html", {"form": form, "recent_workers": recent_workers})


@login_required(login_url="/systemapp/worker_login/")
def worker_registry(request):
    from django.core.paginator import Paginator
    from .models import worker_login as WorkerLogin

    q = (request.GET.get("q") or "").strip()
    workers = WorkerLogin.objects.all().order_by("-created_at")
    if q:
        workers = workers.filter(models.Q(full_name__icontains=q) | models.Q(phone_number__icontains=q))

    paginator = Paginator(workers, 20)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(request, "systemapp/worker_registry.html", {"page_obj": page_obj, "q": q})
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages

def admin_login(request):
    context = {}
    if request.method == "POST":
        username_or_email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")

        # Try authenticate by username first, then by email
        user = authenticate(request, username=username_or_email, password=password)
        if user is None:
            # Try to find user by email
            try:
                email_user = User.objects.get(email=username_or_email)
                user = authenticate(request, username=email_user.username, password=password)
            except User.DoesNotExist:
                pass

        if user is not None:
            if user.is_superuser or user.is_staff:
                login(request, user)
                request.session['is_admin'] = True
                return redirect("admin_workplace")
            else:
                context['login_error'] = 'Access denied. You do not have administrator privileges.'
        else:
            context['login_error'] = 'Invalid username/email or password.'

    return render(request, "systemapp/admin_login.html", context)

from .models import Farm, Cattle, Emergency

@login_required(login_url='/systemapp/admin_login/')
def admin_overview(request):
    if not (request.user.is_superuser or request.user.is_staff):
        return redirect('admin_login')
    total_farms = Farm.objects.count()
    total_cattle = Cattle.objects.count()
    total_alerts = Emergency.objects.filter(status="active").count()

    recent_alerts = Emergency.objects.all().order_by('-created_at')[:5]

    return render(request, 'systemapp/admin_overview.html', {
        'total_farms': total_farms,
        'total_cattle': total_cattle,
        'total_alerts': total_alerts,
        'recent_alerts': recent_alerts,
    })
from .models import Cattle

@login_required(login_url='/systemapp/admin_login/')
def cattle_approval(request):
    if not (request.user.is_superuser or request.user.is_staff):
        return redirect('admin_login')

    q = (request.GET.get("q") or "").strip()
    pending_cattle = Cattle.objects.filter(health_status='PENDING').order_by("-created_at")
    if q:
        pending_cattle = pending_cattle.filter(tag_id__icontains=q)

    return render(request, 'systemapp/cattle_approval.html', {
        'pending_cattle': pending_cattle,
        'pending_count': pending_cattle.count(),
        'q': q,
    })


@login_required(login_url="/systemapp/admin_login/")
def admin_add_cattle(request):
    from .forms import AdminCattleAddForm

    if not (request.user.is_superuser or request.user.is_staff):
        return redirect("admin_login")

    if request.method == "POST":
        form = AdminCattleAddForm(request.POST, request.FILES)
        if form.is_valid():
            cattle = form.save(commit=False)
            cattle.added_by = request.user
            cattle.added_via = request.path
            if cattle.age_months and not cattle.age:
                cattle.age = cattle.age_months // 12
            if not cattle.health_status:
                cattle.health_status = "PENDING"
            cattle.save()
            messages.success(request, f"{cattle.tag_id} added successfully.")
            return redirect("admin_cattle_added", cattle_id=cattle.id)
        messages.error(request, "Please fix the errors and try again.")
    else:
        form = AdminCattleAddForm(initial={"health_status": "PENDING"})

    return render(request, "systemapp/admin_add_cattle.html", {"form": form})


@login_required(login_url="/systemapp/admin_login/")
def admin_cattle_added(request, cattle_id):
    if not (request.user.is_superuser or request.user.is_staff):
        return redirect("admin_login")

    cattle = get_object_or_404(Cattle, id=cattle_id)
    return render(request, "systemapp/admin_cattle_added.html", {"cattle": cattle})


@login_required(login_url="/systemapp/admin_login/")
def admin_settings(request):
    from django.contrib.auth import update_session_auth_hash
    from .forms import AdminPasswordChangeForm, AdminSettingsForm
    from .models import AdminSettings

    if not (request.user.is_superuser or request.user.is_staff):
        return redirect("admin_login")

    settings_obj, _ = AdminSettings.objects.get_or_create(pk=1)

    if request.method == "POST":
        action = (request.POST.get("action") or "").strip()

        if action == "save_settings":
            settings_form = AdminSettingsForm(request.POST, instance=settings_obj)
            password_form = AdminPasswordChangeForm(request.user)
            if settings_form.is_valid():
                updated = settings_form.save(commit=False)
                updated.updated_by = request.user
                updated.save()
                messages.success(request, "Settings saved.")
                return redirect("admin_settings")
            messages.error(request, "Please fix the settings errors.")
            return render(request, "systemapp/admin_settings.html", {"settings_form": settings_form, "password_form": password_form})

        if action == "change_password":
            settings_form = AdminSettingsForm(instance=settings_obj)
            password_form = AdminPasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Password updated.")
                return redirect("admin_settings")
            messages.error(request, "Please fix the password errors.")
            return render(request, "systemapp/admin_settings.html", {"settings_form": settings_form, "password_form": password_form})

        messages.error(request, "Invalid action.")
        return redirect("admin_settings")

    settings_form = AdminSettingsForm(instance=settings_obj)
    password_form = AdminPasswordChangeForm(request.user)
    return render(request, "systemapp/admin_settings.html", {"settings_form": settings_form, "password_form": password_form})


@login_required(login_url="/systemapp/admin_login/")
def approve_cattle(request, cattle_id):
    if not (request.user.is_superuser or request.user.is_staff):
        return redirect("admin_login")

    cattle = get_object_or_404(Cattle, id=cattle_id)
    if request.method == "POST":
        cattle.health_status = "HEALTHY"
        cattle.is_active = True
        cattle.save(update_fields=["health_status", "is_active"])
        messages.success(request, f"{cattle.tag_id} approved.")
        return redirect("cattle_approved", cattle_id=cattle.id)
    return redirect("cattle_approval")


@login_required(login_url="/systemapp/admin_login/")
def reject_cattle(request, cattle_id):
    if not (request.user.is_superuser or request.user.is_staff):
        return redirect("admin_login")

    cattle = get_object_or_404(Cattle, id=cattle_id)
    if request.method == "POST":
        cattle.health_status = "SICK"
        cattle.is_for_sale = False
        cattle.is_active = False
        cattle.save(update_fields=["health_status", "is_for_sale", "is_active"])
        messages.success(request, f"{cattle.tag_id} rejected.")
        return redirect("cattle_rejected", cattle_id=cattle.id)
    return redirect("cattle_approval")


@login_required(login_url="/systemapp/admin_login/")
def cattle_approved(request, cattle_id):
    if not (request.user.is_superuser or request.user.is_staff):
        return redirect("admin_login")

    cattle = get_object_or_404(Cattle, id=cattle_id)
    return render(request, "systemapp/cattle_approved.html", {"cattle": cattle})


@login_required(login_url="/systemapp/admin_login/")
def cattle_rejected(request, cattle_id):
    if not (request.user.is_superuser or request.user.is_staff):
        return redirect("admin_login")

    cattle = get_object_or_404(Cattle, id=cattle_id)
    return render(request, "systemapp/cattle_rejected.html", {"cattle": cattle})



from .models import Vet
from django.shortcuts import render, redirect, get_object_or_404

@login_required(login_url='/systemapp/admin_login/')
def vet_approval(request):
    pending_vets = Vet.objects.filter(status='pending')
    pending_count = pending_vets.count()

    return render(request, 'systemapp/vet_approval.html', {
        'pending_vets': pending_vets,
        'pending_count': pending_count,
    })

from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Cattle


@login_required(login_url='/systemapp/customer_login/')
def olx(request):
    query = (request.GET.get("q") or "").strip()
    breed = (request.GET.get("breed") or "").strip()
    location = (request.GET.get("location") or "").strip()
    price_range = (request.GET.get("price") or "").strip()

    base_qs = Cattle.objects.filter(is_for_sale=True).select_related("farm")
    cattle_qs = base_qs

    if query:
        # Keep text-search focused so "jersey" does not return unrelated breeds.
        cattle_qs = cattle_qs.filter(
            Q(tag_id__icontains=query)
            | Q(breed__icontains=query)
        )

    if breed:
        cattle_qs = cattle_qs.filter(breed__iexact=breed)

    if location:
        cattle_qs = cattle_qs.filter(farm__location__iexact=location)

    if price_range == "0-1500":
        cattle_qs = cattle_qs.filter(price__gte=0, price__lte=1500)
    elif price_range == "1500-3000":
        cattle_qs = cattle_qs.filter(price__gt=1500, price__lte=3000)
    elif price_range == "3000+":
        cattle_qs = cattle_qs.filter(price__gt=3000)

    cattle_qs = cattle_qs.order_by("-id")
    paginator = Paginator(cattle_qs, 8)
    page_obj = paginator.get_page(request.GET.get("page"))

    breed_options = (
        base_qs.exclude(breed="")
        .values_list("breed", flat=True)
        .distinct()
        .order_by("breed")
    )
    location_options = (
        base_qs.exclude(farm__location="")
        .values_list("farm__location", flat=True)
        .distinct()
        .order_by("farm__location")
    )

    applied_filters = []
    if query:
        applied_filters.append(f"Search: {query}")
    if breed:
        applied_filters.append(f"{breed} Breed")
    if price_range == "0-1500":
        applied_filters.append("$0 - $1500")
    elif price_range == "1500-3000":
        applied_filters.append("$1500 - $3000")
    elif price_range == "3000+":
        applied_filters.append("$3000+")
    if location:
        applied_filters.append(location)

    context = {
        "cattle_list": page_obj.object_list,
        "page_obj": page_obj,
        "total_count": base_qs.count(),
        "shown_count": page_obj.end_index() if page_obj.paginator.count else 0,
        "q": query,
        "breed": breed,
        "location": location,
        "price": price_range,
        "breed_options": breed_options,
        "location_options": location_options,
        "applied_filters": applied_filters,
    }
    return render(request, "systemapp/olx.html", context)

from django.shortcuts import render, redirect, get_object_or_404
from .models import EmergencyAlert


@login_required(login_url='/systemapp/admin_login/')
def alert_view(request):
    alerts = EmergencyAlert.objects.select_related('cattle', 'farm').all()

    return render(request, 'systemapp/alerts.html', {
        'alerts': alerts
    })


@login_required(login_url='/systemapp/admin_login/')
def assign_vet(request, alert_id):
    alert = get_object_or_404(EmergencyAlert, id=alert_id)
    alert.is_assigned = True
    alert.save()

    return redirect('alert_page')

from django.shortcuts import render
from .models import EmergencyCases, TreatmentReport


@login_required(login_url='/systemapp/vet_login/')
def vet_cases(request):
    emergency_cases = EmergencyCases.objects.all().order_by('-created_at')
    reports = TreatmentReport.objects.all().order_by('-visit_date')

    return render(request, 'systemapp/vet_cases.html', {
        'emergency_cases': emergency_cases,
        'reports': reports
    })
from django.shortcuts import render, redirect, get_object_or_404
from .models import Customer

@login_required(login_url='/systemapp/admin_login/')
def customer_approval(request):

    customers = Customer.objects.filter(status="Pending")

    total_pending = customers.count()
    total_flagged = Customer.objects.filter(risk_level="High", status="Pending").count()
    total_approved = Customer.objects.filter(status="Approved").count()

    context = {
        'customers': customers,
        'total_pending': total_pending,
        'total_flagged': total_flagged,
        'total_approved': total_approved,
    }

    return render(request, 'systemapp/customer_approval.html', context)

@login_required(login_url='/systemapp/admin_login/')
def approve_customer(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    customer.status = "Approved"
    customer.save()
    return redirect('customer_approval')
@login_required(login_url='/systemapp/admin_login/')
def block_customer(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    customer.status = "Blocked"
    customer.save()
    return redirect('customer_approval')


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import translation
from django.http import JsonResponse
from .models import FeedingRecord, CleaningRecord, IssueReport, WorkerProfile, Cattle


# Worker Dashboard
@login_required(login_url='/systemapp/worker_login/')
def worker_dashboard(request):

    # Activate worker preferred language
    try:
        profile = WorkerProfile.objects.get(user=request.user)
        translation.activate(profile.preferred_language)
        request.session["django_language"] = profile.preferred_language
    except WorkerProfile.DoesNotExist:
        pass

    return render(request, 'systemapp/worker_dashboard.html')


@login_required(login_url='/systemapp/worker_login/')
def set_worker_language(request):
    if request.method != "POST":
        return JsonResponse({"ok": False, "error": "Invalid request method"}, status=405)

    language = request.POST.get("language", "").strip()
    allowed_languages = {"en", "hi", "ml", "ur", "ta"}

    if language not in allowed_languages:
        return JsonResponse({"ok": False, "error": "Unsupported language"}, status=400)

    WorkerProfile.objects.update_or_create(
        user=request.user,
        defaults={"preferred_language": language},
    )

    translation.activate(language)
    request.session["django_language"] = language

    return JsonResponse({"ok": True, "language": language})


# Worker Copilot (AI chat)
@login_required(login_url='/systemapp/worker_login/')
def worker_copilot(request):
    from .ai_logic import worker_copilot_reply

    allowed_languages = {"en", "hi", "ml", "ur", "ta"}

    try:
        profile = WorkerProfile.objects.get(user=request.user)
        default_language = profile.preferred_language or "en"
    except WorkerProfile.DoesNotExist:
        default_language = "en"

    selected_language = request.session.get("django_language") or default_language
    if selected_language not in allowed_languages:
        selected_language = "en"

    if request.GET.get("reset") == "1":
        request.session.pop("worker_copilot_history", None)

    history = request.session.get("worker_copilot_history") or []

    if request.method == "POST":
        # Fallback: if JS isn't available, allow POSTed language for this reply.
        posted_language = (request.POST.get("language") or "").strip()
        if posted_language in allowed_languages:
            selected_language = posted_language

        message = (request.POST.get("message") or "").strip()
        if message:
            history.append({"role": "user", "content": message})
            reply = worker_copilot_reply(message, language=selected_language)
            history.append({"role": "assistant", "content": reply})
            history = history[-20:]
            request.session["worker_copilot_history"] = history

    return render(request, "systemapp/worker_copilot.html", {
        "history": history,
        "language": selected_language,
    })


# Update Feeding
@login_required(login_url='/systemapp/worker_login/')
def update_feeding(request):
    if request.method == "POST":
        cattle_id = request.POST.get('cattle')
        feed_type = request.POST.get('feed_type')
        quantity = request.POST.get('quantity')
        feeding_time = request.POST.get('feeding_time')
        cattle = Cattle.objects.get(id=cattle_id)

        FeedingRecord.objects.create(
            cattle=cattle,
            worker=request.user,
            feed_type=feed_type,
            quantity_kg=quantity_kg,
            status="completed",
            medication=False,
            feeding_time=feeding_time,
            quarantine_feed=False,
        ) 

        return redirect('worker_dashboard')

    return redirect('feeding_status')


# Update Cleaning
@login_required(login_url='/systemapp/worker_login/')
def update_cleaning(request):
    if request.method == "POST":
        area = request.POST.get('area')

        CleaningRecord.objects.create(
            worker=request.user,
            area_cleaned=area,
            status="completed"
        )

        return redirect('worker_dashboard')

    return redirect('cleaning_status')


# AI Severity Logic (Simple Example)
def detect_severity(text):
    text = text.lower()

    if "bleeding" in text or "not breathing" in text:
        return "emergency"
    elif "fever" in text or "infection" in text:
        return "high"
    elif "not eating" in text:
        return "medium"
    else:
        return "low"


# Report Issue
@login_required(login_url='/systemapp/worker_login/')
def report_issue(request):
    if request.method == "POST":
        cattle_id = request.POST.get('cattle')
        description = request.POST.get('description')

        cattle = Cattle.objects.get(id=cattle_id)

        severity = detect_severity(description)

        IssueReport.objects.create(
            cattle=cattle,
            worker=request.user,
            original_text=description,
            translated_text=description,  # replace with actual translation API
            severity=severity
        )

        # If emergency â†’ call nearby vet logic here

        return redirect('worker_dashboard')

    return redirect('AI_issue_reporting')

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Task, Cattle, ActivityRecord


@login_required(login_url='/systemapp/worker_login/')
def language_translation(request):

    worker = request.user

    tasks = Task.objects.filter(worker=worker)
    total_cattle = Cattle.objects.count()

    completed_tasks = tasks.filter(is_completed=True).count()
    total_tasks = tasks.count()

    recent_records = ActivityRecord.objects.order_by('-time')[:5]

    urgent_alert = Cattle.objects.filter(is_sick=True).first()

    context = {
        'tasks': tasks,
        'total_cattle': total_cattle,
        'completed_tasks': completed_tasks,
        'total_tasks': total_tasks,
        'recent_records': recent_records,
        'urgent_alert': urgent_alert,
    }

    return render(request, 'systemapp/language_translation.html', context)

def generate_prediction(quantity):
    base_yield = 20

    predicted = base_yield + (quantity * 1.2)

    efficiency = min(95, int(quantity * 10))
    absorption = min(98, int(quantity * 12))

    suggestion = "Increase Silage by 1.5kg to boost production by 5%."

    return predicted, efficiency, absorption, suggestion

from django.shortcuts import render, redirect, get_object_or_404
from .models import Cattle, FeedingRecord, AIProductionPrediction, WorkerProfile
from django.contrib.auth.decorators import login_required
from django.urls import reverse


@login_required(login_url='/systemapp/worker_login/')
def feeding_status(request):
    # Keep feeding page language aligned with worker preference.
    try:
        profile = WorkerProfile.objects.get(user=request.user)
        translation.activate(profile.preferred_language)
        request.session["django_language"] = profile.preferred_language
    except WorkerProfile.DoesNotExist:
        pass

    cattle_list = Cattle.objects.all().order_by("tag_id")

    if request.method == "POST":
        cattle_tag_id = (request.POST.get("cattle_id") or "").strip()
        feeding_time = request.POST.get("feeding_time")
        feed_type = request.POST.get("feed_type")
        quantity_raw = request.POST.get("quantity")

        if not cattle_tag_id or not feeding_time or not feed_type or not quantity_raw:
            return render(request, "systemapp/feeding_status.html", {
                "cattle_list": cattle_list,
                "prediction": None,
                "form_error": "Please fill all required fields before saving.",
            })

        try:
            quantity = float(quantity_raw)
        except (TypeError, ValueError):
            return render(request, "systemapp/feeding_status.html", {
                "cattle_list": cattle_list,
                "prediction": None,
                "form_error": "Quantity must be a valid number.",
            })

        if quantity <= 0:
            return render(request, "systemapp/feeding_status.html", {
                "cattle_list": cattle_list,
                "prediction": None,
                "form_error": "Quantity must be greater than zero.",
            })

        medication = request.POST.get("medication") == "on"
        quarantine = request.POST.get("quarantine") == "on"
        notes = request.POST.get("notes")

        cattle = get_object_or_404(Cattle, tag_id=cattle_tag_id)

        FeedingRecord.objects.create(
            cattle=cattle,
            worker=request.user,
            feeding_time=feeding_time,
            feed_type=feed_type,
            quantity_kg=quantity,
            medication=medication,
            quarantine_feed=quarantine,
            notes=notes
        )

        predicted, efficiency, absorption, suggestion = generate_prediction(quantity)

        prediction = AIProductionPrediction.objects.create(
            cattle=cattle,
            predicted_milk_liters=predicted,
            feed_efficiency=efficiency,
            nutrient_absorption=absorption,
            suggestion=suggestion
        )

        redirect_url = f"{reverse('feeding_status')}?saved=1&prediction_id={prediction.id}"
        return redirect(redirect_url)

    prediction_id = request.GET.get("prediction_id")
    prediction = None
    if prediction_id:
        prediction = AIProductionPrediction.objects.filter(id=prediction_id).select_related("cattle").first()

    context = {
        "cattle_list": cattle_list,
        "prediction": prediction,
        "saved": request.GET.get("saved") == "1",
    }
    return render(request, "systemapp/feeding_status.html", context)

def generate_sanitation_prediction(method, disinfectant, deep_cycle):

    base_risk = 50

    # Method impact
    if method == "Steam":
        base_risk -= 25
    elif method == "Pressure":
        base_risk -= 15
    elif method == "Chemical":
        base_risk -= 20
    else:
        base_risk -= 10

    # Disinfectant strength
    if disinfectant == "Peracetic":
        base_risk -= 20
    elif disinfectant == "Chlorine":
        base_risk -= 15
    elif disinfectant == "Iodine":
        base_risk -= 10

    # Deep disinfection bonus
    if deep_cycle:
        base_risk -= 15

    health_risk = max(5, base_risk)

    prevention_score = 100 - health_risk
    pathogen_suppression = min(98, prevention_score + 2)
    hygiene_longevity = int(prevention_score * 0.75)

    suggestion = "Humidity control optimization may reduce mastitis risk by 3%."

    return health_risk, prevention_score, pathogen_suppression, hygiene_longevity, suggestion

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import CleaningLog, AISanitationPrediction, Cattle, WorkerProfile


@login_required(login_url='/systemapp/worker_login/')
def cleaning_status(request):
    try:
        profile = WorkerProfile.objects.get(user=request.user)
        translation.activate(profile.preferred_language)
        request.session["django_language"] = profile.preferred_language
    except WorkerProfile.DoesNotExist:
        pass

    cattle_list = Cattle.objects.all().order_by("tag_id")

    if request.method == "POST":
        cattle_tag_id = (request.POST.get("cattle_id") or "").strip()
        cleaning_time = request.POST.get("cleaning_time")
        area = request.POST.get("cleaning_area")
        method = request.POST.get("method")
        disinfectant = request.POST.get("disinfectant")

        if not cattle_tag_id or not cleaning_time or not area or not method or not disinfectant:
            return render(request, "systemapp/cleaning_status.html", {
                "cattle_list": cattle_list,
                "prediction": None,
                "form_error": "Please fill all required fields before saving.",
            })

        cross_check = request.POST.get("cross_check") == "on"
        deep_cycle = request.POST.get("deep_cycle") == "on"
        notes = request.POST.get("notes")

        cattle = get_object_or_404(Cattle, tag_id=cattle_tag_id)

        CleaningLog.objects.create(
            cattle=cattle,
            worker=request.user,
            cleaning_time=cleaning_time,
            cleaning_area=area,
            method=method,
            disinfectant=disinfectant,
            cross_contamination_check=cross_check,
            deep_disinfection=deep_cycle,
            notes=notes
        )

        health_risk, prevention_score, suppression, longevity, suggestion = generate_sanitation_prediction(
            method, disinfectant, deep_cycle
        )

        prediction = AISanitationPrediction.objects.create(
            cattle=cattle,
            health_risk_index=health_risk,
            prevention_score=prevention_score,
            pathogen_suppression=suppression,
            hygiene_longevity_hours=longevity,
            suggestion=suggestion
        )

        redirect_url = f"{reverse('cleaning_status')}?saved=1&prediction_id={prediction.id}"
        return redirect(redirect_url)

    prediction_id = request.GET.get("prediction_id")
    prediction = None
    if prediction_id:
        prediction = AISanitationPrediction.objects.filter(id=prediction_id).select_related("cattle").first()

    context = {
        "cattle_list": cattle_list,
        "prediction": prediction,
        "saved": request.GET.get("saved") == "1",
    }
    return render(request, "systemapp/cleaning_status.html", context)


def analyze_severity(transcription):

    text = transcription.lower()

    if "bleeding" in text or "unable to stand" in text:
        return "emergency", 0.95

    elif "deep cut" in text or "fracture" in text:
        return "high", 0.85

    elif "fever" in text or "not eating" in text:
        return "medium", 0.75

    else:
        return "low", 0.60


from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import IssueReport, WorkerProfile,AISeverityAnalysis, EmergencyDispatch, Cattle, Vet
import random


@login_required(login_url='/systemapp/worker_login/')
def AI_issue_reporting(request):
    try:
        profile = WorkerProfile.objects.get(user=request.user)
        translation.activate(profile.preferred_language)
        request.session["django_language"] = profile.preferred_language
    except WorkerProfile.DoesNotExist:
        pass

    severity_analysis = None
    dispatch = None
    form_error = None
    cattle_list = Cattle.objects.all().order_by("tag_id")

    if request.method == "POST":

        cattle_tag_id = (request.POST.get("cattle_id") or "").strip()
        issue_type = (request.POST.get("issue_type") or "").strip()
        transcription = (request.POST.get("voice_transcription") or "").strip()

        if not cattle_tag_id or not issue_type or not transcription:
            form_error = "Please select cattle, choose issue category, and provide transcription."
            return render(request, "systemapp/AI_issue_reporting.html", {
                "analysis": severity_analysis,
                "dispatch": dispatch,
                "form_error": form_error,
                "cattle_list": cattle_list,
            })

        cattle = get_object_or_404(Cattle, tag_id=cattle_tag_id)

        issue = IssueReport.objects.create(
            cattle=cattle,
            reported_by=request.user,
            issue_type=issue_type,
            voice_transcription=transcription
        )

        # AI Analysis
        severity, confidence = analyze_severity(transcription)

        severity_analysis = AISeverityAnalysis.objects.create(
            issue=issue,
            severity=severity,
            confidence_score=confidence,
            automatic_action_taken=(severity in ["high", "emergency"])
        )

        # If emergency â†’ auto dispatch
        if severity in ["high", "emergency"]:

            nearest_vet = Vet.objects.first()  # later can calculate nearest
            dispatch_id = f"EM-{random.randint(1000,9999)}"

            dispatch = EmergencyDispatch.objects.create(
                issue=issue,
                vet=nearest_vet,
                dispatch_id=dispatch_id,
                eta_minutes=random.randint(5, 15),
                admin_notified=True,
                vet_notified=True,
                status="En Route"
            )

    return render(request, "systemapp/AI_issue_reporting.html", {
        "analysis": severity_analysis,
        "dispatch": dispatch,
        "form_error": form_error,
        "cattle_list": cattle_list,
    })

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Practitioner, AIVerification, AdminNote, ActionHistory


@login_required
def AI_verification_vet(request, pk):

    practitioner = get_object_or_404(Practitioner, id=pk)
    ai_data = AIVerification.objects.filter(practitioner=practitioner).first()
    notes = AdminNote.objects.filter(practitioner=practitioner).order_by('-created_at')
    history = ActionHistory.objects.filter(practitioner=practitioner).order_by('-timestamp')

    return render(request, "systemapp/AI_verification_vet.html", {
        "practitioner": practitioner,
        "ai_data": ai_data,
        "notes": notes,
        "history": history,
    })
@login_required
def approve_practitioner(request, pk):
    if request.method != "POST":
        return redirect("AI_verification_vet", pk=pk)

    practitioner = get_object_or_404(Practitioner, id=pk)
    practitioner.status = "approved"
    practitioner.save()

    ActionHistory.objects.create(
        practitioner=practitioner,
        action="Registration Approved",
        performed_by=request.user
    )

    return redirect("AI_verification_vet", pk=pk)
@login_required
def reject_practitioner(request, pk):
    if request.method != "POST":
        return redirect("AI_verification_vet", pk=pk)

    practitioner = get_object_or_404(Practitioner, id=pk)
    practitioner.status = "rejected"
    practitioner.save()

    ActionHistory.objects.create(
        practitioner=practitioner,
        action="Registration Rejected",
        performed_by=request.user
    )

    return redirect("AI_verification_vet", pk=pk)

@login_required
def clarify_practitioner(request, pk):
    if request.method != "POST":
        return redirect("AI_verification_vet", pk=pk)

    practitioner = get_object_or_404(Practitioner, id=pk)
    practitioner.status = "pending"
    practitioner.save()

    ActionHistory.objects.create(
        practitioner=practitioner,
        action="Clarification Requested",
        performed_by=request.user
    )

    return redirect("AI_verification_vet", pk=pk)

@login_required
def add_admin_note(request, pk):

    practitioner = get_object_or_404(Practitioner, id=pk)

    if request.method == "POST":
        note_text = (request.POST.get("note") or "").strip()
        if not note_text:
            return redirect("AI_verification_vet", pk=pk)

        AdminNote.objects.create(
            practitioner=practitioner,
            admin=request.user,
            note=note_text
        )

        ActionHistory.objects.create(
            practitioner=practitioner,
            action="Admin Added Note",
            performed_by=request.user
        )

    return redirect("AI_verification_vet", pk=pk)

from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.urls import reverse
from .models import Farm, Cattle, Reports


@login_required(login_url='/systemapp/vet_login/')
def select_farms(request):
    query = (request.GET.get("q") or "").strip()
    sort = request.GET.get("sort", "nearest")
    herd_size = request.GET.get("herd", "")
    ai_pending = request.GET.get("ai_pending") == "1"

    farms_qs = Farm.objects.annotate(
        cattle_count=Count("cattle", distinct=True),
        ai_pending_count=Count(
            "cattle__healthcase",
            filter=Q(cattle__healthcase__is_resolved=False),
            distinct=True,
        ),
    ).filter(cattle_count__gt=0)

    if query:
        farms_qs = farms_qs.filter(
            Q(farm_name__icontains=query)
            | Q(location__icontains=query)
            | Q(contact_number__icontains=query)
            | Q(id__icontains=query)
        )

    if herd_size == "small":
        farms_qs = farms_qs.filter(cattle_count__lt=100)
    elif herd_size == "medium":
        farms_qs = farms_qs.filter(cattle_count__gte=100, cattle_count__lte=250)
    elif herd_size == "large":
        farms_qs = farms_qs.filter(cattle_count__gt=250)

    if ai_pending:
        farms_qs = farms_qs.filter(ai_pending_count__gt=0)

    if sort == "name":
        farms_qs = farms_qs.order_by("farm_name")
    elif sort == "herd_desc":
        farms_qs = farms_qs.order_by("-cattle_count", "farm_name")
    else:
        farms_qs = farms_qs.order_by("id")

    paginator = Paginator(farms_qs, 6)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "farms": page_obj.object_list,
        "page_obj": page_obj,
        "total_count": farms_qs.count(),
        "q": query,
        "sort": sort,
        "herd": herd_size,
        "ai_pending": ai_pending,
    }
    return render(request, "systemapp/select_farms.html", context)


@login_required(login_url='/systemapp/vet_login/')
def select_cattle(request, farm_id):
    farm = get_object_or_404(Farm, id=farm_id)
    query = (request.GET.get("q") or "").strip()
    species = (request.GET.get("species") or "").strip()
    health = (request.GET.get("health") or "").strip()
    selected_id = request.GET.get("selected")
    select_all = request.GET.get("select_all") == "1"

    cattle_qs = Cattle.objects.filter(farm=farm).order_by("tag_id")
    if query:
        cattle_qs = cattle_qs.filter(
            Q(tag_id__icontains=query)
            | Q(breed__icontains=query)
            | Q(health_status__icontains=query)
        )
    if species:
        cattle_qs = cattle_qs.filter(cattle_type=species)
    if health:
        cattle_qs = cattle_qs.filter(health_status=health)

    if select_all and not selected_id:
        first_cattle = cattle_qs.first()
        if first_cattle:
            selected_id = str(first_cattle.id)

    selected_cattle = None
    if selected_id:
        selected_cattle = cattle_qs.filter(id=selected_id).first()

    species_options = (
        Cattle.objects.filter(farm=farm)
        .values_list("cattle_type", flat=True)
        .distinct()
        .order_by("cattle_type")
    )

    context = {
        "farm": farm,
        "cattles": cattle_qs,
        "q": query,
        "species": species,
        "health": health,
        "selected_id": str(selected_id or ""),
        "selected_cattle": selected_cattle,
        "species_options": species_options,
    }
    return render(request, "systemapp/select_cattle.html", context)

from django.shortcuts import render, get_object_or_404, redirect
from .models import Diagnosis, IssueReport, Cattle
from django.contrib.auth.decorators import login_required

@login_required(login_url='/systemapp/vet_login/')
def diagnosis_prescription_entry(request):
    report_id = request.GET.get("report_id")
    cattle_id = request.GET.get("cattle_id")

    if report_id and cattle_id:
        return redirect("diagnosis_prescription", report_id=report_id, cattle_id=cattle_id)

    latest_issue = (
        IssueReport.objects.select_related("cattle")
        .filter(cattle__isnull=False)
        .order_by("-id")
        .first()
    )

    if latest_issue:
        return redirect(
            "diagnosis_prescription",
            report_id=latest_issue.id,
            cattle_id=latest_issue.cattle_id,
        )

    return redirect("vet_cases")

@login_required(login_url='/systemapp/vet_login/')
def diagnosis_prescription(request, report_id, cattle_id):

    report = get_object_or_404(IssueReport, id=report_id)
    cattle = get_object_or_404(Cattle, id=cattle_id)

    if request.method == 'POST':

        observed_date = request.POST.get('observed_date')
        condition_category = request.POST.get('condition_category')
        observation_notes = request.POST.get('observation_notes')
        prescription_file = request.FILES.get('prescription_file')
        is_emergency = request.POST.get('is_emergency') == 'on'

        Diagnosis.objects.create(
            issue_report=report,
            cattle=cattle,
            observed_date=observed_date,
            condition_category=condition_category,
            observation_notes=observation_notes,
            prescription_file=prescription_file,
            is_emergency=is_emergency,
            created_by=request.user
        )

        return redirect('vet_cases')

    return render(
        request,
        'systemapp/diagnosis_prescription.html',
        {
            'report': report,
            'cattle': cattle
        }
    )
@login_required(login_url='/systemapp/vet_login/')
def create_report(request, farm_id, cattle_id):
    farm = get_object_or_404(Farm, id=farm_id)
    cattle = get_object_or_404(Cattle, id=cattle_id, farm=farm)

    report = Reports.objects.create(
        vet=request.user,
        farm=farm,
        cattle=cattle,
        findings="",
    )

    return redirect(
        f"{reverse('report_health')}?farm_id={farm.id}&cattle_id={cattle.id}&report_id={report.id}"
    )

from django.shortcuts import render, redirect, get_object_or_404
from .models import Cattle, IssueReport, Farm
from django.contrib.auth.decorators import login_required


@login_required(login_url='/systemapp/vet_login/')
def select_cattles(request, farm_id, report_id):
    farm = get_object_or_404(Farm, id=farm_id)
    report = get_object_or_404(IssueReport, id=report_id)

    cattle_list = Cattle.objects.filter(farm=farm)

    if request.method == "POST":
        selected_ids = request.POST.getlist('cattle_ids')
        if hasattr(report, "selected_cattle"):
            report.selected_cattle.set(selected_ids)
        elif hasattr(report, "cattle_id") and selected_ids:
            report.cattle_id = selected_ids[0]
            report.save(update_fields=["cattle"])
        else:
            request.session["selected_cattle_ids"] = selected_ids
        return redirect(f"{reverse('report_health')}?report_id={report.id}&farm_id={farm.id}")

    context = {
        'farm': farm,
        'report': report,
        'cattle_list': cattle_list
    }

    return render(request, 'systemapp/select_cattles.html', context)

from django.shortcuts import render, redirect
from .models import Vaccination
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.db.models import Q


@login_required(login_url='/systemapp/vet_login/')
def vaccination_reminder(request):
    today = timezone.now().date()
    view = (request.GET.get("view") or "all").strip()
    query = (request.GET.get("q") or "").strip()

    vaccinations = Vaccination.objects.select_related("cattle", "cattle__farm")

    for v in vaccinations:
        if v.completed_date and v.status != "completed":
            v.status = "completed"
        elif v.scheduled_date and v.status != "scheduled":
            v.status = "scheduled"
        elif v.due_date <= today:
            v.status = "due_now"
        elif (v.due_date - today).days <= 7:
            v.status = "upcoming"
        v.save()

    vaccinations = Vaccination.objects.select_related("cattle", "cattle__farm").order_by("due_date")

    if query:
        vaccinations = vaccinations.filter(
            Q(cattle__tag_id__icontains=query)
            | Q(cattle__breed__icontains=query)
            | Q(cattle__farm__farm_name__icontains=query)
            | Q(vaccine_type__icontains=query)
        )

    if view == "high":
        vaccinations = vaccinations.filter(status__in=["due_now", "upcoming"])
    elif view == "regional":
        vaccinations = vaccinations.filter(ai_reason__isnull=False).exclude(ai_reason="")

    counts_qs = Vaccination.objects.all()
    immediate_count = counts_qs.filter(status="due_now").count()
    coming_soon_count = counts_qs.filter(status="upcoming").count()
    routine_count = counts_qs.filter(status="scheduled").count()

    context = {
        "vaccinations": vaccinations,
        "immediate_count": immediate_count,
        "coming_soon_count": coming_soon_count,
        "routine_count": routine_count,
        "total_count": counts_qs.count(),
        "shown_count": vaccinations.count(),
        "active_view": view,
        "q": query,
    }

    return render(request, "systemapp/vaccination_reminder.html", context)


@login_required(login_url='/systemapp/vet_login/')
def schedule_all_vaccinations(request):
    if request.method != "POST":
        return redirect("vaccination_reminder")

    scheduled_date = request.POST.get("scheduled_date") or str(timezone.now().date())

    Vaccination.objects.filter(status__in=["due_now", "upcoming"]).update(
        scheduled_date=scheduled_date,
        status="scheduled",
    )
    return redirect("vaccination_reminder")

@login_required(login_url='/systemapp/vet_login/')
def schedule_vaccination(request, vaccination_id):
    vaccination = get_object_or_404(Vaccination, id=vaccination_id)

    if request.method == 'POST':
        scheduled_date = request.POST.get('scheduled_date') or str(timezone.now().date())
        vaccination.scheduled_date = scheduled_date
        vaccination.status = 'scheduled'
        vaccination.save()

        return redirect('vaccination_reminder')

    return redirect('vaccination_reminder')

@login_required(login_url='/systemapp/vet_login/')
def complete_vaccination(request, vaccination_id):
    vaccination = get_object_or_404(Vaccination, id=vaccination_id)

    vaccination.completed_date = timezone.now().date()
    vaccination.status = 'completed'
    vaccination.save()

    return redirect('vaccination_reminder')

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from .models import UserProfile


def customer_register(request):
    form_data = {}
    if request.method == "POST":
        full_name = (request.POST.get("full_name") or "").strip()
        farm_name = (request.POST.get("farm_name") or "").strip()
        location = (request.POST.get("location") or "").strip()
        contact = (request.POST.get("contact") or "").strip()
        email = (request.POST.get("email") or "").strip().lower()
        password = request.POST.get("password") or ""

        form_data = {
            "full_name": full_name,
            "farm_name": farm_name,
            "location": location,
            "contact": contact,
            "email": email,
        }

        if not all([full_name, farm_name, location, contact, email, password]):
            messages.error(request, "Please fill all required fields.")
            return render(request, "systemapp/customer_register.html", {"form_data": form_data})

        if len(password) < 8:
            messages.error(request, "Password must be at least 8 characters.")
            return render(request, "systemapp/customer_register.html", {"form_data": form_data})

        if User.objects.filter(username=email).exists():
            messages.error(request, "Email already registered.")
            return render(request, "systemapp/customer_register.html", {"form_data": form_data})

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=full_name
        )

        farm, _ = Farm.objects.get_or_create(
            farm_name=farm_name,
            defaults={"location": location, "contact_number": contact},
        )
        if not farm.location:
            farm.location = location
        if not farm.contact_number:
            farm.contact_number = contact
        farm.save()

        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.role = "WORKER"
        profile.farm = farm
        profile.is_verified = False
        profile.save()

        messages.success(request, "Registration submitted. Waiting for admin approval.")
        return redirect('customer_login')

    return render(request, "systemapp/customer_register.html", {"form_data": form_data})

from django.contrib.auth import authenticate, login


def user_login(request):

    if request.method == "POST":

        username = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:

            profile = user.userprofile

            if profile.approval_status != 'approved':
                messages.error(request, "Your account is pending admin approval.")
                return redirect('systemapp/login')

            if profile.account_blocked:
                messages.error(request, "Your account has been blocked.")
                return redirect('systemapp/login')

            login(request, user)
            return redirect('portal')

        else:
            messages.error(request, "Invalid credentials.")

    return render(request, 'systemapp/login.html')

from django.contrib.auth import logout
from django.shortcuts import redirect


def user_logout(request):
    logout(request)
    request.session.flush()
    return redirect('get_started')

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import UserProfile


def customer_login(request):
    form_data = {}
    if request.method == 'POST':
        email = (request.POST.get('email') or '').strip().lower()
        password = request.POST.get('password') or ''
        form_data["email"] = email

        user = authenticate(request, username=email, password=password)

        if user is not None:
            profile = UserProfile.objects.filter(user=user).first()
            if profile and not profile.is_verified:
                messages.warning(request, "Your account is pending admin approval.")
                return render(request, 'systemapp/customer_login.html', {"form_data": form_data})

            login(request, user)
            return redirect('portal')

        else:
            messages.error(request, "Invalid email or password")

    return render(request, 'systemapp/customer_login.html', {"form_data": form_data})
def user_logout(request):
    logout(request)
    request.session.flush()
    return redirect('get_started')


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Cattle, PurchaseRequest


# Public — no login needed to browse/compare
def compare_cattle(request):

    cattle_ids = request.GET.getlist('cattle') or request.GET.getlist('ids')

    if cattle_ids:
        cattles = Cattle.objects.select_related('farm').filter(id__in=cattle_ids)[:3]
    else:
        # Fallback to первые 2 available cattle for sale
        cattles = Cattle.objects.select_related('farm').filter(is_for_sale=True)[:2]

    context = {
        'cattles': cattles
    }

    return render(request, 'systemapp/compare_cattle.html', context)

from django.utils import timezone
from datetime import timedelta
from .models import Order

@login_required
def my_requests(request):

    requests = PurchaseRequest.objects.filter(buyer=request.user)

    return render(request, 'systemapp/my_requests.html', {
        'requests': requests
    })
def calculate_ai_score(cattle):

    score = 0

    if cattle.is_recommended:
        score += 30

    if cattle.price < 4000:
        score += 30

    score += 40  # Health weight (custom logic)

    return score

from django.shortcuts import render, get_object_or_404
from .models import Order


@login_required(login_url='/systemapp/customer_login/')
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    context = {
        "order": order
    }

    return render(request, "systemapp/order_confirmation.html", context)

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Cattle, Bid



@login_required
def cattle_detail(request, pk):
    cattle = get_object_or_404(Cattle, pk=pk)
    return render(request, "cattle_detail.html", {"cattle": cattle})


@login_required
def place_bid(request, pk):
    cattle = get_object_or_404(Cattle, pk=pk)
    profile = getattr(request.user, 'userprofile', None)

    # 🔒 Restriction check
    if not profile or not profile.is_approved:
        return render(request, "purchase_restriction.html")

    if request.method == "POST":
        amount = request.POST.get("bid_amount")

        Bid.objects.create(
            user=request.user,
            cattle=cattle,
            bid_amount=amount
        )

        messages.success(request, "Bid placed successfully!")
        return redirect("systemapp/olx")

    return render(request, "place_bid.html", {"cattle": cattle})

def purchase_restriction(request):
    return render(request, "systemapp/purchase_restriction.html")

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from .models import Order, Cattle
@login_required
def place_order(request, pk):
    cattle = get_object_or_404(Cattle, pk=pk)

    # Check duplicate in last 5 minutes
    five_minutes_ago = timezone.now() - timedelta(minutes=5)

    existing_order = Order.objects.filter(
        user=request.user,
        cattle=cattle,
        created_at__gte=five_minutes_ago
    ).first()

    if existing_order:
        return redirect('duplicate_detection', pk=cattle.pk)

    if request.method == "POST":
        Order.objects.create(
            user=request.user,
            cattle=cattle,
            amount=cattle.price,
            status='pending'
        )
        return redirect('olx')

    return render(request, "systemapp/place_order.html", {"cattle": cattle})

@login_required
def duplicate_detection(request, pk):
    cattle = get_object_or_404(Cattle, pk=pk)

    latest_order = Order.objects.filter(
        user=request.user,
        cattle=cattle
    ).order_by('-created_at').first()

    return render(request, "systemapp/duplicate_detection.html", {
        "cattle": cattle,
        "order": latest_order
    })

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import UserVerification


@login_required
def account_verified(request):
    verification = UserVerification.objects.get(user=request.user)

    if verification.status != 'approved':
        return redirect('olx')   # or wherever you want unapproved users to go

    return render(request, "systemapp/account_verified.html")


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Vet, Worker, Buyer

@login_required(login_url='/systemapp/admin_login/')
def admin_workplace(request):
    if not (request.user.is_superuser or request.user.is_staff):
        return redirect('admin_login')
    from .models import VetProfile
    from .models import Farm
    pending_vets = Vet.objects.filter(is_approved=False).count()
    pending_workers = Worker.objects.filter(is_approved=False).count()
    pending_buyers = Buyer.objects.filter(is_approved=False).count()

    # Also count VetProfile pending approvals (from vet_register flow)
    from .ai_logic import validate_vet_license_number
    pending_vet_profiles = VetProfile.objects.filter(approved=False)
    pending_vet_profile_count = pending_vet_profiles.count()
    approved_vet_profiles = VetProfile.objects.filter(approved=True).select_related("user")

    farms = Farm.objects.all().order_by("farm_name")
    selected_farm = None
    farm_id = request.GET.get("farm_id") or ""
    if farm_id.isdigit():
        selected_farm = farms.filter(id=int(farm_id)).first()

    nearby_vets = list(approved_vet_profiles)
    if selected_farm and (selected_farm.location or "").strip():
        loc = selected_farm.location.strip()
        nearby_vets = list(approved_vet_profiles.filter(location__icontains=loc)) or list(approved_vet_profiles)

    recent_activities = list(Vet.objects.all()[:2]) + list(Worker.objects.all()[:2]) + list(Buyer.objects.all()[:2])

    context = {
        'pending_vets': pending_vets + pending_vet_profile_count,
        'pending_workers': pending_workers,
        'pending_buyers': pending_buyers,
        'recent_activities': recent_activities,
        'pending_vet_profiles': pending_vet_profiles,
        'pending_vet_profile_rows': [
            {"profile": p, "validation": validate_vet_license_number(p.license_number)}
            for p in pending_vet_profiles
        ],
        'farms': farms,
        'selected_farm': selected_farm,
        'nearby_vets': nearby_vets,
    }

    return render(request, 'systemapp/admin_workplace.html', context)


@login_required(login_url='/systemapp/worker_login/')
def nearby_vets(request):
    from .models import VetProfile, Farm

    # Determine farm (best-effort)
    farm = None
    try:
        profile = getattr(request.user, "userprofile", None)
        if profile and getattr(profile, "farm_id", None):
            farm = profile.farm
    except Exception:
        farm = None

    farm_id = request.GET.get("farm_id") or ""
    if not farm and farm_id.isdigit():
        farm = Farm.objects.filter(id=int(farm_id)).first()

    farms = Farm.objects.all().order_by("farm_name")
    vets_qs = VetProfile.objects.filter(approved=True).select_related("user")

    nearby = []
    if farm and (farm.location or "").strip():
        loc = farm.location.strip()
        nearby = list(vets_qs.filter(location__icontains=loc))
        # Fallback: if no vet has matching location string, show all approved vets
        if not nearby:
            nearby = list(vets_qs)
    else:
        nearby = list(vets_qs)

    return render(request, "systemapp/nearby_vets.html", {
        "farms": farms,
        "selected_farm": farm,
        "vets": nearby,
    })

def admin_logout(request):
    logout(request)
    request.session.flush()
    return render(request, 'systemapp/admin_logged_out.html')

def worker_logout(request):
    logout(request)
    request.session.flush()
    return redirect('get_started')


@login_required(login_url='/systemapp/admin_login/')
def approve_vet(request, vet_id):
    from .models import VetProfile
    profile = get_object_or_404(VetProfile, id=vet_id)
    profile.approved = True
    profile.save()
    messages.success(request, f"Vet '{profile.user.username}' has been approved.")
    return redirect('admin_workplace')


@login_required(login_url='/systemapp/admin_login/')
def reject_vet(request, vet_id):
    from .models import VetProfile
    profile = get_object_or_404(VetProfile, id=vet_id)
    profile.approved = False
    profile.save()
    messages.warning(request, f"Vet '{profile.user.username}' has been rejected.")
    return redirect('admin_workplace')


# Home Page
def home(request):
    from .models import NewsletterSubscriber
    if request.method == "POST":
        email = request.POST.get("email")
        if email:
            NewsletterSubscriber.objects.get_or_create(email=email)
            messages.success(request, "Subscribed successfully!")
    return render(request, "systemapp/home.html")


# Register Choice Page
def register_choice(request):
    return render(request, "systemapp/register_choice.html")


# Login View
def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            if user.is_superuser:
                return redirect('admin_workplace')
            elif hasattr(user, 'buyerprofile'):
                return redirect('olx')
            elif hasattr(user, 'vetprofile'):
                return redirect('vet_dashboard')
            elif hasattr(user, 'workerprofile'):
                return redirect('worker_dashboard')
            else:
                return redirect('home')

        else:
            messages.error(request, "Invalid credentials")

    return render(request, "systemapp/login.html")


# Logout
def logout_view(request):
    logout(request)
    request.session.flush()
    return redirect('get_started')


# Vet Logout
def vet_logout(request):
    logout(request)
    request.session.flush()
    return redirect('get_started')


# Buyer Registration
def buyer_register(request):
    from .models import BuyerProfile
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = User.objects.create_user(username=username, password=password)
        BuyerProfile.objects.create(user=user)

        messages.success(request, "Registration submitted. Await admin approval.")
        return redirect('customer_login')

    return render(request, "systemapp/buyer_register.html")


# Worker Registration
def worker_register(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        role = request.POST.get('role', 'General Worker')

        user = User.objects.create_user(username=username, password=password)
        WorkerProfile.objects.create(user=user, role=role)

        messages.success(request, "Registration submitted. Await admin approval.")
        return redirect('worker_login')

    return render(request, "systemapp/worker_register.html")


# Vet Registration
def vet_register(request):
    from .models import VetProfile
    from .models import Vet
    from .ai_logic import validate_vet_license_number
    if request.method == "POST":
        username = " ".join((request.POST.get('username') or '').split())
        password = request.POST.get('password') or ''
        license_number = (request.POST.get('license_number') or '').strip()
        location = (request.POST.get("location") or "").strip()
        license_document = request.FILES.get("license_document")

        if not username or not password or not license_number:
            messages.error(request, 'All fields are required.')
            return render(request, "systemapp/vet_register.html")

        if len(password) < 6:
            messages.error(request, 'Password must be at least 6 characters.')
            return render(request, "systemapp/vet_register.html")

        validation = validate_vet_license_number(license_number)
        if not validation["format_ok"]:
            msg = "Invalid license number format."
            if validation["reasons"]:
                msg += " " + "; ".join(validation["reasons"][:2])
            messages.error(request, msg)
            return render(request, "systemapp/vet_register.html")

        normalized_license = validation["normalized"]

        if not license_document:
            messages.error(request, "Please upload a photo/PDF of your license for admin verification.")
            return render(request, "systemapp/vet_register.html")

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
            return render(request, "systemapp/vet_register.html")

        if VetProfile.objects.filter(license_number=normalized_license).exists() or Vet.objects.filter(license_number=normalized_license).exists():
            messages.error(request, "This license number is already registered. Please contact admin if this is a mistake.")
            return render(request, "systemapp/vet_register.html")

        user = User.objects.create_user(username=username, password=password)
        VetProfile.objects.create(
            user=user,
            license_number=normalized_license,
            license_document=license_document,
            location=location,
        )

        messages.success(request, "Registration submitted successfully. Please wait for admin approval before logging in.")
        return redirect('vet_login')

    return render(request, "systemapp/vet_register.html")


# ============================================================
#  CUSTOMER / BUYER MODULE  —  Registration, Login, Marketplace
# ============================================================

from .models import BuyerProfile, PurchaseRequest, Order, Bid, UserVerification


# ---------- Registration ----------
def buyer_register(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name", "").strip()
        email     = request.POST.get("email", "").strip()
        password  = request.POST.get("password", "").strip()
        username  = request.POST.get("username", "").strip()

        # Use email as username if no username provided
        if not username:
            username = email

        if not email or not password:
            messages.error(request, "Email and password are required.")
            return render(request, "systemapp/buyer_register.html")

        if User.objects.filter(username=username).exists():
            messages.error(request, "An account with this email already exists.")
            return render(request, "systemapp/buyer_register.html")

        user = User.objects.create_user(
            username=username, email=email, password=password,
            first_name=full_name,
        )
        BuyerProfile.objects.create(user=user, approved=False)
        messages.success(request, "Registration submitted. Await admin approval.")
        return redirect("account_verified")

    return render(request, "systemapp/buyer_register.html")


# ---------- Login with approval gate ----------
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import ensure_csrf_cookie


@never_cache
@ensure_csrf_cookie
def customer_login(request):
    if request.method == "POST":
        email    = request.POST.get("email", "").strip()
        password = request.POST.get("password", "").strip()

        # Try to authenticate by email-as-username first, then by email lookup
        user = authenticate(request, username=email, password=password)
        if user is None:
            # Fallback: find user by email field
            try:
                user_obj = User.objects.get(email=email)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                user = None

        if user is not None:
            # Check if buyer profile exists
            try:
                profile = BuyerProfile.objects.get(user=user)
            except BuyerProfile.DoesNotExist:
                messages.error(request, "No buyer account found. Please register first.")
                return render(request, "systemapp/customer_login.html")

            # Log the user in
            login(request, user)

            # ─── Always follow the next URL so purchase → order_confirmation works ───
            # If account is still pending, just show an info notice — don't block the flow
            if not profile.approved:
                messages.info(request, "⏳ Your account is pending admin approval.")

            next_url = request.POST.get('next') or request.GET.get('next') or 'olx'
            return redirect(next_url)
        else:
            messages.error(request, "Invalid credentials.")

    return render(request, "systemapp/customer_login.html")


# ---------- Account verified / pending page ----------
def account_verified(request):
    return render(request, "systemapp/account_verified.html")


# ---------- Buyer Profile ----------
@login_required
def buyer_profile(request):
    try:
        profile = BuyerProfile.objects.get(user=request.user)
    except BuyerProfile.DoesNotExist:
        profile = None

    purchase_requests = PurchaseRequest.objects.filter(
        buyer=request.user
    ).select_related("cattle").order_by("-created_at")[:10]

    orders = Order.objects.filter(
        user=request.user
    ).select_related("cattle").order_by("-order_date")[:10]

    stats = {
        "requests": PurchaseRequest.objects.filter(buyer=request.user).count(),
        "orders": Order.objects.filter(user=request.user).count(),
        "bids": Bid.objects.filter(user=request.user).count(),
    }

    return render(request, "systemapp/buyer_profile.html", {
        "profile": profile,
        "purchase_requests": purchase_requests,
        "orders": orders,
        "stats": stats,
    })


# ---------- Admin: customer approval ----------
@login_required
def customer_approval(request):
    from .models import Customer
    buyers = BuyerProfile.objects.select_related("user").all()
    customers = Customer.objects.all()
    return render(request, "systemapp/customer_approval.html", {
        "buyers": buyers,
        "customers": customers,
    })


@login_required
def approve_customer(request, customer_id):
    profile = get_object_or_404(BuyerProfile, id=customer_id)
    profile.approved = True
    profile.save()
    messages.success(request, f"Buyer '{profile.user.username}' approved.")
    return redirect("customer_approval")


@login_required
def block_customer(request, customer_id):
    profile = get_object_or_404(BuyerProfile, id=customer_id)
    profile.approved = False
    profile.save()
    messages.warning(request, f"Buyer '{profile.user.username}' blocked.")
    return redirect("customer_approval")


# ---------- OLX Marketplace ----------
# Login required here (entry point) — ensures buyer is authenticated for
# entire flow: OLX → Compare → Send Request → Order Confirmation
@login_required(login_url='/systemapp/customer_login/')
def olx(request):

    from django.core.paginator import Paginator

    qs = Cattle.objects.select_related("farm").filter(
        is_for_sale=True, sale_status="available"
    ).order_by("-created_at")

    # --- Filters ---
    q = request.GET.get("q", "").strip()
    breed = request.GET.get("breed", "").strip()
    price = request.GET.get("price", "").strip()
    location = request.GET.get("location", "").strip()

    applied_filters = []

    if q:
        qs = qs.filter(
            models.Q(breed__icontains=q)
            | models.Q(tag_id__icontains=q)
            | models.Q(farm__location__icontains=q)
            | models.Q(farm__farm_name__icontains=q)
        )
        applied_filters.append(f'Search: "{q}"')

    if breed:
        qs = qs.filter(breed__iexact=breed)
        applied_filters.append(f"Breed: {breed}")

    if price:
        if price == "0-1500":
            qs = qs.filter(price__lte=1500)
        elif price == "1500-3000":
            qs = qs.filter(price__gt=1500, price__lte=3000)
        elif price == "3000+":
            qs = qs.filter(price__gt=3000)
        applied_filters.append(f"Price: {price}")

    if location:
        qs = qs.filter(farm__location__iexact=location)
        applied_filters.append(f"Location: {location}")

    total_count = qs.count()

    # Pagination (12 per page)
    paginator = Paginator(qs, 12)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    # Filter option lists
    breed_options = (
        Cattle.objects.filter(is_for_sale=True)
        .values_list("breed", flat=True)
        .distinct()
        .order_by("breed")
    )
    breed_options = [b for b in breed_options if b]

    location_options = (
        Cattle.objects.filter(is_for_sale=True)
        .select_related("farm")
        .values_list("farm__location", flat=True)
        .distinct()
        .order_by("farm__location")
    )
    location_options = [loc for loc in location_options if loc]

    context = {
        "cattle_list": page_obj,
        "page_obj": page_obj,
        "total_count": total_count,
        "shown_count": len(page_obj),
        "q": q,
        "breed": breed,
        "price": price,
        "location": location,
        "breed_options": breed_options,
        "location_options": location_options,
        "applied_filters": applied_filters,
    }
    return render(request, "systemapp/olx.html", context)


# ---------- Cattle Detail ----------
@login_required(login_url='/systemapp/customer_login/')
def cattle_detail(request, pk):
    cattle = get_object_or_404(Cattle, pk=pk)
    bids = Bid.objects.filter(cattle=cattle).order_by("-placed_at")[:5]
    return render(request, "systemapp/olx.html", {
        "cattle": cattle,
        "bids": bids,
    })


# ---------- Place Bid ----------
@login_required(login_url='/systemapp/customer_login/')
def place_bid(request, pk):
    cattle = get_object_or_404(Cattle, pk=pk)
    if request.method == "POST":
        amount = request.POST.get("bid_amount", "0")
        try:
            amount = float(amount)
        except (ValueError, TypeError):
            amount = 0

        if amount <= 0:
            messages.error(request, "Please enter a valid bid amount.")
            return redirect("cattle_detail", pk=pk)

        Bid.objects.create(user=request.user, cattle=cattle, bid_amount=amount)
        messages.success(request, f"Bid of ${amount:.2f} placed successfully.")
    return redirect("olx")


# ---------- Send Purchase Request ----------
# No login required — anonymous users use the demo buyer account automatically
def send_purchase_request(request, cattle_id):
    from django.contrib.auth.models import User as AuthUser
    from datetime import timedelta

    cattle = get_object_or_404(Cattle, pk=cattle_id)

    # Use the logged-in buyer, or fall back to the demo testbuyer account
    if request.user.is_authenticated:
        buyer = request.user
    else:
        try:
            buyer = AuthUser.objects.get(username='testbuyer')
        except AuthUser.DoesNotExist:
            # Safety: create testbuyer on the fly if somehow missing
            buyer = AuthUser.objects.create_user(
                username='testbuyer', email='testbuyer@test.com', password='test1234'
            )
            from systemapp.models import BuyerProfile
            BuyerProfile.objects.get_or_create(user=buyer, defaults={'approved': True})

    # Create purchase request
    PurchaseRequest.objects.filter(buyer=buyer, cattle=cattle, status="pending").delete()
    PurchaseRequest.objects.create(buyer=buyer, cattle=cattle, status="approved")

    # Create order and redirect straight to confirmation
    order = Order.objects.create(
        user=buyer,
        cattle=cattle,
        amount=cattle.price or 0,
        amount_paid=cattle.price or 0,
        estimated_delivery_start=timezone.now().date() + timedelta(days=3),
        estimated_delivery_end=timezone.now().date() + timedelta(days=7),
    )

    return redirect("order_confirmation", order_id=order.id)


# ---------- My Requests ----------
@login_required(login_url='/systemapp/customer_login/')
def my_requests(request):
    requests_list = PurchaseRequest.objects.filter(
        buyer=request.user
    ).select_related("cattle").order_by("-created_at")
    return render(request, "systemapp/olx.html", {
        "cattle_list": [],
        "my_requests": requests_list,
        "total_count": 0,
        "shown_count": 0,
        "q": "",
        "breed": "",
        "price": "",
        "location": "",
        "breed_options": [],
        "location_options": [],
        "applied_filters": [],
    })


# ---------- Place Order (from approved purchase request) ----------
@login_required(login_url='/systemapp/customer_login/')
def place_order(request, pk):
    from datetime import timedelta
    from django.utils import timezone

    purchase_req = get_object_or_404(PurchaseRequest, pk=pk, buyer=request.user)

    if purchase_req.status != "approved":
        messages.error(request, "This purchase request has not been approved yet.")
        return redirect("my_requests")

    cattle = purchase_req.cattle

    # Check for purchase restriction (admin-flagged fake purchase)
    if purchase_req.ai_score < -1:
        return redirect("purchase_restriction")

    order = Order.objects.create(
        user=request.user,
        cattle=cattle,
        amount=cattle.price or 0,
        amount_paid=cattle.price or 0,
        estimated_delivery_start=timezone.now().date() + timedelta(days=3),
        estimated_delivery_end=timezone.now().date() + timedelta(days=7),
    )

    # Mark cattle as sold
    cattle.sale_status = "sold"
    cattle.is_for_sale = False
    cattle.save()

    # Mark purchase request as completed
    purchase_req.status = "approved"
    purchase_req.save()

    messages.success(request, "Order placed successfully!")
    return redirect("order_confirmation", order_id=order.id)


# ---------- Order Confirmation ----------
@login_required(login_url='/systemapp/customer_login/')
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    from .models import PaymentSubmission
    payment_submission = PaymentSubmission.objects.filter(order=order).first()
    return render(request, "systemapp/order_confirmation.html", {"order": order, "payment_submission": payment_submission})


# ---------- Payment Setup (QR / Bank Transfer) ----------
@login_required(login_url='/systemapp/customer_login/')
def payment_setup(request, order_id):
    from django.conf import settings
    from urllib.parse import quote
    from django.utils import timezone
    from .models import AdminSettings, PaymentSubmission

    order = get_object_or_404(Order, id=order_id, user=request.user)

    admin_cfg = AdminSettings.objects.filter(pk=1).first()

    payee_name = (getattr(admin_cfg, "payee_name", "") or "").strip() or getattr(settings, "PAYMENT_PAYEE_NAME", "Cattle Farm System")
    upi_id = (getattr(admin_cfg, "upi_id", "") or "").strip() or getattr(settings, "PAYMENT_UPI_ID", "yourupi@bank")
    currency = (getattr(admin_cfg, "currency", "") or "").strip() or getattr(settings, "PAYMENT_CURRENCY", "INR")

    bank_account_number = (getattr(admin_cfg, "bank_account_number", "") or "").strip() or getattr(settings, "PAYMENT_BANK_ACCOUNT_NUMBER", "123456789012345")
    bank_ifsc = (getattr(admin_cfg, "bank_ifsc", "") or "").strip() or getattr(settings, "PAYMENT_BANK_IFSC", "ABCD0123456")
    bank_name = (getattr(admin_cfg, "bank_name", "") or "").strip() or getattr(settings, "PAYMENT_BANK_NAME", "Your Bank")

    amount_str = str(order.amount)
    note = f"Order #{order.id}"

    upi_uri = (
        "upi://pay"
        f"?pa={quote(upi_id)}"
        f"&pn={quote(payee_name)}"
        f"&am={quote(amount_str)}"
        f"&cu={quote(currency)}"
        f"&tn={quote(note)}"
    )

    submission = PaymentSubmission.objects.filter(order=order).first()

    if request.method == "POST":
        method = (request.POST.get("method", "UPI") or "UPI").strip().upper()
        if method not in {"UPI", "BANK"}:
            method = "UPI"

        transaction_reference = (request.POST.get("transaction_reference", "") or "").strip()
        receipt = request.FILES.get("receipt")

        if not transaction_reference and not receipt:
            messages.error(request, "Please add a transaction reference or upload a receipt screenshot.")
        else:
            submission, _ = PaymentSubmission.objects.get_or_create(order=order)
            if submission.status == "verified":
                messages.info(request, "This payment is already verified.")
            else:
                submission.method = method
                submission.transaction_reference = transaction_reference
                if receipt:
                    submission.receipt = receipt
                submission.status = "submitted"
                submission.submitted_at = timezone.now()
                submission.save()
                messages.success(request, "Payment submitted. Our team will verify it shortly.")
                return redirect("order_confirmation", order_id=order.id)

    return render(request, "systemapp/payment_setup.html", {
        "order": order,
        "payee_name": payee_name,
        "currency": currency,
        "upi_id": upi_id,
        "upi_uri": upi_uri,
        "bank_account_number": bank_account_number,
        "bank_ifsc": bank_ifsc,
        "bank_name": bank_name,
        "support_email": getattr(admin_cfg, "support_email", "") if admin_cfg else "",
        "support_phone": getattr(admin_cfg, "support_phone", "") if admin_cfg else "",
        "payment_submission": submission,
    })


# ---------- Purchase Restriction (admin flag) ----------
@login_required(login_url='/systemapp/customer_login/')
def purchase_restriction(request):
    return render(request, "systemapp/purchase_restriction.html")


# ---------- Duplicate Detection ----------
@login_required
def duplicate_detection(request, pk):
    cattle = get_object_or_404(Cattle, pk=pk)
    return render(request, "systemapp/duplicate_detection.html", {"cattle": cattle})


# ============================================================
# VET MODULE VIEWS
# ============================================================

@login_required(login_url='/systemapp/vet_login/')
def select_farms(request):
    from .models import Farm
    from django.core.paginator import Paginator

    q = request.GET.get('q', '')
    sort = request.GET.get('sort', 'name')
    herd = request.GET.get('herd', '')
    ai_pending = request.GET.get('ai_pending', '')

    farms = Farm.objects.filter(is_active=True)

    if q:
        farms = farms.filter(
            models.Q(farm_name__icontains=q) |
            models.Q(location__icontains=q) |
            models.Q(contact_number__icontains=q) |
            models.Q(registration_id__icontains=q)
        )

    if herd == 'small':
        farms = farms.filter(cattle_count__lt=100)
    elif herd == 'medium':
        farms = farms.filter(cattle_count__gte=100, cattle_count__lte=250)
    elif herd == 'large':
        farms = farms.filter(cattle_count__gt=250)

    if ai_pending:
        farms = farms.filter(ai_verified=False)

    if sort == 'name':
        farms = farms.order_by('farm_name')
    elif sort == 'herd_desc':
        farms = farms.order_by('-cattle_count')
    else:
        farms = farms.order_by('farm_name')

    total_count = farms.count()
    paginator = Paginator(farms, 12)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    demo_images = [
        "https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=1600&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1469474968028-56623f02e42e?q=80&w=1600&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1472396961693-142e6e269027?q=80&w=1600&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1500595046743-cd271d694d30?q=80&w=1600&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1592861956120-e524fc739696?q=80&w=1600&auto=format&fit=crop",
    ]

    for farm in page_obj.object_list:
        try:
            idx = int(farm.id or 0) % len(demo_images)
        except Exception:
            idx = 0
        farm.demo_image_url = demo_images[idx]

    context = {
        'farms': page_obj,
        'q': q,
        'sort': sort,
        'herd': herd,
        'ai_pending': ai_pending,
        'total_count': total_count,
        'page_obj': page_obj,
    }
    return render(request, 'systemapp/select_farms.html', context)


@login_required(login_url='/systemapp/vet_login/')
def select_cattle(request, farm_id):
    from .models import Farm
    farm = get_object_or_404(Farm, id=farm_id)

    q = request.GET.get('q', '')
    species = request.GET.get('species', '')
    health = request.GET.get('health', '')
    selected_id = request.GET.get('selected', '')

    cattles = Cattle.objects.filter(farm=farm)

    if q:
        cattles = cattles.filter(
            models.Q(tag_id__icontains=q) |
            models.Q(breed__icontains=q) |
            models.Q(health_status__icontains=q)
        )

    if species:
        cattles = cattles.filter(species=species)

    if health:
        cattles = cattles.filter(health_status=health)

    species_options = Cattle.objects.filter(farm=farm).values_list('species', flat=True).distinct()

    selected_cattle = None
    if selected_id:
        selected_cattle = Cattle.objects.filter(id=selected_id, farm=farm).first()

    context = {
        'farm': farm,
        'cattles': cattles,
        'q': q,
        'species': species,
        'health': health,
        'species_options': [s for s in species_options if s],
        'selected_id': selected_id,
        'selected_cattle': selected_cattle,
    }
    return render(request, 'systemapp/select_cattle.html', context)


@login_required(login_url='/systemapp/vet_login/')
def create_report(request, farm_id, cattle_id):
    from .models import Farm, Reports
    farm = get_object_or_404(Farm, id=farm_id)
    cattle = get_object_or_404(Cattle, id=cattle_id)

    if request.method == 'POST':
        findings = request.POST.get('findings') or request.POST.get('symptoms') or ''
        report = Reports.objects.create(
            vet=request.user,
            farm=farm,
            cattle=cattle,
            findings=findings,
        )
        messages.success(request, 'Report created successfully.')
        return redirect('diagnosis_prescription', report_id=report.id, cattle_id=cattle.id)

    context = {
        'farm': farm,
        'cattle': cattle,
    }
    return render(request, 'systemapp/report_health.html', context)


@login_required(login_url='/systemapp/vet_login/')
def diagnosis_prescription_entry(request):
    """Entry point: show the diagnosis form. User must select a cattle first."""
    cattle_id = request.GET.get('cattle_id')
    cattle = None
    if cattle_id:
        cattle = Cattle.objects.filter(id=cattle_id).first()

    if not cattle:
        # If no cattle selected, redirect to farm selection
        messages.info(request, 'Please select a farm and cattle first to add a diagnosis.')
        return redirect('select_farms')

    context = {
        'cattle': cattle,
    }
    return render(request, 'systemapp/diagnosis_prescription.html', context)


@login_required(login_url='/systemapp/vet_login/')
def diagnosis_prescription(request, report_id, cattle_id):
    from .models import Diagnosis, Reports
    cattle = get_object_or_404(Cattle, id=cattle_id)
    report = get_object_or_404(Reports, id=report_id)

    if request.method == 'POST':
        observed_date = request.POST.get('observed_date')
        condition_category = request.POST.get('condition_category')
        observation_notes = request.POST.get('observation_notes')
        is_emergency = request.POST.get('is_emergency') == 'on'
        prescription_file = request.FILES.get('prescription_file')

        from .models import IssueReport
        # Create a simple IssueReport to link the diagnosis
        issue = IssueReport.objects.create(
            cattle=cattle,
            reported_by=request.user,
            issue_type='illness',
            original_text=observation_notes or '',
        )

        diagnosis = Diagnosis.objects.create(
            issue_report=issue,
            cattle=cattle,
            observed_date=observed_date,
            condition_category=condition_category,
            observation_notes=observation_notes or '',
            prescription_file=prescription_file,
            is_emergency=is_emergency,
            created_by=request.user,
        )

        messages.success(request, f'Diagnosis recorded for {cattle.tag_id}.')
        return redirect('vet_dashboard')

    context = {
        'cattle': cattle,
        'report': report,
    }
    return render(request, 'systemapp/diagnosis_prescription.html', context)


@login_required(login_url='/systemapp/vet_login/')
def vaccination_reminder(request):
    from .models import Vaccination, RegionalAlert

    q = request.GET.get('q', '')
    active_view = request.GET.get('view', 'all')

    vaccinations = Vaccination.objects.all().order_by('due_date')

    if q:
        vaccinations = vaccinations.filter(
            models.Q(cattle__tag_id__icontains=q) |
            models.Q(cattle__breed__icontains=q) |
            models.Q(cattle__farm__farm_name__icontains=q)
        )

    if active_view == 'high':
        vaccinations = vaccinations.filter(status__in=['due_now', 'upcoming'])
    elif active_view == 'regional':
        vaccinations = vaccinations.all()

    immediate_count = Vaccination.objects.filter(status='due_now').count()
    coming_soon_count = Vaccination.objects.filter(status='upcoming').count()
    routine_count = Vaccination.objects.filter(status='scheduled').count()
    total_count = vaccinations.count()

    context = {
        'vaccinations': vaccinations,
        'q': q,
        'active_view': active_view,
        'immediate_count': immediate_count,
        'coming_soon_count': coming_soon_count,
        'routine_count': routine_count,
        'total_count': total_count,
        'shown_count': vaccinations.count(),
    }
    return render(request, 'systemapp/vaccination_reminder.html', context)


@login_required(login_url='/systemapp/vet_login/')
def schedule_vaccination(request, vaccination_id):
    from .models import Vaccination
    vaccination = get_object_or_404(Vaccination, id=vaccination_id)

    if request.method == "GET":
        initial_date = request.GET.get("scheduled_date") or getattr(vaccination, "scheduled_date", "") or ""
        return render(request, "systemapp/schedule_visit.html", {"vaccination": vaccination, "initial_date": initial_date})

    if request.method == 'POST':
        scheduled_date = request.POST.get('scheduled_date')
        if scheduled_date:
            vaccination.scheduled_date = scheduled_date
            vaccination.status = 'scheduled'
            vaccination.save()
            messages.success(request, f'Vaccination scheduled for {vaccination.cattle.tag_id}.')
        else:
            messages.error(request, 'Please provide a schedule date.')
    return redirect('vaccination_reminder')


@login_required(login_url='/systemapp/vet_login/')
def complete_vaccination(request, vaccination_id):
    from .models import Vaccination
    from django.utils import timezone
    vaccination = get_object_or_404(Vaccination, id=vaccination_id)
    if request.method == 'POST':
        vaccination.status = 'completed'
        vaccination.completed_date = timezone.now().date()
        vaccination.save()
        messages.success(request, f'Vaccination for {vaccination.cattle.tag_id} marked as completed.')
    return redirect('vaccination_reminder')


@login_required(login_url='/systemapp/vet_login/')
def schedule_all_vaccinations(request):
    from .models import Vaccination
    from django.utils import timezone
    if request.method == 'POST':
        pending = Vaccination.objects.filter(status__in=['due_now', 'upcoming'])
        count = 0
        for v in pending:
            if not v.scheduled_date:
                v.scheduled_date = timezone.now().date()
            v.status = 'scheduled'
            v.save()
            count += 1
        messages.success(request, f'{count} vaccinations scheduled.')
    return redirect('vaccination_reminder')


@login_required(login_url='/systemapp/vet_login/')
def select_cattles(request, farm_id, report_id):
    """Alternative cattle selection view that passes a report_id forward."""
    from .models import Farm, Reports
    farm = get_object_or_404(Farm, id=farm_id)
    report = get_object_or_404(Reports, id=report_id)

    cattles = Cattle.objects.filter(farm=farm)
    q = request.GET.get('q', '')
    if q:
        cattles = cattles.filter(
            models.Q(tag_id__icontains=q) |
            models.Q(breed__icontains=q)
        )

    context = {
        'farm': farm,
        'cattles': cattles,
        'report': report,
        'q': q,
    }
    return render(request, 'systemapp/select_cattles.html', context)
