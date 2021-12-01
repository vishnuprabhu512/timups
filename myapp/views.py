from django.shortcuts import render, redirect
from .models import User, Watch, Contact, Wishlist, Cart,Transaction
from django.http import JsonResponse
from django.conf import settings
from django.core.mail import send_mail
import random
from .paytm import generate_checksum, verify_checksum
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
def initiate_payment(request):
    user = User.objects.get(email=request.session['email'])
    try:
        amount = int(request.POST['amount'])
    except:
        return render(request, 'pay.html', context={'error': 'Wrong Account Details or amount'})

    transaction = Transaction.objects.create(made_by=user, amount=amount)
    transaction.save()
    carts=Cart.objects.filter(user=user,payment_status="Pending")
    for i in carts:
        i.payment_status="Completed"
        i.save()
    merchant_key = settings.PAYTM_SECRET_KEY

    params = (
        ('MID', settings.PAYTM_MERCHANT_ID),
        ('ORDER_ID', str(transaction.order_id)),
        ('CUST_ID', str(user.email)),
        ('TXN_AMOUNT', str(transaction.amount)),
        ('CHANNEL_ID', settings.PAYTM_CHANNEL_ID),
        ('WEBSITE', settings.PAYTM_WEBSITE),
        # ('EMAIL', str(user.email)),
        # ('MOBILE_N0', str(user.mobile)),
        ('INDUSTRY_TYPE_ID', settings.PAYTM_INDUSTRY_TYPE_ID),
        ('CALLBACK_URL', 'http://localhost:8000/callback/'),
        # ('PAYMENT_MODE_ONLY', 'NO'),
    )

    paytm_params = dict(params)
    checksum = generate_checksum(paytm_params, merchant_key)

    transaction.checksum = checksum
    transaction.save()

    paytm_params['CHECKSUMHASH'] = checksum
    print('SENT: ', checksum)
    return render(request, 'redirect.html', context=paytm_params)

@csrf_exempt
def callback(request):
    if request.method == 'POST':
        received_data = dict(request.POST)
        paytm_params = {}
        paytm_checksum = received_data['CHECKSUMHASH'][0]
        for key, value in received_data.items():
            if key == 'CHECKSUMHASH':
                paytm_checksum = value[0]
            else:
                paytm_params[key] = str(value[0])
        # Verify checksum
        is_valid_checksum = verify_checksum(paytm_params, settings.PAYTM_SECRET_KEY, str(paytm_checksum))
        if is_valid_checksum:
            received_data['message'] = "Checksum Matched"
        else:
            received_data['message'] = "Checksum Mismatched"
            return render(request, 'callback.html', context=received_data)
        return redirect('mycart')




def validate_email(request):
    email=request.GET.get('email')
    data={
    'is_email':User.objects.filter(email__iexact=email).exists()
    }
    return JsonResponse(data)

def validate_oldpassword(request):
    oldpassword=request.GET.get('oldpassword')
    data={
    'is_oldpassword':User.objects.filter(password__iexact=oldpassword).exists()
    }
    return JsonResponse(data)


def index(request):
    all_watch = Watch.objects.all()
    try:
        user = User.objects.get(email=request.session['email'])
        if user.usertype == "user":
            return render(request, 'index.html',{'all_watch': all_watch})
        elif user.usertype == "seller":
            return render(request, 'seller_index.html')
    except:
        return render(request, 'index.html',{'all_watch': all_watch})


def about(request):
    return render(request, 'about.html')


def contact(request):
    if request.method == "POST":
        Contact.objects.create(
            name=request.POST['name'],
            email=request.POST['email'],
            mobile=request.POST['mobile'],
            message=request.POST['message']
        )
        msg1 = "Contact Saved Successfully"
        return render(request, 'contact.html', {'msg1': msg1})
    else:
        return render(request, 'contact.html')


def watches(request):
    all_watch = Watch.objects.all()
    return render(request, 'watches.html', {'all_watch': all_watch})


