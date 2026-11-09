from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from .models import Document
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
import os
from django.contrib import messages
from django.http import HttpResponseBadRequest

def home(request):
    return render(request, 'vault/home.html')
def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            return redirect('dashboard')

        return render(request, 'vault/login.html',
                      {'error': 'Invalid username or password!'})

    return render(request, 'vault/login.html')
def signup(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            return render(request, 'vault/signup.html',
                          {'error': 'Passwords do not match!'})

        if User.objects.filter(username=username).exists():
            return render(request, 'vault/signup.html',
                          {'error': 'Username already exists!'})

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        user.first_name = full_name
        user.save()

        return redirect('login')

    return render(request, 'vault/signup.html')
@login_required(login_url='login')
@login_required(login_url='login')
def dashboard(request):
    search_query = request.GET.get('search')

    documents = Document.objects.filter(user=request.user)

    if search_query:
        documents = documents.filter(title__icontains=search_query)

    documents = documents.order_by('-uploaded_at')

    return render(request, 'vault/dashboard.html', {'documents': documents})
def logout(request):
    auth_logout(request)
    return redirect('home')
@login_required(login_url='login')
def upload_document(request):
    if request.method != 'POST':
        return redirect('dashboard')

    title = request.POST.get('title', '').strip()
    file = request.FILES.get('file')

    allowed_extensions = [
        '.pdf', '.docx', '.txt',
        '.jpg', '.jpeg', '.png'
    ]

    if not title or not file:
        return redirect('dashboard')

    extension = os.path.splitext(file.name)[1].lower()

    if extension not in allowed_extensions:
        return HttpResponseBadRequest('File type not allowed.')

    if file.size > 5 * 1024 * 1024:
        return HttpResponseBadRequest('File size must be below 5 MB.')

    Document.objects.create(
        user=request.user,
        title=title,
        file=file
    )

    return redirect('dashboard')
@login_required(login_url='login')
def delete_document(request, document_id):
    if request.method == 'POST':
        document = Document.objects.get(
            id=document_id,
            user=request.user
        )
        document.file.delete()
        document.delete()

    return redirect('dashboard')
@login_required(login_url='login')
def download_document(request, document_id):
    document = get_object_or_404(
        Document,
        id=document_id,
        user=request.user
    )

    return FileResponse(
        document.file.open('rb'),
        as_attachment=True,
        filename=document.file.name.split('/')[-1]
    )
@login_required(login_url='login')
def profile(request):
    return render(request, 'vault/profile.html')
def about(request):
    return render(request, 'vault/about.html')


def help_page(request):
    return render(request, 'vault/help.html')