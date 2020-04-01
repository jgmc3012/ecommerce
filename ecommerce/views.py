from django.shortcuts import render
from django.shortcuts import redirect

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth import authenticate

def index(request):
    return render(request, 'index.html', {
        #Context 
    })

def login_view(request):
    print(request.method)
    if request.method == 'POST':
        username = request.POST.get('username') #diccionario
        password = request.POST.get('password') #diccionario

        user = authenticate(username=username, password=password)

        if user:
            login(request, user)
            messages.success(request, 'Bienvenido {}'.format(user.username))
            return redirect('index')
        else:
            messages.error(request, 'Usuario o contraseña invalidos')

    return render(request, 'users/login.html', {
        #context
    })
