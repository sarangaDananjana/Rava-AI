from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, ClonedVoice, VoiceSample, GeneratedAudio

# Register Custom User with standard UserAdmin features


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'is_staff', 'is_active')
    search_fields = ('email', 'username')
    ordering = ('email',)

# Inline admin to allow adding samples directly from the ClonedVoice page


class VoiceSampleInline(admin.TabularInline):
    model = VoiceSample
    extra = 1


@admin.register(ClonedVoice)
class ClonedVoiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'gender', 'approximate_age', 'created_at')
    list_filter = ('gender', 'created_at')
    search_fields = ('name', 'user__email')
    # Shows sample upload fields inside the Voice admin
    inlines = [VoiceSampleInline]


@admin.register(VoiceSample)
class VoiceSampleAdmin(admin.ModelAdmin):
    list_display = ('voice', 'uploaded_at')
    search_fields = ('voice__name', 'transcription')


@admin.register(GeneratedAudio)
class GeneratedAudioAdmin(admin.ModelAdmin):
    list_display = ('character_name', 'user', 'created_at')
    list_filter = ('character_name', 'created_at')
    search_fields = ('character_name', 'user__email', 'transcription')
