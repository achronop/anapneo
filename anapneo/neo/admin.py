from django.contrib import admin
from anapneo.neo.models import Neo, UserProfile, Feedback


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'get_user_mail', 'first_name', 'last_name', 'city', 
                    'country', 'lat', 'lon']

admin.site.register(UserProfile, UserProfileAdmin)

class FeedbackInline(admin.TabularInline):
    model = Feedback
    extra = 2

class NeoAdmin(admin.ModelAdmin):
    list_display = ['get_user_display_name', 'no','score', 'observation_date', 'position_ra', 
                    'position_dec', 'magnitude', 'updated', 'note', 'num_obs', 
                    'arc', 'nominal_h', 'image', 'number_of_votes_yes',
                    'number_of_votes_no', 'number_of_votes_total']
    inlines = [FeedbackInline]
        
admin.site.register(Neo, NeoAdmin)

class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['user', 'neo', 'vote']

admin.site.register(Feedback, FeedbackAdmin)
