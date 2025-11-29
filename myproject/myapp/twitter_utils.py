import os
import tweepy
import urllib.parse
from pathlib import Path
from myapp.config import (
    X_CONSUMER_KEY,
    X_CONSUMER_SECRET,
    X_ACCESS_TOKEN,
    X_ACCESS_SECRET,
)

def get_twitter_client_v1():
    """Initialize and return Twitter API v1.1 client (used for media uploads)"""
    try:
        # Get credentials from environment variables
        consumer_key = X_CONSUMER_KEY
        consumer_secret = X_CONSUMER_SECRET
        access_token = X_ACCESS_TOKEN
        access_token_secret = X_ACCESS_SECRET

        # URL decode the tokens if they're URL-encoded
        if access_token and '%' in access_token:
            access_token = urllib.parse.unquote(access_token)
        if access_token_secret and '%' in access_token_secret:
            access_token_secret = urllib.parse.unquote(access_token_secret)

        # Do not print or log credential values

        # Validate all credentials are present
        missing = []
        if not consumer_key: missing.append('X_CONSUMER_KEY')
        if not consumer_secret: missing.append('X_CONSUMER_SECRET')
        if not access_token: missing.append('X_ACCESS_TOKEN')
        if not access_token_secret: missing.append('X_ACCESS_SECRET')
        
        if missing:
            raise ValueError(f"Missing Twitter API credentials: {', '.join(missing)} in .env file")

        # Initialize Twitter client with OAuth 1.0a
        auth = tweepy.OAuth1UserHandler(
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            access_token=access_token,
            access_token_secret=access_token_secret
        )
        
        # Create API client
        api = tweepy.API(auth, wait_on_rate_limit=True)
        
        # Verify credentials
        api.verify_credentials()
        
        return api
        
    except Exception as e:
        print(f"❌ Error initializing Twitter v1.1 client: {str(e)}")
        raise

def get_twitter_client_v2():
    """Initialize and return Twitter API v2 client"""
    try:
        # Get credentials from environment variables
        consumer_key = os.getenv('X_CONSUMER_KEY')
        consumer_secret = os.getenv('X_CONSUMER_SECRET')
        access_token = os.getenv('X_ACCESS_TOKEN')
        access_token_secret = os.getenv('X_ACCESS_SECRET')

        # Do not print or log credential values

        # Initialize Twitter client with OAuth 1.0a for v2
        client = tweepy.Client(
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            access_token=access_token,
            access_token_secret=access_token_secret,
        )
        
        pass
        return client
        
    except Exception as e:
        print(f"❌ Error initializing Twitter v2 client: {str(e)}")
        raise

def post_tweet(text, image_path=None):
    """Legacy function - uses v1.1 API"""
    print("⚠️  Using legacy v1.1 API. Consider updating to post_tweet_v2()")
    return post_tweet_v2(text, image_path)

def post_tweet_v2(text, image_path=None):
    """Post a tweet using Twitter API v2 with optional image"""
    try:
        # Initialize v2 client for posting
        client = get_twitter_client_v2()
        
        # For media upload, we need v1.1 API
        media_id = None
        if image_path and os.path.exists(image_path):
            try:
                print(f"📤 Uploading media: {image_path}")
                # Use v1.1 client for media upload
                api_v1 = get_twitter_client_v1()
                media = api_v1.media_upload(image_path)
                media_id = media.media_id
                print(f"✅ Media uploaded successfully. Media ID: {media_id}")
            except Exception as e:
                error_msg = f"Error uploading media: {str(e)}"
                print(f"❌ {error_msg}")
                return {
                    'success': False,
                    'error': error_msg
                }
        
        # Post the tweet using v2 API
        print(f"📝 Posting tweet: {text}")
        try:
            if media_id:
                response = client.create_tweet(text=text, media_ids=[media_id])
            else:
                response = client.create_tweet(text=text)
                
            tweet_id = response.data['id']
            print(f"✅ Tweet posted successfully! Tweet ID: {tweet_id}")
            
            return {
                'success': True,
                'tweet_id': tweet_id,
                'text': text,
                'url': f"https://twitter.com/user/status/{tweet_id}"
            }
            
        except Exception as e:
            error_msg = str(e)
            if "Forbidden" in error_msg and "read-only" in error_msg:
                error_msg += "\nYour app may not have write permissions. Please check your app permissions in the Twitter Developer Portal."
            raise Exception(error_msg)
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Error posting tweet: {error_msg}")
        
        # More detailed error handling
        if "Invalid or expired token" in error_msg:
            error_msg = "Twitter API token is invalid or expired. Please check your credentials."
        elif "Could not authenticate you" in error_msg:
            error_msg = "Twitter API authentication failed. Please verify your API keys and tokens."
        elif "read-only" in error_msg:
            error_msg = "Your app doesn't have write permissions. Please check your app permissions in the Twitter Developer Portal."
            
        return {
            'success': False,
            'error': error_msg
        }
