from email import message
from email.message import EmailMessage
from lib2to3.pgen2.token import tok_name
from django.shortcuts import render,redirect



from .forms import RegistrationForm
from .models import Account
from django.contrib import messages,auth
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import  render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.core.mail import EmailMessage 
import requests


##from django.contrib.auth import get_user_model


# Create your views here.

def  register(request):
    ##https://stackoverflow.com/questions/47814228/django-2-python-3-4-cannot-decode-urlsafe-base64-decodeuidb64
    form=RegistrationForm()
  
    if request.method=='POST':
        form=RegistrationForm(request.POST)
    
     
        if form.is_valid()  :
            first_name=form.cleaned_data['first_name']      
            last_name=form.cleaned_data['last_name']
            phone_number=form.cleaned_data['phone_number']
            email=form.cleaned_data['email']
            password=form.cleaned_data['password']
            vaux=email.split("@")
            username=vaux[0]
            user=Account.objects.create_user(first_name=first_name,last_name=last_name,username=username,email=email,password=password)
            user.phone_number=phone_number
            user.save()
          
   
            
           
            messages.success(request,'Se registro el usuario exitosamente')

            current_site= get_current_site(request)
            mail_subject="Por favor activa tu cuenta"
         
            miUid =  urlsafe_base64_encode(force_bytes(user.pk)) 
            token= default_token_generator.make_token(user)
        

            body=render_to_string('accounts/account_verification_email.html',{
                'user':user,
                'domain':current_site,
                'uid':miUid,
                 'token':token
            })
            to_email=email
            send_email=EmailMessage(mail_subject,body,to=[to_email])
            send_email.send()

            # return redirect("register")
            return redirect("/accounts/login/?command=verification&email="+email)
            #return redirect("login")
        else:
            print("no valida")


   

    context={
        'form':form
    }
    return render(request,"accounts/register.html",context)


def  login(request):
    if request.method=='POST':
        email=request.POST['email']
        password=request.POST['password']
        user=auth.authenticate(email=email,password=password)
        print(user)
        if user is not None:
            auth.login(request,user)
            messages.success(request,"Te has conectado exitosamente")


            url = request.META.get("HTTP_REFERER")
            query=requests.utils.urlparse(url).query

            if query :
                params=dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    siguiente= params['next']
                    return redirect(siguiente)
                else:
                    return render(request,"presentacion.html")
            else:
                messages.error(request,"Intente nuevamente")
                return redirect("login")
        else:
            messages.error(request,"Usuario y clave no corresponden")
            return redirect("login")

    return render(request,"accounts/login.html")


@login_required(login_url='login')
def  logout(request):
    auth.logout(request)
    messages.success(request,"Te extrañaremos")
    return redirect('login')



def activate(request,uidb64,token):
    assert uidb64 is not None and token is not None 
    try:
        uid2=urlsafe_base64_decode(uidb64).decode()
        user=Account._default_manager.get(pk=uid2)
   
      
       
        ##UserModel = get_user_model()
        ##user = UserModel._default_manager.get(pk=uid2)

    except TypeError:
        print("Type")
        user=None
    except ValueError:
        print("value")
        user=None
    except OverflowError:
        print("overflow") 
        user=None
    except Account.DoesNotExist:
        print("No existe")
        user=None


  



    genera=default_token_generator.check_token(user,token)

    if user is not None and genera:
        user.is_active=True
        user.save()
        
        messages.success(request,"Felicidades tu cuenta esta activa")
        return redirect("login")
    else:
        messages.error(request,"No se pudo activar la cuenta")
        return redirect("register")

@login_required(login_url='login')



def forgotpassword(request):
    if request.method=='POST':
        email=request.POST['email']
        if Account.objects.filter(email=email).exists():
            user= Account.objects.get(email__exact=email)

            current_site= get_current_site(request)
            mail_subject="Resetear Password"
            miUid =  urlsafe_base64_encode(force_bytes(user.pk)) 
            token= default_token_generator.make_token(user)

            body=render_to_string('accounts/reset_password_email.html',{
                'user':user,
                'domain':current_site,
                'uid':miUid,
                 'token':token
            })
            to_email=email
            send_email=EmailMessage(mail_subject,body,to=[to_email])
            send_email.send()
            messages.success(request,"se envío un correo,para resetear tu password")
            return redirect("login")
        else:
            messages.error(request,'la cuenta de usuario no existe')
            return redirect("forgotpassword")



        
    return render (request,"accounts/forgotpassword.html")

def  resetpassword_validate(request,uidb64,token):
    assert uidb64 is not None and token is not None 
    try:
        uid=urlsafe_base64_decode(uidb64).decode()
        user=Account._default_manager.get(pk=uid)
    except TypeError:
        print("Type")
        user=None
    except ValueError:
        print("value")
        user=None
    except OverflowError:
        print("overflow") 
        user=None
    except Account.DoesNotExist:
        print("No existe")
        user=None

    genera=default_token_generator.check_token(user,token)
    if user is not None and genera:
        
        request.session['uid']=uid
        messages.success(request,"Por favor resetea tu cuenta")
        return redirect("resetpassword")
    else:
        messages.error(request,"El link ha expirado")
        return redirect("login")

def resetpassword(request):
    if request.method=='POST':
        password=request.POST['password']
        confirm_password= request.POST['confirm_password']
        if password==confirm_password:
            uid= request.session['uid']
            user=Account._default_manager.get(pk=uid)
            user.set_password(password)
            messages.success(request,'Clave reseteada correctamente')
            return redirect("login")
        else:
            messages.error(request,'las claves no concuerdan')
            return redirect("resetpassword")
    else:
        return render(request,'accounts/resetpassword.html')