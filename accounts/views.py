from django.shortcuts import render, redirect
from django.db import connection
from django.contrib import messages
from django.http import HttpResponse
from .models import User, Team, Department, Session, HealthCard, Votes, Project
from django.db.models.functions import TruncDate
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordChangeView

from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import JsonResponse
import json
from datetime import datetime
from django.utils import timezone
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from .models import Profile
from django.contrib.auth import authenticate, login
import sys

# Reminder, do not remove unused imports. We are still processing the logic!!!

# Ridhwan code here
# Sign UP
def signup_view(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip()
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        repeat_password = request.POST.get('repeat_password', '')

        if not all([full_name, email, username, password, repeat_password]):
            messages.error(request, "Please fill in all fields.")
            return render(request, 'accounts/signup.html')

        if password != repeat_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'accounts/signup.html')

        if len(password) < 8:
            messages.error(request, "Password must be at least 8 characters.")
            return render(request, 'accounts/signup.html')

        if User.objects.filter(username__iexact=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, 'accounts/signup.html')

        if User.objects.filter(email__iexact=email).exists():
            messages.error(request, "Email already exists.")
            return render(request, 'accounts/signup.html')

        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
            )
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.full_name = full_name
            profile.role = 'Unassigned'
            profile.save()
            messages.success(request, 'Account created successfully! You can now log in.')
            return redirect('login')
        except IntegrityError:
            messages.error(request, "A user with these details already exists.")
            return render(request, 'accounts/signup.html')
        except Exception:
            messages.error(request, "Could not create your account. Please try again.")
            return render(request, 'accounts/signup.html')

    return render(request, 'accounts/signup.html')
# Ridhwan code here

# Bilal code here
# Log in

def login_view(request):
    if request.method == 'POST':
        identifier = request.POST.get('identifier', '').strip()
        password = request.POST.get('password', '').strip()

        if not identifier or not password:
            messages.error(request, 'Please enter your username/email and password.')
            return render(request, 'accounts/login.html')

        # Try to find by username or email
        user = None
        # Try username first
        user = authenticate(request, username=identifier, password=password)
        if user is None:
            # Try email
            try:
                user_obj = User.objects.get(email__iexact=identifier)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                user = None

        if user is not None:
            login(request, user)  # Django handles session
            return redirect('/accounts/home/')
        else:
            messages.error(request, 'Invalid credentials.')

    return render(request, 'accounts/login.html')

# Bilal code here


# Bilal code here
# Log out
def logout_view(request):
    logout(request)
    return redirect('login')
# Bilal code here

# Ridhwan code here
# Home page view
@login_required(login_url='login')
def home_view(request):
    return render(request, 'accounts/home.html')
# Ridhwan code here

# Milan
# Help form
def help_view(request):
    if request.method == "POST":
        email = request.POST.get("email", "")
        message = request.POST.get("message", "")
        if email and message:
            send_mail(
                "HealthCheck Help Message",
                message,
                email,
                [settings.DEFAULT_FROM_EMAIL],  # Change to your admin/support email
                fail_silently=False,
            )
            messages.success(request, "Your message has been sent. We'll get back to you soon!")
        else:
            messages.error(request, "Please fill in all fields.")
    return render(request, "accounts/help.html")
# Milan


# Gabriel code below 🔵🔵🔵🔵🔵
ALLOWED_HEALTHCHECK_ROLES = ["Engineer", "Team Leader"]
VALID_VOTES = {"green", "amber", "red"}
VALID_TRENDS = {"improving", "steady", "worsening"}


@login_required(login_url='login')
def healthcheck_landing(request):
    user = request.user
    profile = user.profile

    if profile.role not in ALLOWED_HEALTHCHECK_ROLES:
        return render(request, 'accounts/awaiting_team.html')

    team = profile.team
    if not team:
        messages.warning(request, "You are not assigned to a team yet. Please contact your admin.")
        return render(request, 'accounts/awaiting_team.html')

    now = timezone.now().date()

    session_obj = Session.objects.filter(
        team=team, start_date__lte=now, end_date__gte=now
    ).first()
    current_session = (
        {'id': session_obj.id, 'name': session_obj.name} if session_obj else None
    )

    upcoming_sessions = [
        {'id': s.id, 'name': s.name, 'start_date': s.start_date}
        for s in Session.objects.filter(team=team, start_date__gt=now).order_by('start_date')
    ]

    project_sessions = Session.objects.filter(team=team)
    project_session_ids = list(project_sessions.values_list('id', flat=True))
    completed_sessions = (
        Votes.objects.filter(
            user_id=user.id,
            session_id__in=project_session_ids,
            submitted=True,
        )
        .values('session_id')
        .distinct()
        .count()
    )
    total_sessions = project_sessions.count()

    session_completed = False
    if current_session:
        session_completed = Votes.objects.filter(
            user_id=user.id,
            session_id=current_session['id'],
            submitted=True,
        ).exists()

    context = {
        'current_session': current_session,
        'session_completed': session_completed,
        'upcoming_sessions': upcoming_sessions,
        'completed_sessions': completed_sessions,
        'total_sessions': total_sessions,
        'team_name': team.name,
        'project_name': team.project.name if team.project else None,
        'department_name': team.department.name if team.department else None,
    }
    return render(request, 'accounts/healthcheck.html', context)


