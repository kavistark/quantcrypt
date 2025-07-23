from django.shortcuts import render, redirect
from .models import Course, Registration
from django.views.decorators.csrf import csrf_exempt

# Hardcoded valid referral code
VALID_REF_CODE = "L4FAw@AA"

def home(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def courses(request):
    courses = Course.objects.all()
    return render(request, 'courses.html', {'courses': courses})

def register(request):
    courses = Course.objects.all()

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        course_id = request.POST.get('course')
        plan = request.POST.get('plan')
        ref_code = request.POST.get('refcode')
        has_ref = request.POST.get('hasRef')

        course = Course.objects.get(id=course_id)

        has_discount = ref_code == VALID_REF_CODE if has_ref == "yes" else False

        registration = Registration.objects.create(
            name=name,
            email=email,
            phone=phone,
            course=course,
            plan=plan,
            referral_code=ref_code if has_ref == "yes" else "",
            has_discount=has_discount
        )

        return redirect(f'/billing/{registration.id}/')

    return render(request, 'register.html', {'courses': courses})

def billing(request, reg_id):
    try:
        reg = Registration.objects.get(id=reg_id)
    except Registration.DoesNotExist:
        return render(request, 'error.html', {'message': 'Registration not found.'})

    # Normalize plan name to lowercase to match pricing keys
    plan_key = reg.plan.lower() if reg.plan else ""

    # Define base and referral pricing
    prices = {
        'standard': 7000,
        'advanced': 11000
    }
    referral_prices = {
        'standard': 5699,
        'advanced': 9999
    }

    # Safely get prices
    original_price = prices.get(plan_key, 0)
    final_price = referral_prices.get(plan_key, original_price) if reg.has_discount else original_price
    discount = original_price - final_price if reg.has_discount else 0

    context = {
        'student': reg,
        'original_price': original_price,
        'final_price': final_price,
        'discount': discount
    }

    return render(request, 'billing.html', context)


@csrf_exempt
def payment_gateway(request):
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        amount = request.POST.get('amount')
        # You can process or redirect to actual payment gateway here
        return render(request, 'payment.html', {
            'student_id': student_id,
            'amount': amount
        })
    


import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

# Razorpay credentials (you can move to settings.py)
RAZORPAY_KEY_ID = "rzp_test_xxxxxxxxxxxx"
RAZORPAY_KEY_SECRET = "xxxxxxxxxxxxxxxx"

@csrf_exempt
def payment_gateway(request):
    if request.method == "POST":
        student_id = request.POST.get("student_id")
        amount = int(float(request.POST.get("amount")) * 100)  # Convert to paise

        # Create Razorpay client
        client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

        # Create order
        payment = client.order.create({
            "amount": amount,
            "currency": "INR",
            "payment_capture": "1"
        })

        return render(request, "payment.html", {
            "student_id": student_id,
            "amount": amount,
            "razorpay_key": RAZORPAY_KEY_ID,
            "order_id": payment['id']
        })
