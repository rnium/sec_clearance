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


def get_clearance_approvals_data(clearance):
    approvals = {
        'academic_depts': [],
        'general_depts': [],
    }
    for dept in Department.objects.exclude(dept_type='administrative').order_by('id'):
        labs = LabApproval.objects.filter(clearance=clearance, lab__in=dept.lab_set.all()).order_by('id')
        approvals['academic_depts'].append(
            {
                'dept_approval': DeptApproval.objects.get(dept=dept, clearance=clearance),
                'lab_approval': labs,
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

        
        

def render_report(clearance):
    context = {'clearance': clearance, 'student': clearance.student}
    govt_logo = settings.BASE_DIR/'clearance/pdf_generators/images/bdgovt.png'
    principal_signature = settings.BASE_DIR/'clearance/pdf_generators/images/principal_signature.png'
    context['govt_logo'] = govt_logo
    context['student_photo'] = settings.BASE_DIR / clearance.student.profile_picture.path
    context['approvals'] = get_clearance_approvals_data(clearance)
    context['principal_signature'] = principal_signature
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
    return buffer.getvalue()

