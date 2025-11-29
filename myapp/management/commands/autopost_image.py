from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from myapp.auto_post import generate_tech_script, post_instagram_image
from myapp.models import PostRun


class Command(BaseCommand):
    help = "Publish a photo post with generated tech caption."

    def add_arguments(self, parser):
        parser.add_argument(
            "--skip-post",
            action="store_true",
            help="Skip the final platform upload step.",
        )

    def handle(self, *args, **options):
        skip_post = options["skip_post"]

        run = PostRun.objects.create(platform=PostRun.Platform.INSTAGRAM)
        metadata = {}

        try:
            caption = generate_tech_script()
            run.quote = caption
            self.stdout.write(self.style.SUCCESS(caption))

            if skip_post:
                run.status = PostRun.Status.SKIPPED
                self.stdout.write(self.style.WARNING("Upload skipped."))
            else:
                post_instagram_image(caption)
                run.status = PostRun.Status.SUCCESS
                self.stdout.write(self.style.SUCCESS("Uploaded."))
        except Exception as exc:
            run.status = PostRun.Status.FAILED
            run.error_message = str(exc)
            self.stderr.write(self.style.ERROR(str(exc)))
        finally:
            run.metadata = metadata
            run.finished_at = timezone.now()
            run.save()