def signup(request):
    if request.method == "POST":

        try:
            User.objects.get(email=request.POST['email'])
            msg2 = "Email Already Registered"
            return render(request, 'signup.html', {'msg2': msg2})
        except:
            if request.POST['password'] == request.POST['cpassword']:
                User.objects.create(
                    usertype=request.POST['usertype'],
                    fname=request.POST['fname'],
                    lname=request.POST['lname'],
                    email=request.POST['email'],
                    mobile=request.POST['mobile'],
                    address=request.POST['address'],
                    password=request.POST['password'],
                    cpassword=request.POST['cpassword'],
                )
                msg1 = "User Sign Up Successfully"
                return render(request, 'login.html', {'msg1': msg1})
            else:
                msg2 = "Password & Confirm Password Does Not Matched"
                return render(request, 'signup.html', {'msg2': msg2})
    else:
        return render(request, 'signup.html')


def login(request):
    if request.method == "POST":
        try:
            user = User.objects.get(
                email=request.POST['email'],
                password=request.POST['password'],
            )
            if user.usertype == "user":
                request.session['fname'] = user.fname
                request.session['email'] = user.email
                wishlists = Wishlist.objects.filter(user=user)
                carts = Cart.objects.filter(user=user)
                request.session['wishlist_count'] = len(wishlists)
                request.session['cart_count'] = len(carts)
                return render(request, 'index.html')
            elif user.usertype == "seller":
                request.session['fname'] = user.fname
                request.session['email'] = user.email
                return render(request, 'seller_index.html')
        except:
            msg2 = "Email or Password Is Incorrect"
            return render(request, 'login.html', {'msg2': msg2})
    else:
        return render(request, 'login.html')


def logout(request):
    try:
        del request.session['fname']
        del request.session['email']
        del request.session['wishlist_count']
        del request.session['cart_count']
        return render(request, 'login.html')
    except:
        return render(request, 'login.html')


def seller_index(request):
    return render(request, 'seller_index.html')


def add_watches(request):
    if request.method == "POST":
        watch_seller = User.objects.get(email=request.session['email'])
        Watch.objects.create(
            watch_seller=watch_seller,
            watch_brand=request.POST['watch_brand'],
            watch_model=request.POST['watch_model'],
            watch_desc=request.POST['watch_desc'],
            watch_price=request.POST['watch_price'],
            watch_image=request.FILES['watch_image'],
        )
        msg1 = "Watch Added Successfully"
        return render(request, 'add_watches.html', {'msg1': msg1})
    else:
        return render(request, 'add_watches.html')


def view_watches(request):
    watch_seller = User.objects.get(email=request.session['email'])
    watches = Watch.objects.filter(watch_seller=watch_seller)
    return render(request, 'view_watches.html', {'watches': watches})


def watch_detail(request, pk):
    watch = Watch.objects.get(pk=pk)
    return render(request, 'watch_detail.html', {'watch': watch})


def user_watch_detail(request, pk):
    wishlist_flag = False
    cart_flag=False
    watch = Watch.objects.get(pk=pk)
    user = User.objects.get(email=request.session['email'])
    try:
        Wishlist.objects.get(user=user, watch=watch)
        wishlist_flag = True
    except:
        pass
    try:
        Cart.objects.get(user=user, watch=watch)
        cart_flag = True
    except:
        pass
    return render(request, 'user_watch_detail.html', {'watch': watch, 'wishlist_flag': wishlist_flag,'cart_flag':cart_flag})


def watch_edit(request, pk):
    watch = Watch.objects.get(pk=pk)
    if request.method == "POST":
        watch.watch_model = request.POST['watch_model']
        watch.watch_desc = request.POST['watch_desc']
        watch.watch_price = request.POST['watch_price']
        try:
            watch.watch_image = request.FILES['watch_image']
        except:
            pass
        watch.save()
        return render(request, 'watch_detail.html', {'watch': watch})
    else:
        return render(request, 'watch_edit.html', {'watch': watch})


def watch_delete(request, pk):
    watch = Watch.objects.get(pk=pk)
    watch.delete()
    return redirect('view_watches')


def add_to_wishlist(request, pk):
    watch = Watch.objects.get(pk=pk)
    user = User.objects.get(email=request.session['email'])
    Wishlist.objects.create(
        user=user,
        watch=watch,
    )
    all_watch = Watch.objects.all()
    return redirect('mywishlist')


def mywishlist(request):
    user = User.objects.get(email=request.session['email'])
    wishlists = Wishlist.objects.filter(user=user)
    request.session['wishlist_count'] = len(wishlists)
    return render(request, 'mywishlist.html', {'wishlists': wishlists})


