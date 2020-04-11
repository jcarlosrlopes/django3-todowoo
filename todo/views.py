from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.utils import timezone
from .forms import TodoForm
from .models import Todo
from django.contrib.auth.decorators import login_required

def home(request):
    return render(request, 'todo/home.html')

def signupuser(request):
    if request.method == 'GET':
        return render(request, 'todo/signupuser.html', { 'form': UserCreationForm() })
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(request.POST['username'],password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('currenttodos')
            except IntegrityError:
                error_message = 'The username has already been taken. Please choose a new one.'
                return render(request, 'todo/signupuser.html', { 'error_message': error_message, 'form': UserCreationForm() })
        else:
            error_message = 'The password and confirmation must be equal'
            return render(request, 'todo/signupuser.html', { 'error_message': error_message, 'form': UserCreationForm() })

def loginuser(request):
    if request.method == 'GET':
        return render(request, 'todo/loginuser.html', { 'form': AuthenticationForm() })
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])

        if user is None:
            return render(request, 'todo/loginuser.html', { 'form': AuthenticationForm(), 'error_message': 'Username and password did not match!' })
        else:
            login(request, user)
            return redirect('currenttodos')

@login_required
def logoutuser(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')

@login_required
def createtodo(request):
    if request.method == 'GET':
        return render(request, 'todo/createtodo.html', { 'form': TodoForm() })
    else:
        try:
            form = TodoForm(request.POST)
            newtodo = form.save(commit=False)
            newtodo.user = request.user
            newtodo.save()
            return redirect('currenttodos')
        except ValueError:
            return render(request, 'todo/createtodo.html', { 'form': TodoForm(), 'error_message': 'Bad data passed in' })

@login_required
def currenttodos(request):
    user_todos = Todo.objects.filter(user=request.user, date_completed__isnull=True)
    return render(request, 'todo/currenttodos.html', { 'todos': user_todos })

@login_required
def completedtodos(request):
    user_todos = Todo.objects.filter(user=request.user, date_completed__isnull=False).order_by('-date_completed')
    return render(request, 'todo/completedtodos.html', { 'todos': user_todos })

@login_required
def viewtodo(request, todo_id):
    todo = get_object_or_404(Todo,pk=todo_id,user=request.user)
    if request.method == 'GET':
        form = TodoForm(instance=todo)
        return render(request, 'todo/viewtodo.html', { 'todo': todo, 'form': form })
    else:
        try:
            form = TodoForm(request.POST, instance=todo)
            form.save()
            return redirect('currenttodos')
        except ValueError:
            return render(request, 'todo/viewtodo.html', { 'todo': todo, 'form': form, 'error_message': 'Bad info' })

@login_required
def completetodo(request, todo_id):
    todo = get_object_or_404(Todo,pk=todo_id,user=request.user)
    if request.method == 'POST':
        todo.date_completed = timezone.now()
        todo.save()
        return redirect('currenttodos')

@login_required
def deletetodo(request, todo_id):
    todo = get_object_or_404(Todo,pk=todo_id,user=request.user)
    if request.method == 'POST':        
        todo.delete()
        return redirect('currenttodos')