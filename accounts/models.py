from django.db import models
from django.contrib.auth.models import User
from smart_selects.db_fields import ChainedForeignKey   

# Bilal code here

# --- Project ---
class Project(models.Model):
    name = models.CharField(max_length=255, unique=True)
    # Optional: description, start_date, etc.

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'projects'

# --- Department ---
class Department(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'departments'

# --- Team ---
class Team(models.Model):
    name = models.CharField(max_length=255)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, db_column='department_id')
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, db_column='project_id')

    def __str__(self):
        return f"{self.name} ({self.department.name})"

    class Meta:
        db_table = 'teams'
        unique_together = ('name', 'department')

# --- Session ---
class Session(models.Model):
    name = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    team = models.ForeignKey(Team, on_delete=models.CASCADE, db_column='team_id')
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, db_column='project_id')

    def __str__(self):
        return f"{self.name} ({self.team}) [{self.project}]"

    class Meta:
        db_table = 'sessions'

# --- HealthCard ---
class HealthCard(models.Model):
    title = models.CharField(max_length=255, db_column='title')
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'health_cards'

# --- Profile (Extra User Info) ---
from smart_selects.db_fields import ChainedForeignKey  # <-- Make sure this import is at the top of your models.py

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Link to Django's built-in User
    full_name = models.CharField(max_length=255, blank=True, null=True)

    # Define user roles for the dropdown
    ROLE_CHOICES = [
        ('Unassigned', 'Unassigned'),
        ('Engineer', 'Engineer'),
        ('Team Leader', 'Team Leader'),
        ('Department Leader', 'Department Leader'),
        ('Senior Manager', 'Senior Manager'),
        ('Admin', 'Admin'),
    ]
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='Unassigned',
        help_text="Select the user's role in the organization."
    )

    # Department field with help text to guide the admin
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="You must select a department before you can choose a team."
    )

    # Team field is dynamically filtered based on the selected department
    team = ChainedForeignKey(
        Team,
        chained_field="department",             # Field on this model
        chained_model_field="department",       # Field on the related Team model
        show_all=False,
        auto_choose=True,
        sort=True,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="Only teams from the selected department will appear here. Select a department first."
    )

    def __str__(self):
        return f"{self.user.username}'s profile"

    class Meta:
        db_table = 'user_profiles'

# --- Votes ---
class Votes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')  # Use built-in User
    session = models.ForeignKey(Session, on_delete=models.CASCADE, db_column='session_id')
    card = models.ForeignKey(HealthCard, on_delete=models.CASCADE, db_column='card_id')
    vote = models.CharField(max_length=10, blank=True, null=True)  # Only 'green', 'amber', 'red'
    timestamp = models.DateTimeField(auto_now=True)
    submitted = models.BooleanField(default=False)
    comment = models.TextField(null=True, blank=True)
    trend = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"Vote by {self.user.username} on {self.card.title} for session {self.session.name}"

    class Meta:
        db_table = 'votes'
        verbose_name = 'Vote'
        verbose_name_plural = 'Votes'

    
# Bilal code here