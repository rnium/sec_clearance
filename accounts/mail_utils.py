import sib_api_v3_sdk
from django.conf import settings
from django.urls import reverse
from django.template.loader import render_to_string
from urllib.parse import urlencode
from django.conf import settings
from sib_api_v3_sdk import SendSmtpEmail, SendSmtpEmailSender, SendSmtpEmailTo


brevo_from_user = settings.BREVO_FROM_EMAIL
brevo_api_key = settings.BREVO_API_KEY_1

configuration = sib_api_v3_sdk.Configuration()
configuration.api_key['api-key'] = brevo_api_key
api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

# Email sender information
sender = SendSmtpEmailSender(name="SEC Clearance Portal", email=brevo_from_user)



def send_html_email(receiver_email, subject, body):
    recipient = SendSmtpEmailTo(email=receiver_email, name="User")
    send_smtp_email = SendSmtpEmail(
        sender=sender,
        to=[recipient],
        html_content=body,
        subject=subject
    )
    api_instance.send_transac_email(send_smtp_email)
    

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
    email_body = render_to_string('accounts/student_ac_confirmation.html', context={
        "student": student,
    })
    try:
        send_html_email(receiver, email_subject, email_body)
    except Exception as e:
        return False
    return True