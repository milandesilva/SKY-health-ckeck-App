# Gabriel code below 🔵🔵🔵🔵🔵

from django.contrib import admin
from .models import Project, Department, Team, Session, HealthCard, Profile

# === Custom filter: Lets admin filter profiles who have not been assigned to a team ===
class TeamIsNullFilter(admin.SimpleListFilter):
    title = 'Team assignment'
    parameter_name = 'team_assignment'

    def lookups(self, request, model_admin):
        return (
            ('unassigned', 'No Team Assigned'),
            ('assigned', 'Team Assigned'),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == 'unassigned':
            return queryset.filter(team__isnull=True)
        if value == 'assigned':
            return queryset.filter(team__isnull=False)
        return queryset

# === Awaiting Team column: shows a green check if profile is assigned, red X if not ===
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'role', 'team', 'department', 'awaiting_team')
    list_filter = (TeamIsNullFilter, 'team', 'department', 'role')
    search_fields = ('user__username', 'user__email', 'full_name')
    readonly_fields = ('user',)
    
    def awaiting_team(self, obj):
        return obj.team is not None
    awaiting_team.boolean = True
    awaiting_team.short_description = "Awaiting Team"

# === Register Project in Admin ===
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

# === Register Department in Admin ===
@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name',)

# === Register Team in Admin, show project and department ===
@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'project')
    list_filter = ('department', 'project')
    search_fields = ('name',)

# === Register HealthCard in Admin ===
@admin.register(HealthCard)
class HealthCardAdmin(admin.ModelAdmin):
    list_display = ('title',)

# === Register Session in Admin, show both project and team ===
@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('name', 'team', 'project', 'start_date', 'end_date')
    list_filter = ('team', 'project')
    search_fields = ('name',)


# Gabriel code ends here 🔵🔵🔵🔵🔵

