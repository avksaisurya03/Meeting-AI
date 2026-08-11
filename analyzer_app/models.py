import uuid
from django.db import models

class Meeting(models.Model):
    """Stores master records of analyzed meetings."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    filename = models.CharField(max_length=255)
    raw_text = models.TextField()
    summary = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.filename} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"

class ActionItem(models.Model):
    """Stores task assignments associated with a meeting."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='action_items')
    task_title = models.TextField()
    assigned = models.CharField(max_length=255)
    priority = models.CharField(max_length=50)
    effort = models.CharField(max_length=50)
    timeline = models.CharField(max_length=255)
    acceptance_criteria = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.task_title} -> {self.assigned}"

class Decision(models.Model):
    """Stores key decisions and rationales associated with a meeting."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='decisions')
    decision = models.TextField()
    rationale = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.decision[:50]

class ProjectRisk(models.Model):
    """Stores technical blocker points and risk impact assessments."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='project_risks')
    blocker = models.TextField()
    impact = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.blocker[:50]
