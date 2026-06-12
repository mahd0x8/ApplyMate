from django.db import models
from django.contrib.auth.models import User


class FormAnswer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='form_answers')
    question = models.TextField()
    answer = models.TextField()
    length_mode = models.CharField(
        max_length=10,
        choices=[('short', 'Short'), ('medium', 'Medium'), ('detailed', 'Detailed')],
        default='medium',
    )
    tone = models.CharField(
        max_length=15,
        choices=[('confident', 'Confident'), ('humble', 'Humble'), ('balanced', 'Balanced')],
        default='balanced',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.question[:80]
