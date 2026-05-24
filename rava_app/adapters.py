import random
from allauth.account.adapter import DefaultAccountAdapter
from allauth.exceptions import ImmediateHttpResponse
from django.shortcuts import redirect
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

class OTPAccountAdapter(DefaultAccountAdapter):
    def pre_login(self, request, user, **kwargs):
        # Allow login if OTP is already verified in this session
        if request.session.get('otp_verified'):
            # Clear the flag so next login requires OTP again
            del request.session['otp_verified']
            return super().pre_login(request, user, **kwargs)

        # Generate a 6-digit OTP
        otp = str(random.randint(100000, 999999))
        
        # Store OTP and User ID securely in the session
        request.session['login_otp'] = otp
        request.session['login_user_id'] = user.id
        
        # Render HTML and Text templates
        context = {'otp': otp}
        subject = 'Your Rava Studio Login OTP'
        text_content = f'Your one-time password for login is: {otp}\n\nPlease enter this code to access your account.'
        html_content = render_to_string('account/email/otp_email.html', context)
        
        # Send Email
        msg = EmailMultiAlternatives(
            subject,
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            [user.email]
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)
        
        # Abort current login flow and redirect to the OTP verification page
        raise ImmediateHttpResponse(redirect('verify_otp'))
