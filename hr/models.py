"""
HR Models
=========
Complete data models for Human Resources management including:
Attendance, Leave, Payroll, Recruitment, Training, Grievance, and Exit.
"""
from django.db import models
from django.contrib.auth.models import User
from accounts.models import Department


class Attendance(models.Model):
    """Daily attendance record for employees."""
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('half_day', 'Half Day'),
        ('leave', 'On Leave'),
        ('holiday', 'Holiday'),
    ]

    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='present')
    check_in = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)
    remarks = models.CharField(max_length=200, blank=True)
    marked_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='attendance_marked'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        unique_together = ['employee', 'date']

    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.date} - {self.get_status_display()}"


class LeaveType(models.Model):
    """Types of leave available (Casual, Sick, Earned, etc.)."""
    name = models.CharField(max_length=50, unique=True)
    days_allowed = models.PositiveIntegerField(default=12)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class LeaveRequest(models.Model):
    """Employee leave application and approval workflow."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]

    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leave_requests')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    approved_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='leaves_approved'
    )
    rejection_reason = models.TextField(blank=True)
    applied_on = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-applied_on']

    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.leave_type} ({self.start_date} to {self.end_date})"

    @property
    def total_days(self):
        return (self.end_date - self.start_date).days + 1


class LeaveBalance(models.Model):
    """Tracks remaining leave balance per employee per type."""
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leave_balances')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    year = models.PositiveIntegerField()
    total_days = models.PositiveIntegerField(default=0)
    used_days = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ['employee', 'leave_type', 'year']

    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.leave_type} ({self.year})"

    @property
    def remaining_days(self):
        return self.total_days - self.used_days


class SalaryStructure(models.Model):
    """Salary breakdown for an employee."""
    employee = models.OneToOneField(User, on_delete=models.CASCADE, related_name='salary')
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    hra = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='HRA')
    transport_allowance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    medical_allowance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    special_allowance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    pf_deduction = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='PF Deduction')
    tax_deduction = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    other_deductions = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    effective_date = models.DateField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Salary - {self.employee.get_full_name()}"

    @property
    def gross_salary(self):
        return (self.basic_salary + self.hra + self.transport_allowance +
                self.medical_allowance + self.special_allowance)

    @property
    def total_deductions(self):
        return self.pf_deduction + self.tax_deduction + self.other_deductions

    @property
    def net_salary(self):
        return self.gross_salary - self.total_deductions


class PayrollRecord(models.Model):
    """Monthly payroll record."""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('processed', 'Processed'),
        ('paid', 'Paid'),
    ]

    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payroll_records')
    month = models.PositiveIntegerField()
    year = models.PositiveIntegerField()
    gross_salary = models.DecimalField(max_digits=12, decimal_places=2)
    total_deductions = models.DecimalField(max_digits=12, decimal_places=2)
    net_salary = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    generated_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-year', '-month']
        unique_together = ['employee', 'month', 'year']

    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.month}/{self.year}"


class JobOpening(models.Model):
    """Job opening / requisition for recruitment."""
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('closed', 'Closed'),
        ('on_hold', 'On Hold'),
        ('filled', 'Filled'),
    ]
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    title = models.CharField(max_length=200)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='job_openings')
    description = models.TextField()
    requirements = models.TextField(blank=True)
    positions = models.PositiveIntegerField(default=1)
    location = models.CharField(max_length=100, blank=True)
    salary_range = models.CharField(max_length=100, blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open')
    posted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    posted_date = models.DateField(auto_now_add=True)
    closing_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['-posted_date']

    def __str__(self):
        return f"{self.title} ({self.department})"


class Candidate(models.Model):
    """Job candidate / applicant record."""
    STATUS_CHOICES = [
        ('applied', 'Applied'),
        ('shortlisted', 'Shortlisted'),
        ('interview', 'Interview Scheduled'),
        ('offered', 'Offered'),
        ('hired', 'Hired'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn'),
    ]

    job_opening = models.ForeignKey(JobOpening, on_delete=models.CASCADE, related_name='candidates')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    experience_years = models.PositiveIntegerField(default=0)
    current_company = models.CharField(max_length=200, blank=True)
    expected_salary = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='applied')
    notes = models.TextField(blank=True)
    applied_date = models.DateField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-applied_date']

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.job_opening.title}"


class Interview(models.Model):
    """Interview schedule for a candidate."""
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]
    RESULT_CHOICES = [
        ('pending', 'Pending'),
        ('passed', 'Passed'),
        ('failed', 'Failed'),
    ]

    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='interviews')
    round_name = models.CharField(max_length=100, help_text='e.g. Technical Round 1, HR Round')
    interviewer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    scheduled_date = models.DateTimeField()
    location = models.CharField(max_length=200, blank=True, help_text='Room or video link')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='scheduled')
    result = models.CharField(max_length=10, choices=RESULT_CHOICES, default='pending')
    feedback = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-scheduled_date']

    def __str__(self):
        return f"{self.candidate} - {self.round_name}"


class Appraisal(models.Model):
    """Employee performance appraisal record."""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('reviewed', 'Reviewed'),
        ('completed', 'Completed'),
    ]
    RATING_CHOICES = [
        (1, 'Needs Improvement'),
        (2, 'Below Expectations'),
        (3, 'Meets Expectations'),
        (4, 'Exceeds Expectations'),
        (5, 'Outstanding'),
    ]

    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appraisals')
    review_period = models.CharField(max_length=50, help_text='e.g. Q1 2026, FY 2025-26')
    reviewer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='reviews_given')
    rating = models.PositiveIntegerField(choices=RATING_CHOICES, null=True, blank=True)
    goals_achieved = models.TextField(blank=True)
    areas_of_improvement = models.TextField(blank=True)
    comments = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.review_period}"


class TrainingSession(models.Model):
    """Training program or session details."""
    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    trainer = models.CharField(max_length=200)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    location = models.CharField(max_length=200, blank=True)
    max_participants = models.PositiveIntegerField(default=30)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='upcoming')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return self.title


class TrainingAssignment(models.Model):
    """Assignment of an employee to a training session."""
    STATUS_CHOICES = [
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('dropped', 'Dropped'),
    ]

    training = models.ForeignKey(TrainingSession, on_delete=models.CASCADE, related_name='assignments')
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='training_assignments')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='assigned')
    completion_date = models.DateField(null=True, blank=True)
    score = models.PositiveIntegerField(null=True, blank=True, help_text='Score out of 100')
    feedback = models.TextField(blank=True)
    assigned_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['training', 'employee']

    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.training.title}"


class Grievance(models.Model):
    """Employee complaint / grievance record."""
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    CATEGORY_CHOICES = [
        ('workplace', 'Workplace Issue'),
        ('harassment', 'Harassment'),
        ('compensation', 'Compensation'),
        ('management', 'Management'),
        ('policy', 'Policy Related'),
        ('other', 'Other'),
    ]

    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='grievances')
    category = models.CharField(max_length=15, choices=CATEGORY_CHOICES)
    subject = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='open')
    assigned_to = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_grievances'
    )
    resolution = models.TextField(blank=True)
    filed_date = models.DateTimeField(auto_now_add=True)
    resolved_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-filed_date']

    def __str__(self):
        return f"{self.subject} - {self.employee.get_full_name()}"


class ExitRecord(models.Model):
    """Employee exit / resignation record."""
    STATUS_CHOICES = [
        ('initiated', 'Initiated'),
        ('notice_period', 'Notice Period'),
        ('exit_interview', 'Exit Interview'),
        ('completed', 'Completed'),
        ('withdrawn', 'Withdrawn'),
    ]
    REASON_CHOICES = [
        ('resignation', 'Resignation'),
        ('termination', 'Termination'),
        ('retirement', 'Retirement'),
        ('contract_end', 'Contract End'),
        ('other', 'Other'),
    ]

    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exit_records')
    reason = models.CharField(max_length=15, choices=REASON_CHOICES)
    resignation_date = models.DateField()
    last_working_day = models.DateField(null=True, blank=True)
    notice_period_days = models.PositiveIntegerField(default=30)
    exit_interview_date = models.DateField(null=True, blank=True)
    exit_interview_notes = models.TextField(blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='initiated')
    full_final_status = models.CharField(max_length=50, default='Pending', help_text='Full & Final Settlement')
    comments = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-resignation_date']

    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.get_reason_display()}"
