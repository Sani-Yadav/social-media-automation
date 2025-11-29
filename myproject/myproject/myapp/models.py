from django.db import models


class PostRun(models.Model):
    class Platform(models.TextChoices):
        INSTAGRAM = "instagram", "Instagram"
        FACEBOOK = "facebook", "Facebook"
        X = "x", "X (Twitter)"
        YOUTUBE = "youtube", "YouTube"

    class Status(models.TextChoices):
        STARTED = "started", "Started"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"
        SKIPPED = "skipped", "Skipped"

    platform = models.CharField(
        max_length=32, choices=Platform.choices, default=Platform.INSTAGRAM
    )
    quote = models.TextField(blank=True)
    video_path = models.CharField(max_length=255, blank=True)
    status = models.CharField(
        max_length=16, choices=Status.choices, default=Status.STARTED
    )
    error_message = models.TextField(blank=True)
    metadata = models.JSONField(blank=True, default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"{self.platform} run ({self.status}) @ {self.created_at:%Y-%m-%d %H:%M}"

    @property
    def status_class(self) -> str:
        palette = {
            self.Status.SUCCESS: "bg-green-100 text-green-800",
            self.Status.FAILED: "bg-red-100 text-red-700",
            self.Status.SKIPPED: "bg-yellow-100 text-yellow-700",
            self.Status.STARTED: "bg-blue-100 text-blue-700",
        }
        return palette.get(self.status, "bg-gray-100 text-gray-600")
