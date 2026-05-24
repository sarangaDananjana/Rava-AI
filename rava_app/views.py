from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from allauth.account.utils import perform_login
from django.contrib import messages

def verify_otp(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp', '').strip()
        session_otp = request.session.get('login_otp')
        user_id = request.session.get('login_user_id')
        
        if entered_otp and entered_otp == session_otp and user_id:
            User = get_user_model()
            try:
                user = User.objects.get(id=user_id)
                # Set flag so pre_login adapter allows it through
                request.session['otp_verified'] = True
                
                # Clean up session OTP variables securely
                del request.session['login_otp']
                del request.session['login_user_id']
                
                # Resume allauth login
                return perform_login(request, user, email_verification='none')
            except User.DoesNotExist:
                messages.error(request, "User not found.")
                return redirect('account_login')
        else:
            messages.error(request, "Invalid or expired OTP. Please try again.")
            
    # GET request
    if not request.session.get('login_otp'):
        return redirect('account_login')
        
    return render(request, 'account/verify_otp.html')
