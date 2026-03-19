"""
Management Command: seed_data
==============================
Populates the database with sample/demo data for development and testing.
Usage: python manage.py seed_data
"""
import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone

from accounts.models import Department, Role, UserProfile
from core.models import Notification, ActivityLog
from hr.models import (
    LeaveType, LeaveRequest, Attendance, SalaryStructure,
    JobOpening, Candidate, Appraisal, TrainingSession, Grievance
)
from tpm.models import (
    Project, Task, Milestone, Risk, Issue, Meeting, ProjectNote
)


class Command(BaseCommand):
    help = 'Seeds the database with demo data for development'

    def handle(self, *args, **options):
        self.stdout.write('Seeding database...\n')

        # --- Departments ---
        departments_data = [
            ('ENG', 'Engineering', 'Software development & engineering'),
            ('HR', 'Human Resources', 'People operations & talent'),
            ('FIN', 'Finance', 'Financial planning & accounting'),
            ('MKT', 'Marketing', 'Brand, growth & communications'),
            ('OPS', 'Operations', 'Operational excellence & logistics'),
            ('SALES', 'Sales', 'Revenue generation & partnerships'),
            ('IT', 'IT Services', 'Infrastructure & support'),
            ('LEGAL', 'Legal', 'Compliance & legal affairs'),
        ]
        depts = {}
        for code, name, desc in departments_data:
            d, _ = Department.objects.get_or_create(
                code=code, defaults={'name': name, 'description': desc}
            )
            depts[code] = d
        self.stdout.write(f'  [OK] {len(depts)} departments')

        # --- Roles ---
        roles_data = [
            ('admin', 'Admin / Super Admin'),
            ('hr', 'Human Resources'),
            ('tpm', 'Technical Project Manager'),
            ('finance', 'Finance'),
            ('sales', 'Sales'),
            ('engineering', 'Engineering'),
        ]
        roles = {}
        for name, desc in roles_data:
            r, _ = Role.objects.get_or_create(name=name)
            roles[name] = r
        self.stdout.write(f'  [OK] {len(roles)} roles')

        # --- Users ---
        users = {}
        users_data = [
            ('admin', 'Admin', 'User', 'admin@erp.com', 'admin', 'ENG', True, 'ADM001', 'System Admin'),
            ('hr_user', 'Sarah', 'Johnson', 'sarah@erp.com', 'hr', 'HR', False, 'HR001', 'HR Manager'),
            ('tpm_user', 'Mike', 'Chen', 'mike@erp.com', 'tpm', 'ENG', False, 'TPM001', 'Sr. Project Manager'),
            ('john', 'John', 'Smith', 'john@erp.com', 'engineering', 'ENG', False, 'ENG001', 'Software Engineer'),
            ('jane', 'Jane', 'Williams', 'jane@erp.com', 'engineering', 'ENG', False, 'ENG002', 'Frontend Developer'),
            ('bob', 'Bob', 'Brown', 'bob@erp.com', 'finance', 'FIN', False, 'FIN001', 'Financial Analyst'),
            ('alice', 'Alice', 'Davis', 'alice@erp.com', 'hr', 'HR', False, 'HR002', 'HR Associate'),
            ('tom', 'Tom', 'Wilson', 'tom@erp.com', 'tpm', 'ENG', False, 'TPM002', 'Project Manager'),
            ('emma', 'Emma', 'Taylor', 'emma@erp.com', 'sales', 'SALES', False, 'SLS001', 'Sales Manager'),
            ('david', 'David', 'Martinez', 'david@erp.com', 'engineering', 'IT', False, 'IT001', 'DevOps Engineer'),
        ]
        for uname, first, last, email, role_name, dept_code, is_super, eid, desig in users_data:
            user, created = User.objects.get_or_create(
                username=uname,
                defaults={
                    'first_name': first, 'last_name': last, 'email': email,
                    'is_staff': is_super, 'is_superuser': is_super,
                }
            )
            if created:
                user.set_password('password123')
                user.save()
            profile, _ = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'role': roles.get(role_name),
                    'department': depts.get(dept_code),
                    'employee_id': eid,
                    'designation': desig,
                    'phone': f'+1-555-{random.randint(1000, 9999)}',
                    'date_of_joining': timezone.now().date() - timedelta(days=random.randint(90, 900)),
                }
            )
            users[uname] = user
        self.stdout.write(f'  [OK] {len(users)} users')

        # --- Leave Types ---
        leave_types = []
        for lt in ['Casual Leave', 'Sick Leave', 'Earned Leave', 'Maternity Leave']:
            obj, _ = LeaveType.objects.get_or_create(name=lt, defaults={'days_allowed': 12})
            leave_types.append(obj)
        self.stdout.write(f'  [OK] {len(leave_types)} leave types')

        # --- Attendance (last 5 days) ---
        today = timezone.now().date()
        att_count = 0
        for day_offset in range(5):
            date = today - timedelta(days=day_offset)
            for uname, user in users.items():
                status = random.choice(['present', 'present', 'present', 'absent', 'half_day'])
                Attendance.objects.get_or_create(
                    employee=user, date=date,
                    defaults={
                        'status': status,
                        'check_in': timezone.now().replace(hour=9, minute=random.randint(0, 30)) if status != 'absent' else None,
                        'check_out': timezone.now().replace(hour=17, minute=random.randint(0, 30)) if status == 'present' else None,
                    }
                )
                att_count += 1
        self.stdout.write(f'  [OK] {att_count} attendance records')

        # --- Leave Requests ---
        leave_count = 0
        for _ in range(8):
            emp = random.choice(list(users.values()))
            lt = random.choice(leave_types)
            start = today + timedelta(days=random.randint(1, 30))
            end = start + timedelta(days=random.randint(1, 5))
            lr, created = LeaveRequest.objects.get_or_create(
                employee=emp, leave_type=lt, start_date=start,
                defaults={
                    'end_date': end,
                    'reason': f'Personal reason - {random.choice(["family event", "medical", "vacation", "personal work"])}',
                    'status': random.choice(['pending', 'pending', 'approved', 'rejected']),
                }
            )
            if created:
                leave_count += 1
        self.stdout.write(f'  [OK] {leave_count} leave requests')

        # --- Salary Structures ---
        sal_count = 0
        for uname, user in users.items():
            basic = random.choice([30000, 40000, 50000, 60000, 75000, 90000])
            SalaryStructure.objects.get_or_create(
                employee=user,
                defaults={
                    'basic_salary': basic,
                    'hra': basic * 0.4,
                    'transport_allowance': 3000,
                    'medical_allowance': 2500,
                    'special_allowance': basic * 0.1,
                    'pf_deduction': basic * 0.12,
                    'tax_deduction': basic * 0.15,
                }
            )
            sal_count += 1
        self.stdout.write(f'  [OK] {sal_count} salary structures')

        # --- Job Openings ---
        openings_data = [
            ('Senior Python Developer', depts['ENG'], 'high', 2),
            ('HR Business Partner', depts['HR'], 'medium', 1),
            ('DevOps Engineer', depts['IT'], 'high', 1),
            ('Financial Analyst', depts['FIN'], 'low', 1),
            ('Marketing Manager', depts['MKT'], 'medium', 1),
        ]
        for title, dept, priority, pos in openings_data:
            JobOpening.objects.get_or_create(
                title=title, department=dept,
                defaults={
                    'description': f'Looking for experienced {title} to join our growing team.',
                    'positions': pos, 'priority': priority, 'status': 'open',
                    'posted_by': users['hr_user'],
                    'location': random.choice(['New York', 'San Francisco', 'Remote']),
                }
            )
        self.stdout.write(f'  [OK] {len(openings_data)} job openings')

        # --- Candidates ---
        candidate_data = [
            ('Raj', 'Patel', 'raj@email.com', 5),
            ('Lisa', 'Wang', 'lisa@email.com', 3),
            ('Carlos', 'Garcia', 'carlos@email.com', 7),
            ('Ana', 'Silva', 'ana@email.com', 2),
        ]
        opening = JobOpening.objects.first()
        if opening:
            for fn, ln, email, exp in candidate_data:
                Candidate.objects.get_or_create(
                    email=email,
                    defaults={
                        'job_opening': opening, 'first_name': fn, 'last_name': ln,
                        'phone': f'+1-555-{random.randint(1000, 9999)}',
                        'experience_years': exp,
                        'current_company': random.choice(['TechCorp', 'DataInc', 'WebStudio', 'CloudBase']),
                        'status': random.choice(['applied', 'shortlisted', 'interview']),
                    }
                )
        self.stdout.write(f'  [OK] {len(candidate_data)} candidates')

        # --- Appraisals ---
        for uname in ['john', 'jane', 'bob']:
            Appraisal.objects.get_or_create(
                employee=users[uname], review_period='2025 Q4',
                defaults={
                    'reviewer': users['hr_user'],
                    'rating': random.randint(3, 5),
                    'status': random.choice(['draft', 'submitted', 'completed']),
                    'goals_achieved': 'Met key deliverables for the quarter.',
                    'areas_of_improvement': 'Communication and documentation.',
                }
            )
        self.stdout.write('  [OK] 3 appraisals')

        # --- Training Sessions ---
        for title, dept_code in [('Django Advanced', 'ENG'), ('Leadership Workshop', 'HR'), ('Data Analysis', 'FIN')]:
            TrainingSession.objects.get_or_create(
                title=title,
                defaults={
                    'description': f'{title} - comprehensive training program.',
                    'trainer': random.choice(['Prof. Smith', 'Dr. Lee', 'Coach Adams']),
                    'start_date': today + timedelta(days=random.randint(5, 30)),
                    'end_date': today + timedelta(days=random.randint(31, 45)),
                    'location': random.choice(['Conference Room A', 'Online - Zoom', 'Training Center']),
                    'department': depts.get(dept_code),
                    'max_participants': 20,
                    'status': 'upcoming',
                }
            )
        self.stdout.write('  [OK] 3 training sessions')

        # --- Grievances ---
        Grievance.objects.get_or_create(
            employee=users['john'], subject='Workplace noise',
            defaults={
                'category': 'workplace',
                'description': 'Noise from construction is disrupting work.',
                'status': 'open',
            }
        )
        self.stdout.write('  [OK] 1 grievance')

        # --- Projects ---
        projects_data = [
            ('PRJ-001', 'ERP System Development', 'Internal', depts['ENG'], users['tpm_user'], 500000, 'active', 'high', 45),
            ('PRJ-002', 'E-Commerce Platform', 'RetailCo', depts['ENG'], users['tom'], 750000, 'active', 'critical', 30),
            ('PRJ-003', 'Mobile App Redesign', 'HealthTech', depts['ENG'], users['tpm_user'], 300000, 'planning', 'medium', 0),
            ('PRJ-004', 'Data Analytics Dashboard', 'Internal', depts['IT'], users['tom'], 200000, 'active', 'medium', 60),
            ('PRJ-005', 'HR Portal Upgrade', 'Internal', depts['HR'], users['tpm_user'], 150000, 'completed', 'low', 100),
        ]
        projects = {}
        for code, name, client, dept, mgr, budget, status, priority, comp in projects_data:
            p, _ = Project.objects.get_or_create(
                project_code=code,
                defaults={
                    'name': name, 'client_name': client, 'department': dept,
                    'manager': mgr, 'budget': budget, 'status': status,
                    'priority': priority, 'completion_percentage': comp,
                    'start_date': today - timedelta(days=random.randint(30, 180)),
                    'end_date': today + timedelta(days=random.randint(30, 180)),
                    'description': f'{name} - Full-scale development project.',
                }
            )
            projects[code] = p
        self.stdout.write(f'  [OK] {len(projects)} projects')

        # --- Tasks ---
        task_count = 0
        for proj_code, proj in projects.items():
            for i in range(random.randint(3, 6)):
                title = random.choice([
                    'Design wireframes', 'Build API endpoints', 'UI implementation',
                    'Database schema design', 'Code review', 'Testing & QA',
                    'Deploy to staging', 'Documentation', 'Performance optimization',
                    'Security audit', 'User acceptance testing', 'Bug fixes'
                ])
                Task.objects.get_or_create(
                    project=proj, title=f'{title} #{i+1}',
                    defaults={
                        'assigned_to': random.choice(list(users.values())),
                        'priority': random.choice(['low', 'medium', 'high', 'critical']),
                        'status': random.choice(['todo', 'in_progress', 'review', 'done', 'done']),
                        'start_date': today - timedelta(days=random.randint(1, 30)),
                        'due_date': today + timedelta(days=random.randint(-5, 30)),
                        'estimated_hours': random.choice([4, 8, 16, 24, 40]),
                        'actual_hours': random.choice([0, 4, 8, 12, 20]),
                        'description': f'Task: {title} for project {proj.name}.',
                    }
                )
                task_count += 1
        self.stdout.write(f'  [OK] {task_count} tasks')

        # --- Milestones ---
        ms_count = 0
        for proj_code, proj in list(projects.items())[:3]:
            for i, ms_name in enumerate(['Phase 1 Complete', 'Beta Release', 'Final Delivery']):
                Milestone.objects.get_or_create(
                    project=proj, title=ms_name,
                    defaults={
                        'due_date': today + timedelta(days=30 * (i + 1)),
                        'completion_percentage': random.randint(0, 100),
                    }
                )
                ms_count += 1
        self.stdout.write(f'  [OK] {ms_count} milestones')

        # --- Risks ---
        risk_count = 0
        for proj in list(projects.values())[:3]:
            Risk.objects.get_or_create(
                project=proj, title=f'Schedule delay risk for {proj.name}',
                defaults={
                    'severity': random.choice(['low', 'medium', 'high']),
                    'description': 'Potential schedule slippage due to scope changes.',
                    'mitigation_plan': 'Regular sprint reviews and scope freeze.',
                    'owner': users['tpm_user'],
                    'status': 'identified',
                }
            )
            risk_count += 1
        self.stdout.write(f'  [OK] {risk_count} risks')

        # --- Issues ---
        issue_count = 0
        for proj in list(projects.values())[:3]:
            Issue.objects.get_or_create(
                project=proj, title=f'Bug in {proj.name} login module',
                defaults={
                    'category': 'bug',
                    'criticality': random.choice(['low', 'medium', 'high']),
                    'description': 'Users experiencing intermittent login failures.',
                    'assigned_to': users['john'],
                    'status': 'open',
                }
            )
            issue_count += 1
        self.stdout.write(f'  [OK] {issue_count} issues')

        # --- Meetings ---
        for proj in list(projects.values())[:2]:
            Meeting.objects.get_or_create(
                project=proj, title=f'{proj.name} Sprint Review',
                defaults={
                    'meeting_date': timezone.now() + timedelta(days=random.randint(1, 14)),
                    'location': 'Conference Room B',
                    'discussion_points': 'Sprint progress, blockers, next sprint planning.',
                    'decisions': 'Continue current sprint, reassign blocked tasks.',
                    'created_by': users['tpm_user'],
                }
            )
        self.stdout.write('  [OK] 2 meetings')

        # --- Notes ---
        for proj in list(projects.values())[:3]:
            ProjectNote.objects.get_or_create(
                project=proj, title=f'{proj.name} - Architecture Notes',
                defaults={
                    'content': 'Key decisions on tech stack, deployment strategy, and monitoring.',
                    'author': users['tpm_user'],
                    'is_pinned': random.choice([True, False]),
                }
            )
        self.stdout.write('  [OK] 3 project notes')

        # --- Notifications ---
        for user in list(users.values())[:5]:
            Notification.objects.get_or_create(
                user=user, title='Welcome to ERP System',
                defaults={
                    'message': 'Your account has been set up. Explore your dashboard!',
                    'level': 'info',
                }
            )
        self.stdout.write('  [OK] 5 notifications')

        self.stdout.write(self.style.SUCCESS('\n✅ Database seeded successfully!'))
        self.stdout.write(self.style.WARNING('\n📋 Demo Credentials:'))
        self.stdout.write('  Admin:  admin / password123')
        self.stdout.write('  HR:     hr_user / password123')
        self.stdout.write('  TPM:    tpm_user / password123')