@login_required(login_url='login')
def healthcheck_wizard(request, session_id):
    user = request.user
    profile = user.profile

    if profile.role not in ALLOWED_HEALTHCHECK_ROLES or not profile.team:
        messages.warning(request, "You need an assigned team and role to complete a health check.")
        return render(request, 'accounts/awaiting_team.html')

    try:
        session = Session.objects.select_related('team').get(id=session_id)
    except Session.DoesNotExist:
        messages.error(request, "That health check session does not exist.")
        return redirect('healthcheck_landing')

    if session.team_id != profile.team_id:
        messages.error(request, "You can only vote in your own team's session.")
        return redirect('healthcheck_landing')

    now = timezone.now().date()
    if not (session.start_date <= now <= session.end_date):
        messages.error(request, "This health check session is not currently open.")
        return redirect('healthcheck_landing')

    if Votes.objects.filter(user_id=user.id, session_id=session_id, submitted=True).exists():
        return redirect('thank_you')

    cards = list(HealthCard.objects.all().order_by('id'))
    total_cards = len(cards)
    if not cards:
        messages.error(request, "No health cards are set up yet.")
        return redirect('healthcheck_landing')

    try:
        card_index = int(request.GET.get('card', 0))
    except (TypeError, ValueError):
        card_index = 0

    if card_index < 0 or card_index >= total_cards:
        messages.error(request, "Invalid card index.")
        return redirect(f'/accounts/healthcheck/{session_id}/?card=0')

    card = cards[card_index]
    vote_obj, _created = Votes.objects.get_or_create(
        user_id=user.id,
        session_id=session_id,
        card_id=card.id,
        defaults={'vote': None, 'trend': None, 'comment': None, 'submitted': False},
    )

    vote_value = vote_obj.vote or ''
    trend_value = vote_obj.trend or ''
    comment_value = vote_obj.comment or ''
    error = None

    if request.method == "POST":
        posted_vote = request.POST.get('vote', '')
        posted_trend = request.POST.get('trend', '')
        comment_value = request.POST.get('comment', '')

        safe_vote = posted_vote if posted_vote in VALID_VOTES else None
        safe_trend = posted_trend if posted_trend in VALID_TRENDS else None
        going_forward = ('next' in request.POST) or ('submit' in request.POST)

        if going_forward and (not safe_vote or not safe_trend):
            if not safe_vote and not safe_trend:
                error = "Please click a traffic light color (Red/Amber/Green) and select a trend before continuing."
            elif not safe_vote:
                error = "Please click a traffic light color (Red, Amber, or Green) to cast your vote."
            else:
                error = "Please select a trend before continuing."

        if error:
            vote_obj.comment = comment_value
            vote_obj.save()
            vote_value = posted_vote
            trend_value = posted_trend
        else:
            # Keep existing answers when going back / save-exit with empty fields
            if safe_vote is not None or going_forward:
                vote_obj.vote = safe_vote
            if safe_trend is not None or going_forward:
                vote_obj.trend = safe_trend
            vote_obj.comment = comment_value
            vote_obj.save()

            vote_value = vote_obj.vote or ''
            trend_value = vote_obj.trend or ''

            if 'next' in request.POST and card_index < total_cards - 1:
                return redirect(f'/accounts/healthcheck/{session_id}/?card={card_index + 1}')
            if 'previous' in request.POST and card_index > 0:
                return redirect(f'/accounts/healthcheck/{session_id}/?card={card_index - 1}')
            if 'save_exit' in request.POST:
                messages.success(request, "Progress saved. You can continue this health check later.")
                return redirect('healthcheck_landing')
            if 'submit' in request.POST and card_index == total_cards - 1:
                incomplete = []
                for health_card in cards:
                    vote = Votes.objects.filter(
                        user_id=user.id,
                        session_id=session_id,
                        card_id=health_card.id,
                    ).first()
                    if (
                        not vote
                        or vote.vote not in VALID_VOTES
                        or vote.trend not in VALID_TRENDS
                    ):
                        incomplete.append(health_card.title)

                if incomplete:
                    error = (
                        "Please complete every card before submitting. "
                        f"Still missing: {', '.join(incomplete[:3])}"
                        + ("..." if len(incomplete) > 3 else "")
                    )
                else:
                    Votes.objects.filter(user_id=user.id, session_id=session_id).update(
                        submitted=True
                    )
                    return redirect('thank_you')

    context = {
        'session_id': session_id,
        'card_index': card_index,
        'total_cards': total_cards,
        'card': card,
        'vote_value': vote_value,
        'trend_value': trend_value,
        'comment_value': comment_value,
        'is_first': card_index == 0,
        'is_last': card_index == total_cards - 1,
        'error_message': error,
        'progress_label': f"Card {card_index + 1} of {total_cards}",
    }
    return render(request, 'accounts/voting_wizard.html', context)


