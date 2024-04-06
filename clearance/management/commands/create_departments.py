from typing import Any, Optional
from django.core.management.base import BaseCommand, CommandError
from clearance.models import Department, Lab

departments = {
    'eee': {
        'meta': {
            'codename': 'eee',
            'name': 'Electrical and Electronic Engineering',
            'display_name': 'Department of EEE',
            'dept_type': 'academic'
        },
        'labs': [
            {
                'codename': 'circuit',
                'name': 'Electrical Circuit',
            },
            {
                'codename': 'electronics',
                'name': 'Electronics Lab',
            },
            {
                'codename': 'dld_lab',
                'name': 'DLD Lab',
            },
            {
                'codename': 'machine',
                'name': 'Electrical Machine',
            },
            {
                'codename': 'hv_lab',
                'name': 'High Voltage Lab',
            },
            {
                'codename': 'atts_lab',
                'name': 'ATTS Lab',
            },
        ]
    },
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
                'codename': 'microprocessor_lab',
                'name': 'Microprocessor Lab',
            },
            {
                'codename': 'networking_lab',
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
            'codename': 'cr',
            'name': 'Civil Engineering',
            'display_name': 'Department of CE',
            'dept_type': 'academic'
        },
        'labs': [
            {
                'codename': 'hydraulics_lab',
                'name': 'Hydraulics Lab',
            },
            {
                'codename': 'transportation_lab',
                'name': 'Transportation Lab',
            },
            {
                'codename': 'materials_lab',
                'name': 'Materials Lab',
            },
            {
                'codename': 'machine_shop',
                'name': 'Machine Shop',
            },
            {
                'codename': 'welding_shop',
                'name': 'Welding Shop',
            },
        ]
    },
    'accessory': {
        'meta': {
            'codename': 'accessory_dept',
            'name': 'Accessory Department',
            'display_name': 'Accessory Department',
            'dept_type': 'accessory'
        },
        'labs': [
            {
                'codename': 'physics_lab',
                'name': 'Physics Lab',
            },
            {
                'codename': 'chemistry_lab',
                'name': 'Chemistry Lab',
            },
        ]
    },
    'security_dept': {
        'meta': {
            'codename': 'security_dept',
            'name': 'Security Department',
            'display_name': 'Security Department',
            'dept_type': 'administrative'
        },
        'labs': []
    },
    'library': {
        'meta': {
            'codename': 'library',
            'name': 'Library',
            'display_name': 'Library',
            'dept_type': 'administrative'
        },
        'labs': []
    },
    'general_section': {
        'meta': {
            'codename': 'general_section',
            'name': 'General Section',
            'display_name': 'General Section',
            'dept_type': 'administrative'
        },
        'labs': []
    },
    'cash_section': {
        'meta': {
            'codename': 'cash_section',
            'name': 'Cash Section',
            'display_name': 'Cash Section',
            'dept_type': 'administrative'
        },
        'labs': []
    },
    'general_store': {
        'meta': {
            'codename': 'general_store',
            'name': 'General Store',
            'display_name': 'General Store',
            'dept_type': 'administrative'
        },
        'labs': []
    },
    'girls_hostel_supervisor_office': {
        'meta': {
            'codename': 'girls_hostel_supervisor_office',
            'name': 'Girls Hostel Supervisor Office',
            'display_name': 'Girls Hostel Supervisor Office',
            'dept_type': 'administrative'
        },
        'labs': []
    },
    'boys_hostel_supervisor_office': {
        'meta': {
            'codename': 'boys_hostel_supervisor_office',
            'name': 'Boys Hostel Supervisor Office',
            'display_name': 'Boys Hostel Supervisor Office',
            'dept_type': 'administrative'
        },
        'labs': []
    },
    'central_computer_center': {
        'meta': {
            'codename': 'central_computer_center',
            'name': 'Central Computer Center',
            'display_name': 'Central Computer Center',
            'dept_type': 'administrative'
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