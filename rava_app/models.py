from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

# Custom User Model optimized for Email Authentication


class CustomUser(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)

    # User's wallet and subscription info
    credits = models.IntegerField(
        default=100, help_text="Number of credits the user owns")
    current_plan = models.CharField(
        max_length=50, default='free plan', help_text="Current subscription plan of the user")

    # Use email for login instead of username
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

# --- CLONED VOICE MODELS ---


class ClonedVoice(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female')
    ]

    # One-to-Many relationship with the User
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='cloned_voices')

    name = models.CharField(
        max_length=255, help_text="Name of the cloned voice")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    approximate_age = models.PositiveIntegerField(
        help_text="Approximate age of the voice owner")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.get_gender_display()}) - {self.user.email}"


class VoiceSample(models.Model):
    """
    Handles multiple audio files and transcriptions for a single cloned voice.
    """
    voice = models.ForeignKey(
        ClonedVoice, on_delete=models.CASCADE, related_name='samples')
    audio_file = models.FileField(upload_to='cloned_voices/samples/')
    transcription = models.TextField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Sample for {self.voice.name}"

# --- GENERATED VOICE MODELS ---


class GeneratedAudio(models.Model):
    # One-to-Many relationship with the User
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='generated_audios')

    # This could be one of the 30 predefined voices or a cloned voice name
    character_name = models.CharField(
        max_length=255, help_text="Name of the character/voice used for generation")
    transcription = models.TextField(
        help_text="The text that was generated into speech")
    audio_file = models.FileField(upload_to='generated_audios/')
    credits_consumed = models.PositiveIntegerField(
        default=0, help_text="Credits consumed to generate this audio")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Generated: {self.character_name} for {self.user.email}"
