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
from .models import Document, DocumentShare
@login_required(login_url='login')
def admin_dashboard(request):
    if not request.user.is_staff:
        return redirect('dashboard')

    total_users = User.objects.count()
    total_documents = Document.objects.count()

    users = User.objects.all().order_by('-date_joined')

    return render(request, 'vault/admin_dashboard.html', {
        'total_users': total_users,
        'total_documents': total_documents,
        'users': users,
    })
def home(request):
    return render(request, 'vault/home.html')
def login(request):
    selected_role = request.GET.get('role', 'owner').lower()

    if request.method == 'POST':
        selected_role = request.POST.get('role', 'owner').lower()
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if not user:
            return render(request, 'vault/login.html', {
                'error': 'Invalid username or password!',
                'role': selected_role
            })

        if selected_role == 'admin' and not user.is_staff:
            return render(request, 'vault/login.html', {
                'error': 'Admin access restricted.',
                'role': selected_role
            })

        if selected_role in ['owner', 'viewer'] and user.is_staff:
            return render(request, 'vault/login.html', {
                'error': 'Please use Admin login.',
                'role': selected_role
            })

        if selected_role not in ['admin', 'owner', 'viewer']:
            selected_role = 'owner'

        auth_login(request, user)
        request.session['role'] = selected_role

        if selected_role == 'admin':
            return redirect('admin_dashboard')

        return redirect('dashboard')

    return render(request, 'vault/login.html', {
        'role': selected_role
    })
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
    search_query = request.GET.get('search', '')
    role = request.session.get('role', 'owner')

    if role == 'viewer':
        shared_ids = DocumentShare.objects.filter(
            viewer=request.user
        ).values_list('document_id', flat=True)

        documents = Document.objects.filter(id__in=shared_ids)
    else:
        documents = Document.objects.filter(user=request.user)

    if search_query:
        documents = documents.filter(title__icontains=search_query)

    documents = documents.order_by('-uploaded_at')

    return render(request, 'vault/dashboard.html', {
        'documents': documents,
        'role': role
    })
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
    role = request.session.get('role', 'owner')

    if role == 'viewer':
        document = get_object_or_404(
            Document,
            id=document_id,
            shares__viewer=request.user
        )
    else:
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