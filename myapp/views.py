import traceback
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import PostRun
from .auto_post import (
    generate_tech_script,
    create_reel_video,
    post_instagram,
    post_instagram_image,
)
from .twitter_utils import post_tweet


def dashboard(request):
    # Latest 10 runs (latest first)
    latest_runs = list(PostRun.objects.all()[:10])
    last = latest_runs[0] if latest_runs else None

    status_color = {
        PostRun.Status.SUCCESS: "text-green-600",
        PostRun.Status.FAILED: "text-red-600",
        PostRun.Status.SKIPPED: "text-yellow-600",
        PostRun.Status.STARTED: "text-blue-600",
    }

    context = {
        "latest_runs": latest_runs,
        "latest_quote": last.quote if last else "",
        "last_status": last.get_status_display() if last else "",
        "status_color_class": status_color.get(last.status, "text-gray-500") if last else "",
        "last_run_time": timezone.localtime(last.finished_at).strftime("%d %b %Y, %H:%M")
            if last and last.finished_at else "",
        "last_platform": last.get_platform_display() if last else "",
    }

    return render(request, "dashboard.html", context)


@csrf_exempt
def post_instagram_view(request):
    """Direct Instagram REEL posting from dashboard"""
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "POST method required"}, status=405)

    # Create a new PostRun record
    run = PostRun.objects.create(platform=PostRun.Platform.INSTAGRAM, status=PostRun.Status.STARTED)
    run_metadata = {}

    try:
        # Step 1: Generate tech content (har bar unique)
        quote = generate_tech_script()
        run.quote = quote

        # Step 2: Create video
        video_path = create_reel_video(quote)
        if not video_path:
            raise Exception("Video generation failed; check logs.")

        run.video_path = video_path
        run_metadata["video_path"] = video_path

        # Step 3: Post to Instagram
        post_instagram(video_path)
        
        run.status = PostRun.Status.SUCCESS
        run_metadata["message"] = "Instagram post successful"

        return JsonResponse({
            "success": True,
            "message": "✅ Instagram par post ho gaya bhai! 🎉",
            "quote": quote,
            "video_path": video_path,
            "run_id": run.id
        })

    except Exception as exc:
        run.status = PostRun.Status.FAILED
        run.error_message = str(exc)
        run_metadata["traceback"] = traceback.format_exc()
        
        return JsonResponse({
            "success": False,
            "error": str(exc),
            "run_id": run.id
        }, status=500)
    
    finally:
        run.metadata = run_metadata
        run.finished_at = timezone.now()
        run.save()


@csrf_exempt
def post_twitter_view(request):
    """Post to Twitter from dashboard"""
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "POST method required"}, status=405)

    # Create a new PostRun record
    run = PostRun.objects.create(platform=PostRun.Platform.X, status=PostRun.Status.STARTED)
    run_metadata = {}

    try:
        # Generate tech content
        quote = generate_tech_script()
        run.quote = quote

        # Post to Twitter
        result = post_tweet(quote)
        
        if not result['success']:
            raise Exception(f"Twitter post failed: {result.get('error', 'Unknown error')}")
        
        run.status = PostRun.Status.SUCCESS
        run_metadata["tweet_id"] = result.get('tweet_id')
        run_metadata["message"] = "Tweet posted successfully"

        return JsonResponse({
            "success": True,
            "message": "✅ Tweet successful! 🚀",
            "quote": quote,
            "tweet_id": result.get('tweet_id'),
            "run_id": run.id
        })

    except Exception as exc:
        run.status = PostRun.Status.FAILED
        run.error_message = str(exc)
        run_metadata["traceback"] = traceback.format_exc()
        
        return JsonResponse({
            "success": False,
            "error": str(exc),
            "run_id": run.id
        }, status=500)
    
    finally:
        run.metadata = run_metadata
        run.finished_at = timezone.now()
        run.save()


@csrf_exempt
def post_instagram_image_view(request):
    """Direct Instagram IMAGE (photo-only) posting from dashboard"""
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "POST method required"}, status=405)

    # Create a new PostRun record
    run = PostRun.objects.create(platform=PostRun.Platform.INSTAGRAM, status=PostRun.Status.STARTED)
    run_metadata = {}

    try:
        # Step 1: Generate tech content (har bar unique)
        quote = generate_tech_script()
        run.quote = quote

        # Step 2: Sirf image ke saath Instagram post
        post_instagram_image(quote)

        run.status = PostRun.Status.SUCCESS
        run_metadata["message"] = "Instagram image post successful"

        return JsonResponse(
            {
                "success": True,
                "message": "✅ Instagram par IMAGE post ho gaya bhai! 🎉",
                "quote": quote,
                "run_id": run.id,
            }
        )

    except Exception as exc:
        run.status = PostRun.Status.FAILED
        run.error_message = str(exc)
        run_metadata["traceback"] = traceback.format_exc()

        return JsonResponse(
            {
                "success": False,
                "error": str(exc),
                "run_id": run.id,
            },
            status=500,
        )

    finally:
        run.metadata = run_metadata
        run.finished_at = timezone.now()
        run.save()
