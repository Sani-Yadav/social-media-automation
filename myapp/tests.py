from instagrapi import Client
from myapp.config import INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD
cl = Client()
cl.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
print("Login OK")
