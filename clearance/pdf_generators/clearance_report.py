from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
from io import BytesIO
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
from io import BytesIO
from django.conf import settings
from django.template.loader import render_to_string
from .utils import get_fonts_css_txt
from clearance.models import Clearance, Department, LabApproval, ClerkApproval, DeptApproval, AdministrativeApproval
import qrcode
import os
from clearance.utils import b64encode
from django.urls import reverse
from django.utils import timezone

def get_clearance_approvals_data(clearance):
    approvals = {
        'academic_depts': [],
        'general_depts': [],
    }
    for dept in Department.objects.exclude(dept_type__in=['administrative', 'hall']).order_by('id'):
        labs = LabApproval.objects.filter(clearance=clearance, lab__in=dept.lab_set.all()).order_by('id')
        approvals['academic_depts'].append(
            {
                'dept_approval': DeptApproval.objects.get(dept=dept, clearance=clearance),
                'lab_approval': labs,
            }
        )
    if hall:=clearance.student.hall:
        approvals['general_depts'].append(
            {
                'dept_approval': DeptApproval.objects.get(dept=hall, clearance=clearance),
                'clerk_approval': ClerkApproval.objects.get(clearance=clearance, dept_approval__dept=hall),
            }
        )
    for dept in Department.objects.filter(dept_type='administrative').order_by('id'):
        approvals['general_depts'].append(
            {
                'dept_approval': DeptApproval.objects.get(dept=dept, clearance=clearance),
                'clerk_approval': ClerkApproval.objects.get(clearance=clearance, dept_approval__dept=dept),
            }
        )
    approvals['principal'] = AdministrativeApproval.objects.get(clearance=clearance, admin_role='principal')
    approvals['cashier'] = AdministrativeApproval.objects.get(clearance=clearance, admin_role='cashier')
    approvals['academic'] = AdministrativeApproval.objects.get(clearance=clearance, admin_role='academic')
    return approvals


def get_qr_code_path(request, clearance):
    clr_id = clearance.id
    code = b64encode(f"{clearance.student.registration}-{clearance.id}")
    qrcode_filepath = settings.BASE_DIR / f'media/temp/reg_{clr_id}.png'
    os.makedirs("media/temp/", exist_ok=True)
    if os.path.exists(qrcode_filepath):
        return qrcode_filepath
    link = request.build_absolute_uri(reverse('clearance:verify_clearance', args=(code,)))
    print(link, flush=1)
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=1,
    )
    qr.add_data(link)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save(qrcode_filepath)
    return qrcode_filepath

def delete_qr(path):
    try:
        os.remove(path)
    except Exception as e:
        print(e, flush=1)   
        

def render_report(request, clearance):
    context = {'clearance': clearance, 'student': clearance.student}
    govt_logo = settings.BASE_DIR/'clearance/pdf_generators/images/bdgovt.png'
    principal_signature = settings.BASE_DIR/'clearance/pdf_generators/images/principal_signature.png'
    cashier_signature = settings.BASE_DIR/'clearance/pdf_generators/images/cashier_signature.jpg'
    qrcode_path = get_qr_code_path(request, clearance)
    context['govt_logo'] = govt_logo
    context['student_photo'] = settings.BASE_DIR / clearance.student.profile_picture.path
    context['approvals'] = get_clearance_approvals_data(clearance)
    context['principal_signature'] = principal_signature
    context['cashier_signature'] = cashier_signature
    context['qrcode'] = qrcode_path
    formatted_time = timezone.now()
    context['server_time'] = formatted_time
    html_text = render_to_string('clearance/pdf_templates/clearance_temp.html', context=context)
    fonts = {
        'roboto': 'Roboto-Regular.ttf',
        'roboto-m': 'Roboto-Medium.ttf',
        'roboto-b': 'Roboto-Bold.ttf',
    }
    font_config = FontConfiguration()
    fonts_css = get_fonts_css_txt(fonts)
    css_filepath = settings.BASE_DIR/f"clearance/pdf_generators/styles/clr_doc.css"
    with open(css_filepath, 'r') as f:
        css_text = f.read()
    html = HTML(string=html_text)
    css = CSS(string=css_text, font_config=font_config)
    css1 = CSS(string=fonts_css, font_config=font_config)
    buffer = BytesIO()
    html.write_pdf(buffer, stylesheets=[css, css1], font_config=font_config)
    delete_qr(qrcode_path)
    return buffer.getvalue()

