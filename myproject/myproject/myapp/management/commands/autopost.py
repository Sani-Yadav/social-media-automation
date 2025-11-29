import traceback

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from myapp.auto_post import (
    create_reel_video,
    generate_tech_script,
    post_instagram,
)
from myapp.models import PostRun


class Command(BaseCommand):
    help = "Generate, render, and publish a motivational reel."

    def add_arguments(self, parser):
        parser.add_argument(
            "--platform",
            default=PostRun.Platform.INSTAGRAM,
            choices=[choice for choice, _ in PostRun.Platform.choices],
            help="Target platform adapter to run.",
        )
        parser.add_argument(
            "--skip-post",
            action="store_true",
            help="Skip the final platform upload step (dry run).",
        )

    def handle(self, *args, **options):
        platform = options["platform"]
        skip_post = options["skip_post"]

        run = PostRun.objects.create(platform=platform)
        run_metadata = {}

        self.stdout.write(self.style.NOTICE(f"🚀 Tech Auto-post started ({platform})"))
        try:
            quote = generate_tech_script()  # Har bar unique tech content
            run.quote = quote
            self.stdout.write(self.style.SUCCESS(f"Quote: {quote}"))

            video_path = create_reel_video(quote)
            if not video_path:
                raise CommandError("Video generation failed; check logs.")

            run.video_path = video_path
            run_metadata["video_path"] = video_path

            if skip_post:
                run.status = PostRun.Status.SKIPPED
                self.stdout.write(self.style.WARNING("Upload skipped (dry run)."))
            else:
                if platform == PostRun.Platform.INSTAGRAM:
                    post_instagram(video_path)
                else:
                    raise CommandError(
                        f"No publisher implementation for platform '{platform}'."
                    )
                run.status = PostRun.Status.SUCCESS
                self.stdout.write(self.style.SUCCESS("✅ Upload complete."))

        except Exception as exc:
            run.status = PostRun.Status.FAILED
            run.error_message = str(exc)
            run_metadata["traceback"] = traceback.format_exc()
            self.stderr.write(self.style.ERROR(f"❌ Run failed: {exc}"))
        finally:
            run.metadata = run_metadata
            run.finished_at = timezone.now()
            run.save()
            self.stdout.write(self.style.NOTICE("Run metadata saved."))

