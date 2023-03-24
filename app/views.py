import random
import uuid
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib import auth
import cv2

from payment.models import PaymentMethod
from .utils import *
from .forms import *
from .access_decorators import *
from django.db.models import Sum
import stripe
from payment.views import createStripeCustomer




global vacant_slots

vacant_slots = [int(i) for  i in range(1,11)]



stripe.api_key = settings.STRIPE_SECRET_KEY



# Create your views here.


def homepage(request):
    return render(request,'UserSide/index.html')


@guest_user
def register(request):
    return render(request,'UserSide/register.html')

@authenticated_user
def VacantSlot(request):
    
    global vacant_slots
    print("V slots :: ", vacant_slots)

    return render(request, 'admin_pages/admin_page3.html', {"vslots":vacant_slots})


@authenticated_user
def PaymentStatus(request):
    data = {
        "payment_status":"success"
    }

    print("Data :: ", data)

    return render(request,'UserSide/payment_status.html', data)


def AdminView(request, pno):

    print("\n\nAdminView !")

    if pno == "1":
        return render(request, 'admin_pages/admin.html')
    elif pno == "2":
        return render(request, 'admin_pages/admin_page2.html')
    elif pno == "3":
        return render(request, 'admin_pages/admin_page3.html')
    else:
        return render(request, 'admin_pages/admin.html')


    # return render(request, 'admin_pages/admin.html')

@authenticated_user
def demo(request, *args, **kargs):
    form = ImagesForm()
    if request.method == 'POST':
        form = ImagesForm(request.POST, request.FILES)
        obj=None
        if form.is_valid():
            obj = form.save()
        return redirect(license_detection, obj.id)
    context = {'form':form}
    return render(request, 'demo.html', context=context)



@authenticated_user
def license_detection(request, id, *args, **kwargs):
    img_obj = Images.objects.filter(id=id).first()
    img_path = cv2.imread(img_obj.img.path)
    plate = None
    output_img, plate = detect_plate(img_path)
    char = segment_characters(plate)

    model_path = str(settings.BASE_DIR)+'/park.h5'

    model = tf.keras.models.load_model(model_path)
    text=show_results(char, model)

    context = {
        'obj':img_obj,
        'text':text,
        'show_info': 'y'
    }

    global vacant_slots

    user_accnt = Accounts.objects.filter(vehicle_no=text).first()

    if user_accnt:
        if len(vacant_slots) == 0:
            context["token"] = "No slots available !"
            context["asl"] = "0"
    
        else:
            i = 0
            while True:
                i+=1
                if i in vacant_slots:
                    vacant_slots.remove(i)
                    context["token"] = i
                    print(vacant_slots)

                    ua = Accounts.objects.filter(user__email=request.user.email).first()
                    new_ve = VehicleEntry.objects.create(user=ua, fair=100, slot_no=i, payment_status="pending")
                    
                    break
        
        context["user_name"] = user_accnt.name
        context["asl"] = "1"



        # print(context)
        

    return render(request, 'demo.html', context)






# # Registration with database
# def signIn(request):
#     global name,email,phone,vehicle_no,password
#     if request.method=="POST":
#         m=sql.connect(host='localhost',user='root',passwd='Dhanu@19',databse='parkify')
#         cursor=m.cursor()
#         d=request.POST
#         for key,value in d.items():
#             if key=="name":
#                 name=value
#             if key=="email":
#                 email=value
#             if key=="phone":
#                 phone=value
#             if key=="vehicle_no":
#                 vehicle_no=value
#             if key=="password":
#                 password=value
        
#         c="insert into users Values('{}','{}','{}','{}','{}')".format(name,email,phone,vehicle_no,password)
#         cursor.execute(c)
#         m.commit()
#     return render(request,'UserSide/register.html')
        


# Registration with database
# @csrf_exempt




@authenticated_user
def Profile(request):

    print("User :: ", request.user)
    accnt = Accounts.objects.filter(email=request.user).first()

    park_history = VehicleEntry.objects.filter(user__email=request.user.email).order_by('-id').values()
    total_amount = park_history.filter(user__email=request.user.email, payment_status="pending").aggregate(Sum('fair'))
    payment_method = PaymentMethod.objects.filter(user__email=request.user.email).first()
    
    print("payment_method :: ", payment_method)
    print("total_amount :: ", total_amount)

    data = {
        "user": accnt,
        "park_history": park_history,
        "total_amount": total_amount['fair__sum'] if total_amount['fair__sum'] is not None else 0,
        "payment_method": payment_method,
    }

    print("\nData :: ", data)

    return render(request,'UserSide/profile.html', data)






@guest_user
def Register(request):
    global name, email, phone, vehicle_no, password


    if request.method == "POST":
        
        data = request.POST
        name = data['name']
        email = data['email']
        password = data['password']
        phone = data['phone']
        vehicle_no = data['vehicle_no']

        tdata = {
            "name": name,
            "email": email,
            "phone": phone,
            "vehicle_no": vehicle_no
        }

        print("\n\n\nData :: ", tdata)

        new_user = User.objects.create_user(username=email, email=email, password=password)
        new_user.save()

        status, customer = createStripeCustomer(tdata)
        if not status:
            return redirect('/register')

        new_acc = Accounts.objects.create(user=new_user, name=name, email=email, phone=phone, vehicle_no=vehicle_no,
                                            stripe_customer_id=customer.id, stripe_customer_response=customer)
        new_acc.save()

        auth.login(request, new_user)
        print("User registered and Login successful !!!")

        # return render(request,'UserSide/profile.html')
        return redirect('/profile')

    # return render(request,'UserSide/register.html')
    # return HttpResponse("GET Method Not Allowed!")
    return redirect('/')


        
@guest_user
def Login(request):
    
    if request.method == "POST":
    
        data = request.POST

        email = data['email']
        password = data['password']

        user = auth.authenticate(username=email, password=password)
        print("auth user :: ", user)

        if user is not None:
            auth.login(request, user)
            print("Login successful !!!")
        
            # return render(request, 'UserSide/profile.html')
            return redirect('/profile')

    # return render(request, 'UserSide/register.html')
    # return HttpResponse("GET Method Not Allowed!")
    return redirect('/')


@authenticated_user
def Logout(request):

    auth.logout(request)

    return redirect('/')