def remove_from_wishlist(request, pk):
    watch = Watch.objects.get(pk=pk)
    user = User.objects.get(email=request.session['email'])
    wishlist = Wishlist.objects.get(user=user, watch=watch)
    wishlist.delete()
    return redirect('mywishlist')

def mycart(request):
    net_price=0
    user=User.objects.get(email=request.session['email'])
    carts=Cart.objects.filter(user=user,payment_status="Pending")
    request.session['cart_count'] = len(carts)
    for i in carts:
        net_price=net_price+i.total_price
    
    return render(request,'mycart.html',{'carts':carts,'net_price':net_price})

def add_to_cart(request,pk):
    watch=Watch.objects.get(pk=pk)
    user=User.objects.get(email=request.session['email'])
    Cart.objects.create(
        user=user,
        watch=watch,
        price=watch.watch_price,
        total_price=watch.watch_price
    )
    return redirect('mycart')

def remove_from_cart(request, pk):
    watch = Watch.objects.get(pk=pk)
    user = User.objects.get(email=request.session['email'])
    cart = Cart.objects.get(user=user, watch=watch)
    cart.delete()
    return redirect('mycart')

def change_qty(request):
    cart=Cart.objects.get(pk=request.POST['cart_id'])
    qty=int(request.POST['qty'])
    cart.qty=qty
    cart.total_price=qty*cart.price
    cart.save()
    return redirect('mycart')

def forgot_password(request):
    if request.method=="POST":
        email=request.POST['email']
        try:
            user=User.objects.get(email=email)
            otp=random.randint(100000,999999)
            subject = "OTP : "+str(otp)
            message = "Use the OTP to Forgot Password : "+str(otp)+".\n\nYou received this email because you requested to Forgot Password to your ID. If you didn\'t request to Forgot Password, you can safely ignore this email."
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [user.email, ]
            send_mail( subject, message, email_from, recipient_list)
            return render(request,'otp.html',{'otp':otp,'email':email})
        except:
            msg2="Email Not Registered"
            return render(request,'forgot_password.html',{'msg2':msg2})
    else:
        return render(request,'forgot_password.html')

def otp(request):
    otp=request.POST['otp']
    uotp=request.POST['uotp']
    email=request.POST['email']
    if otp==uotp:
        return render(request,'new_password.html',{'email':email})

    else:
        msg2="Entered OTP Is Invalid"
        return render(request,'otp.html',{'otp':otp,'email':email,'msg2':msg2})

def new_password(request):
    email=request.POST['email']
    password=request.POST['password']
    cpassword=request.POST['cpassword']

    if password==cpassword:
        user=User.objects.get(email=email)
        user.password=password
        user.cpassword=password
        user.save()
        msg1="Password Updated Successfully"
        return render(request,'login.html',{'msg1':msg1})

    else:
        msg2="Password & Confirm Password Does Not Matched"
        return render(request,'new_password.html',{'email':email,'msg2':msg2})

def profile(request):
    user=User.objects.get(email=request.session['email'])
    if request.method=="POST":
        user.fname=request.POST['fname']
        user.lname=request.POST['lname']
        user.email=request.POST['email']
        user.mobile=request.POST['mobile']
        user.address=request.POST['address']
        user.save()
        msg1="Profile Updated Successfully"
        return render(request,'profile.html',{'user':user,'msg1':msg1})
    else:
        return render(request,'profile.html',{'user':user})

def change_password(request):
    if request.method=="POST":
        user=User.objects.get(email=request.session['email'])
        if user.password==request.POST['old_password']:
            if request.POST['new_password']==request.POST['cnew_password']:
                user.password=request.POST['new_password']
                user.cpassword=request.POST['new_password']
                user.save()
                return redirect('logout')
            else:
                msg2="New Password & Confirm New Password Does Not Matched"
                return render(request,'change_password.html',{'msg2':msg2})
        else:
            msg2="Old Password is Incorrect"
            return render(request,'change_password.html',{'msg2':msg2})
    else:
        return render(request,'change_password.html')

def myorder(request):
    user=User.objects.get(email=request.session['email'])
    carts=Cart.objects.filter(user=user,payment_status="Completed")
    return render(request,'myorder.html',{'carts':carts})


