from django.shortcuts import render
import stripe
from partkitup import settings
from app.access_decorators import *
from django.views.decorators.csrf import csrf_exempt
from app.models import *
from .models import *
from django.db.models import Sum
from django.http import JsonResponse




stripe.api_key = settings.STRIPE_SECRET_KEY


# Create your views here.



def createStripeCustomer(data, payment_method=None):
    
    try:

        if payment_method is not None:
            customer = stripe.Customer.create(
                email=data["email"],
                payment_method=payment_method,
                description= f"Name :: {data['name']} | Phone :: {data['phone']}",
                name= data["name"],
                metadata={
                    "user_email":data.email,
                    "user_name": data['name'],
                    "user_vehicle_no": data["vehicle_no"]
                }
            )

        else:
            customer = stripe.Customer.create(
                email=data["email"],
                description= f"Name :: {data['name']} | Phone :: {data['phone']}",
                name= data['name'],
                metadata={
                    "user_email":data["email"],
                    "user_name": data['name'],
                    "user_vehicle_no": data["vehicle_no"]
                }
            )

        return True, customer

    except Exception as err:
        print("Error :: ", err)
        return False, "Error occured while creating stripe customer !"


def addStripePaymentMethod(user, pm_id, cus_id):
    
    try:
        response = stripe.PaymentMethod.attach(pm_id, customer=cus_id)
        print("\nresponse :: ", response)

        args = {
            "invoice_settings":{
                'default_payment_method': pm_id
            }
        }

        customer = stripe.Customer.modify(cus_id, **args)

        user.stripe_customer_id = customer.id
        user.stripe_customer_response = customer
        user.save()

        return True, "PaymentMethod attched successfully !"

    except Exception as err:
        print("Error :: ", err)
        return False, "Error occured while attaching payment method to user !"










# Views 

@csrf_exempt
@authenticated_user
def AddRemovePaymentMethod(request, action):

    if action == "form":

        if PaymentMethod.objects.filter(user__email=request.user.email).exists():
            return redirect('/profile')

        return render(request,'UserSide/add_payment_method_form.html')

    if action == "add":
        print("Post Method PaymentMethod !")

        if PaymentMethod.objects.filter(user__email=request.user.email).exists():
            return redirect('/profile')

        rd = request.POST
        print("rd :: ", rd)

        b_addrs = f"{rd['address']} {rd['city']}, {rd['state']}, India. {rd['zip']}"

        payment_method = stripe.PaymentMethod.create(
            type="card",
            card={
                "number": rd['cardnumber'],
                "exp_month": rd['expmonth'],
                "exp_year": rd['expyear'],
                "cvc": rd['cvv'],
            },
            billing_details={
                "address": {
                    "city": rd['city'],
                    "country": "IN",
                    "line1": rd['address'],
                    "line2": "",
                    "postal_code": rd['zip'],
                    "state": rd['state']
                },
                "email": rd['email'],
                "name": rd['fullname'],
                "phone": rd['phone']
            },
            metadata={
                "user_email": rd["email"],
                "user_fullname": rd["fullname"],
                "billing_address": b_addrs
            }
        )
        
        ua = Accounts.objects.filter(user__email=request.user.email).first()


        status, msg = addStripePaymentMethod(ua, payment_method.id, ua.stripe_customer_id)
        if not status:
            return redirect('/profile')
        
        new_pm = PaymentMethod.objects.create(user=ua, billing_address=b_addrs, currency="inr", is_default=True,
                                                name=rd["fullname"], email=rd["email"], phone=rd["phone"],
                                                pm_type="card", name_on_card=rd["cardname"], card_no=rd["cardnumber"], 
                                                exp_month=rd["expmonth"], exp_year=rd["expyear"], cvv_no=rd["cvv"],
                                                stripe_payment_method_id=payment_method.id, stripe_payment_method_response=payment_method)
    
        
        return redirect('/profile')

    elif action == "remove":

        if not PaymentMethod.objects.filter(user__email=request.user.email).exists():
            return redirect('/profile')

        PaymentMethod.objects.filter(user__email=request.user.email).delete()

        return redirect('/profile')


    return redirect('/')



@csrf_exempt
@authenticated_user
def HandlePayment(request, action):


    
    if action == "status":

        pid = request.POST.get('pid')

        print("pid :: ", pid)

        payment_obj = stripe.PaymentIntent.retrieve(
            pid,
        )

        print("Payment Obj :: ", payment_obj)

        state = "processing"
        if payment_obj.status == "succeeded":
            state = "succeeded"

        if payment_obj.status == "failed":
            state = "failed"

        print("state :: ", state)

        return JsonResponse({"success": True, "state": state})



    total_amount = VehicleEntry.objects.filter(user__email=request.user.email, payment_status="pending").aggregate(Sum('fair'))
    amount = total_amount['fair__sum'] if total_amount['fair__sum'] is not None else 0

    pm = PaymentMethod.objects.filter(user__email=request.user.email).first()
    print("\nPM :: ", pm)

    if amount in [None, 0] or pm == None:
        return redirect('/')

    if action == "get":
    
        return render(request, "UserSide/payment_status.html")


    elif action == "pay":

        user = Accounts.objects.filter(user__email=request.user.email).first()

        payment = stripe.PaymentIntent.create(
            customer=user.stripe_customer_id, 
            payment_method=pm.stripe_payment_method_id,
            receipt_email=pm.email,
            currency=pm.currency,
            amount=amount*100,
            confirm=True,
        )

        print("\n\n\npayment :: ", payment)

        data = {
            "success":True, "status":"success",
            "payment_id": payment.id,
            "auth_url": payment['next_action']['use_stripe_sdk']['stripe_js'],
        }


        VehicleEntry.objects.filter(user__email=request.user.email, payment_status="pending").update(payment_status="completed")

        return JsonResponse(data)

    return redirect('/profile')





