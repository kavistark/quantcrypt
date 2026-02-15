from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from .models import (
    Course,
    Registration,
    ProgramRegister,
    ServiceInterest,
)

import razorpay

# =========================
# CONSTANTS
# =========================
VALID_REF_CODE = "L4FAw@AA"

RAZORPAY_KEY_ID = "rzp_test_xxxxxxxxxxxx"
RAZORPAY_KEY_SECRET = "xxxxxxxxxxxxxxxx"


# =========================
# BASIC PAGES
# =========================
def home(request):
    return render(request, "index.html")


def about(request):
    return render(request, "about.html")


def contact(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")
        # You can save or email this later
        messages.success(request, "Message sent successfully!")
        return redirect("contact")

    return render(request, "contact.html")


# =========================
# COURSES
# =========================
def courses(request):
    courses = Course.objects.all()
    return render(request, "courses.html", {"courses": courses})


# =========================
# COURSE REGISTRATION
# =========================
def register(request):
    courses = Course.objects.all()

    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        course_id = request.POST.get("course")
        plan = request.POST.get("plan")
        ref_code = request.POST.get("refcode")
        has_ref = request.POST.get("hasRef")

        course = get_object_or_404(Course, id=course_id)

        has_discount = ref_code == VALID_REF_CODE if has_ref == "yes" else False

        registration = Registration.objects.create(
            name=name,
            email=email,
            phone=phone,
            course=course,
            plan=plan,
            referral_code=ref_code if has_ref == "yes" else "",
            has_discount=has_discount,
        )

        return redirect("billing", reg_id=registration.id)

    return render(request, "register.html", {"courses": courses})


# =========================
# BILLING
# =========================
def billing(request, reg_id):
    reg = get_object_or_404(Registration, id=reg_id)

    plan_key = reg.plan.lower()

    prices = {
        "standard": 7000,
        "advanced": 11000,
    }

    referral_prices = {
        "standard": 5699,
        "advanced": 9999,
    }

    original_price = prices.get(plan_key, 0)
    final_price = (
        referral_prices.get(plan_key, original_price)
        if reg.has_discount
        else original_price
    )

    context = {
        "student": reg,
        "original_price": original_price,
        "final_price": final_price,
        "discount": original_price - final_price,
    }

    return render(request, "billing.html", context)


# =========================
# PAYMENT (RAZORPAY)
# =========================
@csrf_exempt
def payment_gateway(request):
    if request.method == "POST":
        student_id = request.POST.get("student_id")
        amount = int(float(request.POST.get("amount")) * 100)  # paise

        client = razorpay.Client(
            auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET)
        )

        order = client.order.create(
            {
                "amount": amount,
                "currency": "INR",
                "payment_capture": "1",
            }
        )

        return render(
            request,
            "payment.html",
            {
                "student_id": student_id,
                "amount": amount,
                "razorpay_key": RAZORPAY_KEY_ID,
                "order_id": order["id"],
            },
        )


# =========================
# PROGRAM REGISTRATION
# =========================
def program_register(request):
    if request.method == "POST":
        name = request.POST.get("name")
        year = request.POST.get("year")
        college = request.POST.get("college")
        number = request.POST.get("number")
        email = request.POST.get("email")

        if not all([name, year, college, number, email]):
            messages.error(request, "All fields are required.")
            return redirect("program_register")

        if ProgramRegister.objects.filter(email=email).exists():
            messages.error(request, "This email is already registered.")
            return redirect("program_register")

        ProgramRegister.objects.create(
            name=name,
            year=year,
            college=college,
            number=number,
            email=email,
        )

        messages.success(request, "Registration successful!")
        return redirect("registration_success")

    return render(request, "programmer_register_page.html")


def registration_success(request):
    return render(request, "registration_success.html")


def Offer_Program(request):
    return render(request, "offer_program.html")


# =========================
# SERVICES
# =========================
def web_ser(request):
    if request.method == "POST":
        ServiceInterest.objects.create(
            name=request.POST.get("name"),
            email=request.POST.get("email"),
            phone=request.POST.get("phone"),
            service=request.POST.get("service"),
            message=request.POST.get("message"),
        )
        messages.success(request, "We’ll contact you shortly!")

    return render(request, "web_service.html")


def and_ser(request):
    if request.method == "POST":
        ServiceInterest.objects.create(
            name=request.POST.get("name"),
            email=request.POST.get("email"),
            phone=request.POST.get("phone"),
            service=request.POST.get("service"),
            message=request.POST.get("message"),
        )
        messages.success(request, "We’ll contact you shortly!")

    return render(request, "andro_servies.html")
