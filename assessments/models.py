from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Question(models.Model):
    """Mental health assessment questions"""
    CATEGORY_CHOICES = [
        ('anxiety', 'Anxiety'),
        ('depression', 'Depression'),
        ('stress', 'Stress'),
        ('general', 'General Well-being'),
    ]
    
    text = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['category', 'id']
    
    def __str__(self):
        return f"{self.category}: {self.text[:50]}"


class QuestionOption(models.Model):
    """Options for multiple choice questions"""
    question = models.ForeignKey(Question, related_name='options', on_delete=models.CASCADE)
    text = models.CharField(max_length=200)
    weight = models.IntegerField(help_text="Score weight (0-4, where 0 is best and 4 is worst)")
    
    class Meta:
        ordering = ['weight']
    
    def __str__(self):
        return f"{self.question.text[:30]}: {self.text} ({self.weight})"


class Assessment(models.Model):
    """User assessment results"""
    RESULT_CATEGORIES = [
        ('low', 'Low'),
        ('mild', 'Mild'),
        ('moderate', 'Moderate'),
        ('severe', 'Severe'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assessments')
    total_score = models.IntegerField()
    anxiety_score = models.IntegerField(default=0)
    depression_score = models.IntegerField(default=0)
    stress_score = models.IntegerField(default=0)
    general_score = models.IntegerField(default=0)
    overall_category = models.CharField(max_length=20, choices=RESULT_CATEGORIES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.overall_category} ({self.total_score}) - {self.created_at.strftime('%Y-%m-%d')}"


class ContactMessage(models.Model):
    """Messages from users via contact form"""
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.created_at.strftime('%Y-%m-%d')}"



