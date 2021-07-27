from django.shortcuts import render, redirect
# from django.contrib.auth.forms import UserCreationForm
# from django.contrib import messages
from .forms import UserRegisterForm

# Create your views here.

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            # messages.success(request, f'Account created for {username}.')         # resume tutorial for message display on main page
            return redirect('register')             # brings user back to register page after account creation (need to change)
    else:
        form = UserRegisterForm()
    return render(request, 'scheduling_application/register.html', {'form': form})