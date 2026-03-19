"""
TPM Admin
"""
from django.contrib import admin
from .models import Project, Task, Milestone, Risk, Issue, Meeting, MeetingActionItem, ProjectNote

admin.site.register(Project)
admin.site.register(Task)
admin.site.register(Milestone)
admin.site.register(Risk)
admin.site.register(Issue)
admin.site.register(Meeting)
admin.site.register(MeetingActionItem)
admin.site.register(ProjectNote)
