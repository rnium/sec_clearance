from typing import Any, Optional
from django.core.management.base import BaseCommand, CommandError
from clearance.models import Department, Lab

departments = {
    'cse': {
        'meta': {
            'codename': 'cse',
            'name': 'Computer Science Engineering',
            'display_name': 'Department of CSE',
            'dept_type': 'academic'
        },
        'labs': [
            {
                'codename': 'software_1_lab',
                'name': 'Software-1 Lab',
            },
            {
                'codename': 'software_2_lab',
                'name': 'Software-2 Lab',
            },
            {
                'codename': 'dld_lab_cse',
                'name': 'DLD Lab',
            },
            {
                'codename': 'mp_lab',
                'name': 'Microprocessor Lab',
            },
            {
                'codename': 'net_lab',
                'name': 'Networking Lab',
            },
            {
                'codename': 'atts_lab_cse',
                'name': 'ATTS Lab',
            },
        ]
    },
    'ce': {
        'meta': {
            'codename': 'ce',
            'name': 'Civil Engineering',
            'display_name': 'Department of CE',
            'dept_type': 'academic'
        },
        'labs': [
            {
                'codename': 'atts_lab_ce',
                'name': 'ATTS Lab',
            },
            {
                'codename': 'env_eng_lab',
                'name': 'Environment Engineering Lab',
            },
            {
                'codename': 'geo_eng_lab',
                'name': 'Geotechnical And Engineering Materials Lab',
            },
            {
                'codename': 'hydraulic_lab',
                'name': 'Hydraulic Lab',
            },
            {
                'codename': 'machine_shop',
                'name': 'Machine Shop',
            },
            {
                'codename': 'structure_lab',
                'name': 'Structure Lab',
            },
            {
                'codename': 'surveying_lab',
                'name': 'Surveying Lab',
            },
            {
                'codename': 'transportation_lab',
                'name': 'Transportation Lab',
            },
            {
                'codename': 'wfw_shop',
                'name': 'Welding, Foundry & Wood Shop',
            },
        ]
    },
    'eee': {
        'meta': {
            'codename': 'eee',
            'name': 'Electrical and Electronic Engineering',
            'display_name': 'Department of EEE',
            'dept_type': 'academic'
        },
        'labs': [
            {
                'codename': 'ckt_lab',
                'name': 'Electrical Circuit Lab',
            },
            {
                'codename': 'electronics_lab',
                'name': 'Electronics Lab',
            },
            {
                'codename': 'dld_lab',
                'name': 'DLD Lab',
            },
            {
                'codename': 'machine_lab',
                'name': 'Electrical Machine',
            },
            {
                'codename': 'hv_lab',
                'name': 'High Voltage Lab',
            },
            {
                'codename': 'atts_lab_eee',
                'name': 'ATTS Lab',
            },
        ]
    },
    'non-tech': {
        'meta': {
            'codename': 'non-tech',
            'name': 'Non-Tech Department',
            'display_name': 'Non-Tech Department',
            'dept_type': 'accessory',
        },
        'labs': [
            {
                'codename': 'phy_lab',
                'name': 'Physics Lab',
            },
            {
                'codename': 'chem_lab',
                'name': 'Chemistry Lab',
            },
        ]
    },
    'security_dept': {
        'meta': {
            'codename': 'security_dept',
            'name': 'Security Department',
            'display_name': 'Security Department',
            'dept_type': 'administrative',
            'head_title': 'In Charge',
        },
        'labs': []
    },
    'library': {
        'meta': {
            'codename': 'library',
            'name': 'Library',
            'display_name': 'Library',
            'dept_type': 'administrative',
            'head_title': 'In Charge',
        },
        'labs': []
    },
    'general_section': {
        'meta': {
            'codename': 'general_section',
            'name': 'General Section',
            'display_name': 'General Section',
            'dept_type': 'administrative',
            'head_title': 'In Charge',
        },
        'labs': []
    },
    'cash_section': {
        'meta': {
            'codename': 'cash_section',
            'name': 'Cash Section',
            'display_name': 'Cash Section',
            'dept_type': 'administrative',
            'head_title': 'In Charge',
        },
        'labs': []
    },
    'general_store': {
        'meta': {
            'codename': 'general_store',
            'name': 'General Store',
            'display_name': 'General Store',
            'dept_type': 'administrative',
            'head_title': 'In Charge',
        },
        'labs': []
    },
    'office_of_the_hall_provost_bangamata ': {
        'meta': {
            'codename': 'office_of_the_hall_provost_bangamata',
            'name': 'Office of The Hall Provost (Bangamata Hall)',
            'display_name': 'Bangamata Hall',
            'dept_type': 'administrative',
            'head_title': 'Provost',
        },
        'labs': []
    },
    'office_of_the_hall_provost_bangabandhu': {
        'meta': {
            'codename': 'office_of_the_hall_provost_bangabandhu',
            'name': 'Office of The Hall Provost (Bangabandhu Hall)',
            'display_name': 'Bangabandhu Hall',
            'dept_type': 'administrative',
            'head_title': 'Provost',
        },
        'labs': []
    },
    'office_of_the_hall_provost_muktijuddha': {
        'meta': {
            'codename': 'office_of_the_hall_provost_muktijuddha',
            'name': 'Office of The Hall Provost (Muktijuddha Hall)',
            'display_name': 'Muktijuddha Hall',
            'dept_type': 'administrative',
            'head_title': 'Provost',
        },
        'labs': []
    },
    'central_computer_center': {
        'meta': {
            'codename': 'central_computer_center',
            'name': 'Central Computer Center',
            'display_name': 'Central Computer Center',
            'dept_type': 'administrative',
            'head_title': 'In Charge',
        },
        'labs': []
    },
}


class Command(BaseCommand):
    def handle(self, *args: Any, **options: Any):
        dept_count = 0
        labs_count = 0
        for i in departments:
            dept, created = Department.objects.get_or_create(**departments[i]['meta'])
            if created:
                dept_count += 1
            for lab_data in departments[i]['labs']:
                lab, lab_created = Lab.objects.get_or_create(dept=dept, **lab_data)
                if lab_created:
                    labs_count += 1
        self.stdout.write(self.style.SUCCESS(f"{dept_count} Departments Ceated, {labs_count} Labs Created"))