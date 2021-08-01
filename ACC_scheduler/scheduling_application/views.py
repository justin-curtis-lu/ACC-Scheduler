from django.shortcuts import render, redirect
# from django.contrib.auth.forms import UserCreationForm
# from django.contrib import messages
from .forms import UserRegisterForm
from .models import Senior


# Create your views here.
def main(response):
    return render(response, "scheduling_application/home.html", {})


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            # messages.success(request, f'Account created for {username}.')         # resume tutorial for message display on main page
            return redirect('account_created')             # brings user back to register page after account creation (need to change)
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
