"""
Core Models
Abstract base models for timestamp tracking.
"""

from django.db import models


class TimeStampedModel(models.Model):
    """
    Abstract base model that provides self-updating
    'created_at' and 'updated_at' fields.
    """
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="Timestamp when this record was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when this record was last updated"
    )
    
    class Meta:
        abstract = True
        ordering = ["-created_at"]


class SoftDeleteModel(models.Model):
    """
    Abstract base model that provides soft delete functionality.
    Records are marked as deleted rather than actually removed.
    """
    
    is_deleted = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Soft delete flag"
    )
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when this record was soft deleted"
    )
    
    class Meta:
        abstract = True
    
    def soft_delete(self):
        """Soft delete this instance."""
        from django.utils import timezone
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=["is_deleted", "deleted_at"])
    
    def restore(self):
        """Restore a soft-deleted instance."""
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=["is_deleted", "deleted_at"])


class BaseModel(TimeStampedModel, SoftDeleteModel):
    """
    Abstract base model combining timestamp and soft delete functionality.
    Use this for most models in the application.
    """
    
    class Meta:
        abstract = True