@login_required(login_url='login')
def thank_you(request):
    return render(request, 'accounts/thank_you.html')


# Gabriel code ends here 🔵🔵🔵🔵🔵


# Mykola codes starts here !!!

@login_required
def summary_view(request):
    #  Get the logged-in user's profile and role
    user_profile = request.user.profile
    role = user_profile.role
    # Get all departments and setup some defaults
    all_departments = Department.objects.all()
    user_department_id = None
    # Determine which departments, teams, sessions the user can see, based on their role
    if role == "Department Leader":
        user_department_id = user_profile.department.id
        selected_department = request.POST.get('department', str(user_department_id))
        departments = all_departments
        if selected_department and str(selected_department) != str(user_department_id):
            teams = Team.objects.filter(department_id=selected_department)
            sessions = Session.objects.filter(team__department_id=selected_department)
            teams_locked = True
            sessions_locked = True
        # Department Leader: Can view own department by default, can select others (locks team/session if not own dept)   
        else:
            teams = Team.objects.filter(department_id=user_department_id)
            sessions = Session.objects.filter(team__department_id=user_department_id)
            teams_locked = False
            sessions_locked = False
        can_view_other_departments = True
        # Team Leader: Can only view their own department, teams, and sessions
    elif role == "Team Leader":
        user_department_id = user_profile.department.id
        departments = Department.objects.filter(id=user_department_id)
        teams = Team.objects.filter(department_id=user_department_id)
        sessions = Session.objects.filter(team__in=teams)
        all_departments = departments
        teams_locked = False
        sessions_locked = False
        can_view_other_departments = False
        # Senior Manager: Can view everything
    elif role == "Senior Manager":
        departments = Department.objects.all()
        teams = Team.objects.all()
        sessions = Session.objects.all()
        all_departments = departments
        teams_locked = False
        sessions_locked = False
        can_view_other_departments = True
        # For other roles (e.g., users not assigned a team), show a waiting page
    else:
        return render(request, 'accounts/awaiting_team.html')

    cards = HealthCard.objects.all()
    stats = []
    total_votes = 0
    selected = {}
    selected_project = None
    # Handle POST (form submission with filters)
    if request.method == 'POST':
        # Read filter selections from form
        selected_department = request.POST.get('department')
        selected_team = request.POST.get('team')
        selected_session = request.POST.get('session')
        selected_card = request.POST.get('card')
        time_period = request.POST.get('time_period')
        # Start with all votes and filter based on selections
        votes_qs = Votes.objects.all()
        if selected_department and selected_department != 'all':
            votes_qs = votes_qs.filter(session__team__department_id=selected_department)
        if selected_team and selected_team != 'all':
            votes_qs = votes_qs.filter(session__team_id=selected_team)
        if selected_session and selected_session != 'all':
            votes_qs = votes_qs.filter(session_id=selected_session)
            # If a session is selected, get its associated project for display
            try:
                session_obj = Session.objects.get(id=selected_session)
                selected_project = session_obj.project
            except Session.DoesNotExist:
                selected_project = None
        if selected_card and selected_card != 'all':
            votes_qs = votes_qs.filter(card_id=selected_card)
        if time_period and '-' in time_period:
            # Parse date range and filter votes by date
            try:
                date_from, date_to = [datetime.strptime(x.strip(), '%d/%m/%Y') for x in time_period.split('-')]
                votes_qs = votes_qs.filter(timestamp__date__gte=date_from, timestamp__date__lte=date_to)
            except Exception:
                pass
        # Aggregate voting stats (vote counts by color)
        stats = list(votes_qs.values('vote').annotate(count=Count('id')).order_by('vote'))
        total_votes = votes_qs.count()

        # --- Trend stats: always provide all three (even if zero) ---
        base_trends = ['improving', 'steady', 'worsening']
        trend_stats_qs = votes_qs.values('trend').annotate(count=Count('id')).order_by('trend')
        trend_counts = {trend: 0 for trend in base_trends}
        for t in trend_stats_qs:
            trend = t['trend']
            if trend in trend_counts:
                trend_counts[trend] = t['count']
        # For template loop:
        trend_stats = [{'trend': k, 'count': trend_counts[k]} for k in base_trends]

        # Find the majority trend
        max_count = max(trend_counts.values())
        max_trends = [k for k, v in trend_counts.items() if v == max_count]
            # Prefer 'steady' if tied
        if 'steady' in max_trends:
            final_trend = 'steady'
        else:
            final_trend = max_trends[0]
        # Save current filter selections for template
        selected = {
            'department': selected_department,
            'team': selected_team,
            'session': selected_session,
            'card': selected_card,
            'time_period': time_period
        }
    else:
        # On GET: set default filters and empty stats
        trend_stats = [{'trend': 'improving', 'count': 0}, {'trend': 'steady', 'count': 0}, {'trend': 'worsening', 'count': 0}]
        final_trend = 'steady'
        if role == "Department Leader":
            selected = {'department': str(user_department_id), 'team': 'all', 'session': 'all', 'card': 'all', 'time_period': ''}
        else:
            selected = {'department': 'all', 'team': 'all', 'session': 'all', 'card': 'all', 'time_period': ''}

    stats_json = json.dumps(stats)
    trend_stats_json = json.dumps(trend_stats)

    # Prepare context for the template (includes everything needed for selection and stats)
    context = {
        'departments': departments,
        'all_departments': all_departments,
        'teams': teams,
        'sessions': sessions,
        'cards': cards,
        'selected': selected,
        'stats': stats,
        'total_votes': total_votes,
        'stats_json': stats_json,
        'trend_stats': trend_stats,
        'trend_stats_json': trend_stats_json,
        'final_trend': final_trend,
        'selected_project': selected_project,
        'can_view_other_departments': can_view_other_departments,
        'role': role,
        'user_department_id': user_department_id,
        'teams_locked': teams_locked if role == "Department Leader" else False,
        'sessions_locked': sessions_locked if role == "Department Leader" else False,
    }
    # Render the summary template
    return render(request, 'accounts/summary.html', context)


