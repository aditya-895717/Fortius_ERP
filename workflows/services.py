"""
Workflow Services
=================
Business logic for handling approvals, rejections, and state transitions
across different modules like Leave Requests and Resignations.
"""
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from .models import ApprovalAction
from core.models import ActivityLog
from accounts.models import UserProfile

class WorkflowService:
    @staticmethod
    def add_action(instance, action, actor, remarks=''):
        """Record an action in the approval workflow timeline."""
        ctype = ContentType.objects.get_for_model(instance)
        ApprovalAction.objects.create(
            content_type=ctype,
            object_id=instance.id,
            action=action,
            actor=actor,
            remarks=remarks
        )
        # Also log the activity for the audit trail
        ActivityLog.objects.create(
            user=actor,
            action=action,
            model_name=instance.__class__.__name__,
            object_id=instance.id,
            object_repr=str(instance),
            details=f"Workflow action: {action} on {instance} - Remarks: {remarks}"
        )

    @staticmethod
    def approve_leave(leave_request, approver, remarks=''):
        """Approve a leave request and deduct balance."""
        if leave_request.status != 'pending':
            raise ValueError("Can only approve pending requests.")
        
        from hr.models import LeaveBalance
        
        # Deduct balance
        balance, created = LeaveBalance.objects.get_or_create(
            employee=leave_request.employee,
            leave_type=leave_request.leave_type,
            year=leave_request.start_date.year,
            defaults={'total_days': leave_request.leave_type.days_allowed, 'used_days': 0}
        )
        
        if balance.remaining_days < leave_request.total_days:
            # allow it to go negative for now in MVP, but could raise error
            pass 
            
        balance.used_days += leave_request.total_days
        balance.save()

        # Update request status
        leave_request.status = 'approved'
        leave_request.approved_by = approver
        leave_request.save()

        WorkflowService.add_action(leave_request, 'approved', approver, remarks)
        return True

    @staticmethod
    def reject_leave(leave_request, approver, remarks=''):
        """Reject a leave request."""
        if leave_request.status != 'pending':
            raise ValueError("Can only reject pending requests.")
            
        leave_request.status = 'rejected'
        leave_request.approved_by = approver
        leave_request.rejection_reason = remarks
        leave_request.save()
        
        WorkflowService.add_action(leave_request, 'rejected', approver, remarks)
        return True

    @staticmethod
    def cancel_leave(leave_request, actor, remarks=''):
        """Employee cancels their own leave request before approval."""
        if leave_request.status != 'pending':
            raise ValueError("Can only cancel pending requests.")
            
        leave_request.status = 'cancelled'
        leave_request.save()
        
        WorkflowService.add_action(leave_request, 'cancelled', actor, remarks)
        return True

    @staticmethod
    def approve_resignation(exit_record, hr_manager, notice_period_days, remarks=''):
        """
        Approve resignation, calculate notice period end, and transition status.
        """
        if exit_record.status != 'initiated':
            raise ValueError("Can only approve initiated resignations.")
            
        # Update dates and status
        exit_record.notice_period_days = notice_period_days
        exit_record.last_working_day = exit_record.resignation_date + timezone.timedelta(days=notice_period_days)
        exit_record.status = 'notice_period'
        exit_record.save()
        
        WorkflowService.add_action(exit_record, 'approved', hr_manager, f"Notice Period: {notice_period_days} days. {remarks}")
        return True

    @staticmethod
    def mark_exit_completed(exit_record, hr_manager, remarks=''):
        """Finalize the exit process marking employee inactive."""
        if exit_record.status not in ['notice_period', 'exit_interview']:
            raise ValueError("Exit record not in valid state for completion.")
            
        exit_record.status = 'completed'
        exit_record.full_final_status = 'Completed'
        exit_record.save()
        
        # Deactivate user profile and user
        profile = exit_record.employee.profile
        profile.status = 'inactive'
        profile.save()
        
        user = exit_record.employee
        user.is_active = False
        user.save()
        
        WorkflowService.add_action(exit_record, 'reviewed', hr_manager, f"Exit Completed. User deactivated. {remarks}")
        return True
