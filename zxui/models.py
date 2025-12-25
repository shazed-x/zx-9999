from django.db import models


class Tool(models.Model):
    name = models.CharField(max_length=80, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self) -> str:
        return self.name


class CommandTemplate(models.Model):
    tool = models.ForeignKey(Tool, on_delete=models.CASCADE, related_name='commands')
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    template = models.TextField()
    category = models.CharField(max_length=60, blank=True, default='')
    tags = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        unique_together = ('tool', 'name')

    def __str__(self) -> str:
        return f"{self.tool.name} - {self.name}"
