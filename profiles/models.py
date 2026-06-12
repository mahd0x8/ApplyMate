from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=200, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    location = models.CharField(max_length=200, blank=True)
    linkedin_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    website_url = models.URLField(blank=True)
    professional_summary = models.TextField(blank=True)
    preferred_titles = models.CharField(max_length=500, blank=True)
    preferred_industries = models.CharField(max_length=500, blank=True)
    preferred_locations = models.CharField(max_length=500, blank=True)
    salary_min = models.PositiveIntegerField(null=True, blank=True)
    salary_max = models.PositiveIntegerField(null=True, blank=True)
    work_mode = models.CharField(
        max_length=20,
        choices=[('remote', 'Remote'), ('hybrid', 'Hybrid'), ('onsite', 'Onsite'), ('any', 'Any')],
        default='any',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} profile"

    def get_initials(self):
        parts = (self.full_name or self.user.email).split()
        if len(parts) >= 2:
            return (parts[0][0] + parts[1][0]).upper()
        return (self.full_name or self.user.email)[:2].upper()


class WorkExperience(models.Model):
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='work_experiences')
    company = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    location = models.CharField(max_length=200, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.title} at {self.company}"


class Education(models.Model):
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='educations')
    institution = models.CharField(max_length=200)
    degree = models.CharField(max_length=200)
    field_of_study = models.CharField(max_length=200, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    gpa = models.CharField(max_length=20, blank=True)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.degree} from {self.institution}"


class Skill(models.Model):
    CATEGORY_CHOICES = [
        ('technical', 'Technical'),
        ('soft', 'Soft Skills'),
        ('language', 'Language'),
        ('tool', 'Tool / Software'),
        ('other', 'Other'),
    ]
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='skills')
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='technical')
    proficiency = models.CharField(
        max_length=20,
        choices=[('beginner', 'Beginner'), ('intermediate', 'Intermediate'), ('advanced', 'Advanced'), ('expert', 'Expert')],
        default='intermediate',
    )

    class Meta:
        ordering = ['category', 'name']

    def __str__(self):
        return self.name


class Project(models.Model):
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='projects')
    name = models.CharField(max_length=200)
    url = models.URLField(blank=True)
    description = models.TextField(blank=True)
    technologies = models.CharField(max_length=500, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', '-start_date']

    def __str__(self):
        return self.name


class Certification(models.Model):
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='certifications')
    name = models.CharField(max_length=200)
    issuer = models.CharField(max_length=200, blank=True)
    issued_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    credential_id = models.CharField(max_length=200, blank=True)
    credential_url = models.URLField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', '-issued_date']

    def __str__(self):
        return self.name
