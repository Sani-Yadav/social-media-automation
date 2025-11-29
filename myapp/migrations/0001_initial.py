from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="PostRun",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                (
                    "platform",
                    models.CharField(
                        choices=[
                            ("instagram", "Instagram"),
                            ("facebook", "Facebook"),
                            ("x", "X (Twitter)"),
                            ("youtube", "YouTube"),
                        ],
                        default="instagram",
                        max_length=32,
                    ),
                ),
                ("quote", models.TextField(blank=True)),
                ("video_path", models.CharField(blank=True, max_length=255)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("started", "Started"),
                            ("success", "Success"),
                            ("failed", "Failed"),
                            ("skipped", "Skipped"),
                        ],
                        default="started",
                        max_length=16,
                    ),
                ),
                ("error_message", models.TextField(blank=True)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("finished_at", models.DateTimeField(blank=True, null=True)),
            ],
            options={"ordering": ("-created_at",)},
        ),
    ]

