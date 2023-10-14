from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser, Plan, Thumbnail_size

class PlanAdmin(admin.ModelAdmin):
    model = Plan
    list_display = ['name', 'expiring_link', 'original_available']
    filter_horizontal = ('thumbnail_sizes',)


    fieldsets = (
        ('Name', {
            'fields': ('name',)
        }),
        ('Plan details', {
            'fields': ('expiring_link', 'original_available')
        }),
        #multiple choice field with ability to input a number for available thumbnail sizes
        ('Available Thumbnail sizes', {
            'fields': ('thumbnail_sizes',)

        })
    )

    add_fieldsets = (
        ('Name', {
            'fields': ('name',)
        }),
        ('Plan details', {
            'fields': ('expiring_link', 'original_available')
        }),
        #multiple choice field with ability to input a number for available thumbnail sizes
        ('Available Thumbnail sizes', {
            'fields': ('thumbnail_sizes',)
        })
    )


admin.site.register(CustomUser)
admin.site.register(Thumbnail_size)
admin.site.register(Plan, PlanAdmin)
