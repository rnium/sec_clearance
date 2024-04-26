from django.conf import settings
from django.urls import reverse
from django.template.loader import render_to_string
from urllib.parse import urlencode
from django.conf import settings
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.core.exceptions import ValidationError

sendgrid_api_key = settings.SG_API_KEY_1
sendgrid_from_email = settings.SG_FROM_EMAIL


def send_html_email(receiver, subject, body):
    message = Mail(
        from_email=(sendgrid_from_email, "SEC Clearance Portal"),
        to_emails=receiver,
        subject=subject,
        html_content=body)
    
    sg = SendGridAPIClient(sendgrid_api_key)
    response = sg.send(message)
    status = response.status_code
    if status >= 400:
        raise ValidationError("API Error")
    

def send_signup_email(request, invitation):
    email_subject = "Signup Invitation"
    receiver = invitation.user_email
    app_admin_signup = request.build_absolute_uri(reverse("signupadmin"))
    url_params = {"tokenid":invitation.id}
    signup_url = f"{app_admin_signup}?{urlencode(url_params)}"
    email_body = render_to_string('accounts/invitation.html', context={
        "signup_url": signup_url,
        "invitation": invitation
    })
    try:
        send_html_email(receiver, email_subject, email_body)
    except Exception as e:
        return False
    return True    


def send_student_ac_confirmation_email(student):
    email_subject = "Account Verification Confirmation"
    receiver = student.user.email
    if receiver is None:
        return False
    email_body = render_to_string('accounts/student_ac_confirmation.html', context={
        "student": student,
    })
    try:
        send_html_email(receiver, email_subject, email_body)
    except Exception as e:
        return False
    return True


def send_clearance_confirmation_email(student):
    email_subject = "Clearance Approval Confirmation"
    receiver = student.user.email
    if receiver is None:
        return False
    email_body = render_to_string('accounts/clearance_confirmation.html', context={
        "student": student,
    })
    try:
        send_html_email(receiver, email_subject, email_body)
    except Exception as e:
        return False
    return True


def send_admin_stats_email(admin_ac, context):
    email_subject = "Awaiting Task Notification"
    receiver = admin_ac.user.email
    if receiver is None:
        return False
    email_body = render_to_string('accounts/admin_stats_mail.html', context=context)
    try:
        send_html_email(receiver, email_subject, email_body)
    except Exception as e:
        return False
    return True