from django.shortcuts import render, redirect
# from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .forms import UserRegisterForm
from .models import Senior
from django.contrib.auth.models import User, auth


# Create your views here.
def main(response):
    return render(response, "scheduling_application/home.html", {})


def login(request):                                                     # created own login form
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('main')
        else:
            messages.info(request, 'invalid credentials')
            return redirect('login')                 # TEMPORARY
    return render(request, 'scheduling_application/login.html', {})


def register(request):                                                  # uses Django's built-in UserRegisterForm
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            # messages.success(request, f'Account created for {username}.')         # resume tutorial for message display on main page
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'scheduling_application/register.html', {'form': form})

def success(response):
    return render(response, "scheduling_application/success.html", {})

def appointment(request):
    seniors_list = Senior.objects.all()
    context = {
        'seniors_list': seniors_list,
    }
    return render(request, 'scheduling_application/appointment.html', context)