@login_required
def ajax_get_teams(request):
    dept_id = request.GET.get('department_id')
    teams = []
    if dept_id and dept_id != 'all':
        teams = list(Team.objects.filter(department_id=dept_id).values('id', 'name', 'department__name'))
    else:
        teams = list(Team.objects.all().values('id', 'name', 'department__name'))
    return JsonResponse({'teams': teams})

@login_required
def ajax_get_sessions(request):
    team_id = request.GET.get('team_id')
    dept_id = request.GET.get('department_id')
    qs = Session.objects.all()
    if dept_id and dept_id != 'all':
        qs = qs.filter(team__department_id=dept_id)
    if team_id and team_id != 'all':
        qs = qs.filter(team_id=team_id)
    sessions = list(qs.values('id', 'name', 'team__name'))
    return JsonResponse({'sessions': sessions})

@login_required
def ajax_get_project(request):
    session_id = request.GET.get('session_id')
    project = None
    if session_id and session_id != 'all':
        from .models import Session, Project
        try:
            session = Session.objects.get(id=session_id)
            if session.project:
                project = {'id': session.project.id, 'name': session.project.name}
        except Session.DoesNotExist:
            project = None
    return JsonResponse({'project': project})

# Placeholder
@login_required
def summary_guide_view(request):
    return render(request, 'accounts/guide_summary.html')


# Mykola code ends here !!!

# Bilal code here
@login_required
def edit_profile(request):
    user = request.user
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        # Check for unique username/email, except for self
        if User.objects.filter(username=username).exclude(pk=user.pk).exists():
            messages.error(request, "Username already taken.")
        elif User.objects.filter(email=email).exclude(pk=user.pk).exists():
            messages.error(request, "Email already taken.")
        else:
            user.username = username
            user.email = email
            user.save()
            messages.success(request, "Profile updated!")
            return redirect('yourprofile')
    return render(request, 'accounts/edit_profile.html', {'user': user})
# Bilal code here

# # Bilal code here

@login_required(login_url='login')
def yourprofile_view(request):
    user = request.user
    profile = user.profile

    # Team and project info
    team = profile.team
    department = profile.department
    project = team.project if team and hasattr(team, 'project') else None

    # If you want to pass stats for summary/progress, do so here
    # (You can copy your team/user stats logic from summary_view and filter by user/team) !!! REMINDER

    context = {
        'user': user,
        'profile': profile,
        'team': team,
        'department': department,
        'project': project,
        # Add stats here for team/user progress
    }
    return render(request, 'accounts/yourprofile.html', context)


