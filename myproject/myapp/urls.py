from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("post-instagram/", views.post_instagram_view, name="post_instagram"),
    path("post-instagram-image/", views.post_instagram_image_view, name="post_instagram_image"),
    path("post-twitter/", views.post_twitter_view, name="post_twitter"),
]

