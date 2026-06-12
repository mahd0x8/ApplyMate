from django.db import models
from django.contrib.auth.models import User


class JobApplication(models.Model):
    STATUS_CHOICES = [
        ('wishlist', 'Wishlist'),
        ('applied', 'Applied'),
        ('interview', 'Interview'),
        ('offer', 'Offer'),
        ('rejected', 'Rejected'),
    ]
    SOURCE_CHOICES = [
        ('linkedin', 'LinkedIn'),
        ('indeed', 'Indeed'),
        ('referral', 'Referral'),
        ('company', 'Company Site'),
        ('other', 'Other'),
    ]
    WORK_MODE_CHOICES = [
        ('remote', 'Remote'),
        ('hybrid', 'Hybrid'),
        ('onsite', 'Onsite'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    company = models.CharField(max_length=200)
    role = models.CharField(max_length=200)
    location = models.CharField(max_length=200, blank=True)
    job_description = models.TextField(blank=True)
    job_url = models.URLField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='wishlist')
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='other')
    work_mode = models.CharField(max_length=10, choices=WORK_MODE_CHOICES, blank=True)
    salary_min = models.PositiveIntegerField(null=True, blank=True)
    salary_max = models.PositiveIntegerField(null=True, blank=True)
    hiring_manager = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
    deadline = models.DateField(null=True, blank=True)
    follow_up_date = models.DateField(null=True, blank=True)
    match_score = models.PositiveIntegerField(null=True, blank=True)
    color = models.CharField(max_length=7, default='#10B981')
    applied_at = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.role} at {self.company}"

    def get_logo_initials(self):
        words = self.company.split()
        if len(words) >= 2:
            return (words[0][0] + words[1][0]).upper()
        return self.company[:2].upper()

    STATUS_COLORS = {
        'wishlist': '#94A3B8',
        'applied': '#10B981',
        'interview': '#F59E0B',
        'offer': '#22C55E',
        'rejected': '#EF4444',
    }

    def get_status_color(self):
        return self.STATUS_COLORS.get(self.status, '#94A3B8')


class GeneratedDocument(models.Model):
    DOC_TYPE_CHOICES = [
        ('cv', 'CV / Resume'),
        ('cover_letter', 'Cover Letter'),
    ]
    application = models.ForeignKey(JobApplication, on_delete=models.CASCADE, related_name='documents')
    doc_type = models.CharField(max_length=20, choices=DOC_TYPE_CHOICES)
    content = models.TextField()
    version = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_doc_type_display()} v{self.version} for {self.application}"


class ChatMessage(models.Model):
    ROLE_CHOICES = [('user', 'User'), ('assistant', 'Assistant')]
    application = models.ForeignKey(JobApplication, on_delete=models.CASCADE, related_name='chat_messages')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.role}: {self.content[:50]}"
