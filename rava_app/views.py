import random
import json
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.http import JsonResponse
from .jwt_utils import generate_tokens, decode_token

User = get_user_model()

def custom_signup(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')

        if password != password_confirm:
            messages.error(request, "Passwords do not match.")
            return render(request, 'account/signup.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "A user with this email already exists.")
            return render(request, 'account/signup.html')
            
        # Create user
        user = User.objects.create_user(username=username, email=email, password=password)
        messages.success(request, "Account created successfully. Please sign in.")
        return redirect('account_login')

    return render(request, 'account/signup.html')


def custom_login(request):
    if request.method == 'POST':
        email = request.POST.get('login', '').strip() # the template uses 'login' for email field
        password = request.POST.get('password', '')
        
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            # Generate a 6-digit OTP
            otp = str(random.randint(100000, 999999))
            
            # Store OTP and User ID securely in the session for the verification step
            request.session['login_otp'] = otp
            request.session['login_user_id'] = user.id
            
            # Send Email
            context = {'otp': otp}
            subject = 'Your Rava Studio Login OTP'
            text_content = f'Your one-time password for login is: {otp}\n\nPlease enter this code to access your account.'
            html_content = render_to_string('account/email/otp_email.html', context)
            
            msg = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, [user.email])
            msg.attach_alternative(html_content, "text/html")
            msg.send(fail_silently=False)
            
            return redirect('verify_otp')
        else:
            messages.error(request, "Invalid email or password.")
            
    return render(request, 'account/login.html')


def verify_otp(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp', '').strip()
        session_otp = request.session.get('login_otp')
        user_id = request.session.get('login_user_id')
        
        if entered_otp and entered_otp == session_otp and user_id:
            try:
                user = User.objects.get(id=user_id)
                # Clean up session OTP
                del request.session['login_otp']
                del request.session['login_user_id']
                
                # Log the user in for Django session compatibility just in case,
                # though our JWT middleware handles request.user
                login(request, user)
                
                # Generate JWT tokens
                access_token, refresh_token = generate_tokens(user)
                
                # Redirect and set cookies
                response = redirect('studio')
                response.set_cookie('access_token', access_token, httponly=True, secure=not settings.DEBUG, samesite='Lax')
                response.set_cookie('refresh_token', refresh_token, httponly=True, secure=not settings.DEBUG, samesite='Lax')
                return response
            except User.DoesNotExist:
                messages.error(request, "User not found.")
                return redirect('account_login')
        else:
            messages.error(request, "Invalid or expired OTP. Please try again.")
            
    if not request.session.get('login_otp'):
        return redirect('account_login')
        
    return render(request, 'account/verify_otp.html')


def custom_logout(request):
    logout(request)
    response = redirect('home')
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')
    return response


def refresh_token_endpoint(request):
    """
    API Endpoint to refresh the access token.
    Reads refresh_token from cookie or JSON body.
    """
    if request.method == 'POST':
        refresh_token = request.COOKIES.get('refresh_token')
        
        if not refresh_token:
            try:
                data = json.loads(request.body)
                refresh_token = data.get('refresh_token')
            except Exception:
                pass
                
        if not refresh_token:
            return JsonResponse({'error': 'Refresh token missing'}, status=400)
            
        payload = decode_token(refresh_token)
        if payload and payload.get('type') == 'refresh':
            try:
                user = User.objects.get(id=payload['user_id'])
                access_token, new_refresh_token = generate_tokens(user)
                
                response = JsonResponse({
                    'access_token': access_token,
                    'refresh_token': new_refresh_token
                })
                response.set_cookie('access_token', access_token, httponly=True, secure=not settings.DEBUG, samesite='Lax')
                response.set_cookie('refresh_token', new_refresh_token, httponly=True, secure=not settings.DEBUG, samesite='Lax')
                return response
            except User.DoesNotExist:
                return JsonResponse({'error': 'User not found'}, status=401)
                
        return JsonResponse({'error': 'Invalid or expired refresh token'}, status=401)
        
    return JsonResponse({'error': 'Method not allowed'}, status=405)
