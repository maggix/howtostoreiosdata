from django.contrib import admin
from .models import Recommendation


class RecommendationAdmin(admin.ModelAdmin):
    list_display = ('protection_level', 'storage', 'protection_level_full_name')
    list_filter = ('protection_level', 'storage',)


admin.site.register(Recommendation, RecommendationAdmin)