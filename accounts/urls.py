from django.urls import path, include
from django.contrib.auth.views import PasswordChangeDoneView
from . import views
from .views import MyPasswordChangeView

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('home/', views.home_view, name='home'),
    path('signup/', views.signup_view, name='signup'),

    path('healthcheck/', views.healthcheck_landing, name='healthcheck_landing'),
    path('healthcheck/thankyou/', views.thank_you, name='thank_you'),
    path('healthcheck/<int:session_id>/', views.healthcheck_wizard, name='healthcheck_wizard'),

    path('help/', views.help_view, name='help'),
    path('chaining/', include('smart_selects.urls')),

    path('summary/', views.summary_view, name='summary'),
    path('summary/guide/', views.summary_guide_view, name='summary_guide'),
    path('ajax/get_teams/', views.ajax_get_teams, name='ajax_get_teams'),
    path('ajax/get_sessions/', views.ajax_get_sessions, name='ajax_get_sessions'),
    path('ajax/get_project/', views.ajax_get_project, name='ajax_get_project'),

    path('yourprofile/', views.yourprofile_view, name='yourprofile'),
    path('yourprofile/edit/', views.edit_profile, name='edit_profile'),
    path('yourprofile/change_password/', MyPasswordChangeView.as_view(), name='change_password'),
    path('yourprofile/change_password/done/', PasswordChangeDoneView.as_view(
        template_name='accounts/password_change_done.html'
    ), name='password_change_done'),
    path('yourprofile/team_summary/', views.team_summary_view, name='team_summary'),

    path('about/', views.about_view, name='about'),
    path('contact_us/', views.contact_us_view, name='contact_us'),
]