class MyPasswordChangeView(PasswordChangeView):
    template_name = 'accounts/change_password.html'
    success_url = reverse_lazy('password_change_done')

# # Bilal code here


# Ridhwan code here
# Engineers summary page

@login_required
def team_summary_view(request):
    profile = request.user.profile
    role = profile.role
    team = profile.team

    # Only Engineers and Team Leaders allowed
    if role not in ["Engineer", "Team Leader"] or not team:
        return render(request, 'accounts/awaiting_team.html')

    sessions = Session.objects.filter(team=team)
    cards = HealthCard.objects.all()

    selected_card = request.POST.get('card')
    time_period = request.POST.get('time_period')

    votes_qs = Votes.objects.filter(session__team=team)
    # Card filter
    if selected_card and selected_card != 'all':
        votes_qs = votes_qs.filter(card_id=selected_card)
    # Time period filter
    if time_period and '-' in time_period:
        try:
            from datetime import datetime
            date_from, date_to = [datetime.strptime(x.strip(), '%d/%m/%Y') for x in time_period.split('-')]
            votes_qs = votes_qs.filter(timestamp__date__gte=date_from, timestamp__date__lte=date_to)
        except Exception:
            pass

    # --- Team Voting Statistics ---
    team_vote_counts = {'amber': 0, 'green': 0, 'red': 0}
    for v in votes_qs.values('vote').annotate(count=Count('id')):
        if v['vote'] in team_vote_counts:
            team_vote_counts[v['vote']] = v['count']
    team_total_votes = sum(team_vote_counts.values())

    # --- User Voting Statistics ---
    user_vote_counts = {'amber': 0, 'green': 0, 'red': 0}
    for v in votes_qs.filter(user=request.user).values('vote').annotate(count=Count('id')):
        if v['vote'] in user_vote_counts:
            user_vote_counts[v['vote']] = v['count']
    user_total_votes = sum(user_vote_counts.values())

    # --- Team Trend Statistics ---
    team_trend_counts = {'improving': 0, 'steady': 0, 'worsening': 0}
    for t in votes_qs.values('trend').annotate(count=Count('id')):
        if t['trend'] in team_trend_counts:
            team_trend_counts[t['trend']] = t['count']
    max_team_trend = max(team_trend_counts.values())
    team_trend_options = [k for k, v in team_trend_counts.items() if v == max_team_trend]
    if 'steady' in team_trend_options:
        final_team_trend = 'steady'
    else:
        final_team_trend = team_trend_options[0] if team_trend_options else 'steady'

    # --- User Trend Statistics ---
    user_trend_counts = {'improving': 0, 'steady': 0, 'worsening': 0}
    for t in votes_qs.filter(user=request.user).values('trend').annotate(count=Count('id')):
        if t['trend'] in user_trend_counts:
            user_trend_counts[t['trend']] = t['count']
    max_user_trend = max(user_trend_counts.values())
    user_trend_options = [k for k, v in user_trend_counts.items() if v == max_user_trend]
    if 'steady' in user_trend_options:
        final_user_trend = 'steady'
    else:
        final_user_trend = user_trend_options[0] if user_trend_options else 'steady'

    context = {
        'sessions': sessions,
        'cards': cards,
        'team': team,
        'selected_card': selected_card,
        'time_period': time_period,

        'team_vote_counts': team_vote_counts,
        'team_total_votes': team_total_votes,
        'user_vote_counts': user_vote_counts,
        'user_total_votes': user_total_votes,

        'team_trend_counts': team_trend_counts,
        'final_team_trend': final_team_trend,
        'user_trend_counts': user_trend_counts,
        'final_user_trend': final_user_trend,
    }
    return render(request, 'accounts/team_summary.html', context)
# Ridhwan code here


# Milan code here
# Just a place holder
@login_required
def about_view(request):
    return render(request, 'accounts/about.html')

def contact_us_view(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        message = request.POST.get("message", "").strip()
        if email and message:
            send_mail(
                "Health Check - Contact Message",
                f"Message from {email}:\n\n{message}",
                email,
                [settings.DEFAULT_FROM_EMAIL],  # Set this in your settings.py
                fail_silently=False,
            )
            messages.success(request, "Thank you for reaching out! Your message has been sent. We’ll get back to you soon.")
        else:
            messages.error(request, "Please fill in all fields.")
    return render(request, "accounts/contact_us.html")
# Milan code here