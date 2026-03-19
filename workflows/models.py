"""
Workflow Models
===============
Generic approval engine models supporting multiple levels of approval for any object type.
"""
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class ApprovalAction(models.Model):
    """
    A generic model to track the approval workflow of any other model
    (e.g., LeaveRequest, ExitRecord).
    """
    ACTION_CHOICES = [
        ('submitted', 'Submitted'),
        ('reviewed', 'Reviewed'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
        ('reverted', 'Reverted'),
    ]

    # ContentType bindings pattern to link to any model
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    # Workflow Action Details
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    actor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='approval_actions')
    remarks = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.actor.get_full_name() or self.actor.username} - {self.get_action_display()} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
