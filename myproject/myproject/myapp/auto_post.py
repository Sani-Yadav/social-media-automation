import os
import random
import textwrap
import requests
import numpy as np
from moviepy.editor import *
from gtts import gTTS
from instagrapi import Client
from pydantic import ValidationError
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
import wave

# ====== FIX FOR IMAGEMAGICK ERROR ======
import moviepy.config as mpconfig
mpconfig.change_settings({
    "IMAGEMAGICK_BINARY": r"C:\Program Files\ImageMagick-7.1.2-Q16-HDRI\magick.exe"
})
# =======================================

# ====== CONFIG ======
from myapp.config import GROQ_API_KEY, INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD, UNSPLASH_ACCESS_KEY

# ====== TECH TOPICS LIST ======
TECH_TOPICS = [
    "Artificial Intelligence", "Machine Learning", "Python Programming", "JavaScript",
    "Web Development", "Mobile App Development", "Cloud Computing", "Cybersecurity",
    "Data Science", "Blockchain", "Internet of Things", "Quantum Computing",
    "DevOps", "React.js", "Node.js", "Django", "Flask", "API Development",
    "Database Management", "Git Version Control", "Docker", "Kubernetes",
    "Full Stack Development", "Frontend Development", "Backend Development",
    "UI/UX Design", "Agile Methodology", "Software Testing", "System Design",
    "Computer Networking", "Linux", "AWS", "Google Cloud", "Azure",
    "Microservices", "REST API", "GraphQL", "MongoDB", "PostgreSQL",
    "TypeScript", "Vue.js", "Angular", "Flutter", "React Native",
    "Swift", "Kotlin", "Go Programming", "Rust", "C++", "Java",
    "Computer Vision", "Natural Language Processing", "Deep Learning",
    "Neural Networks", "TensorFlow", "PyTorch", "ChatGPT", "OpenAI",
    "GitHub", "CI/CD", "Jenkins", "Agile Development", "Scrum"
]

# ====== 1. Tech Script Generate (Google/YouTube se inspired) ======
def generate_tech_script():
    """Generate unique, readable & engaging tech content using Groq API with tech topics"""
    if not GROQ_API_KEY or len(GROQ_API_KEY) < 10:
        print("⚠️ GROQ_API_KEY nahi daala → default tech tip use kar raha hoon")
        return "💡 Linux seekhna shuru karo - tech career ka first step hai yeh!"

    random_topic = random.choice(TECH_TOPICS)
    
    tech_prompts = [
        f"'{random_topic}' par ek detailed tech tip Hindi mein 40-50 words mein explain karo - YouTube tech videos style, with examples",
        f"'{random_topic}' ka ek important fact aur use case Hindi mein 40-50 words mein explain karo",
        f"'{random_topic}' ke baare mein powerful insight Hindi mein 40-50 words mein batao - real-world application ke saath",
        f"'{random_topic}' ki ek interesting tip aur kaise use kare Hindi mein 40-50 words mein share karo",
        f"'{random_topic}' ka quick hack ya trick Hindi mein 40-50 words mein explain karo - benefits ke saath"
    ]

    max_retries = 3
    # prepare a safe fallback message in case the API is unavailable or unauthorized
    fallback = f"💡 {random_topic} seekhna shuru karo - tech career ka first step hai yeh!"

    for attempt in range(max_retries):
        try:
            prompt = random.choice(tech_prompts)
            print(f"📱 Tech Topic: {random_topic}")
            print(f"💡 Prompt: {prompt}")
            print(f"🔄 Attempt {attempt + 1}/{max_retries}...")

            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
                json={
                    "model": "llama-3.3-70b-versatile",  # Updated model
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 1.3,
                    "max_tokens": 200,
                    "top_p": 0.9,
                    "frequency_penalty": 0.6,
                    "presence_penalty": 0.4
                },
                timeout=30
            )

            if response.status_code == 401:
                # Unauthorized: API key invalid/expired — don't retry
                print("⚠️ Groq API returned 401 Unauthorized. Check GROQ_API_KEY in your .env or environment variables.")
                print(f"⚠️ Response snippet: {response.text[:200]}")
                return fallback

            if response.status_code != 200:
                print(f"⚠️ Groq API returned status {response.status_code}: {response.text[:200]}")
                if attempt < max_retries - 1:
                    continue
                else:
                    raise Exception(f"API returned status {response.status_code}")

            response_data = response.json()
            choices = response_data.get("choices", [])
            if not choices:
                if attempt < max_retries - 1:
                    continue
                else:
                    raise Exception("No choices in API response")

            content = choices[0].get("message", {}).get("content", "").strip()
            if not content or len(content) < 30:
                if attempt < max_retries - 1:
                    continue
                else:
                    fallback = f"💡 {random_topic} seekhna shuru karo - tech career ka first step hai yeh!"
                    return fallback

            # ✅ Format content for reels
            lines = content.split(". ")
            formatted_lines = []
            for i, line in enumerate(lines):
                line = line.strip()
                if not line:
                    continue
                # Add emoji for first line or key points
                if i == 0:
                    line = f"💡 {line}"
                else:
                    line = f"🔹 {line}"
                formatted_lines.append(line)
            formatted_content = "\n".join(formatted_lines)

            # Add topic if not present
            if random_topic.lower() not in formatted_content.lower():
                formatted_content = f"{random_topic}: {formatted_content}"

            print(f"✅ Groq se content generate ho gaya (formatted) → {formatted_content[:60]}...")
            return formatted_content

        except Exception as e:
            print(f"⚠️ Attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                fallback = f"💡 {random_topic} seekhna shuru karo - tech career ka first step hai yeh!"
                return fallback

# ====== Backward compatibility ======
def generate_motivation_script():
    """Backward compatibility - now generates tech content"""
    return generate_tech_script()

# ====== 2. Random Tech Image Download (Google/Unsplash se) ======
def download_random_tech_image():
    """Download random tech-related image from Unsplash API"""
    # Images folder banaye agar nahi hai
    images_folder = "images"
    os.makedirs(images_folder, exist_ok=True)
    
    # Tech-related image keywords - har bar random select hoga
    tech_keywords = [
        "technology", "coding", "programming", "computer", "laptop", 
        "artificial intelligence", "machine learning", "data science",
        "cybersecurity", "cloud computing", "blockchain", "web development",
        "software development", "code", "developer", "tech startup",
        "digital technology", "innovation", "tech background", "futuristic technology",
        "ai technology", "programming code", "coding laptop", "tech workspace",
        "modern technology", "digital transformation", "tech industry"
    ]
    
    # Random keyword select karo
    keyword = random.choice(tech_keywords)
    print(f"🖼️ Random tech image fetch kar raha hoon: '{keyword}'")
    
    # Agar Unsplash API key hai to use karo, nahi to fallback
    if UNSPLASH_ACCESS_KEY and len(UNSPLASH_ACCESS_KEY) > 10:
        try:
            # Unsplash API se random image fetch karo
            unsplash_url = f"https://api.unsplash.com/photos/random"
            params = {
                "query": keyword,
                "orientation": "portrait",
                "client_id": UNSPLASH_ACCESS_KEY
            }
            
            response = requests.get(unsplash_url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                image_url = data.get("urls", {}).get("regular") or data.get("urls", {}).get("full")
                
                if image_url:
                    # Image download karo
                    img_response = requests.get(image_url, timeout=15)
                    if img_response.status_code == 200:
                        # Images folder mein save karo
                        image_path = os.path.join(images_folder, "bg_tech.jpg")
                        with open(image_path, "wb") as f:
                            f.write(img_response.content)
                        print(f"✅ Tech image download ho gayi: {keyword} → {image_path}")
                        return image_path
        except Exception as e:
            print(f"⚠️ Unsplash API error: {e}")
            print("⚠️ Fallback: Default image use kar raha hoon")
    
    # Fallback: Local bg.jpg use karo agar available ho (images folder mein ya root mein)
    fallback_paths = [
        os.path.join(images_folder, "bg.jpg"),
        "bg.jpg"
    ]
    for fallback_path in fallback_paths:
        if os.path.exists(fallback_path):
            print(f"📸 Default bg.jpg use kar raha hoon: {fallback_path} (Unsplash API key add karo for random images)")
            return fallback_path
    
    # Agar kuch bhi nahi mila
    print("❌ Image nahi mili! Auto-generated background create kar raha hoon")
    try:
        img = Image.new("RGB", (1080, 1440), (20, 20, 20))
        draw = ImageDraw.Draw(img)
        for y in range(0, 1440, 40):
            shade = 40 + (y // 8) % 80
            draw.rectangle([(0, y), (1080, y + 40)], fill=(shade, shade, shade))
        for i in range(20):
            x0 = random.randint(0, 980)
            y0 = random.randint(0, 1340)
            draw.rectangle([(x0, y0), (x0 + 100, y0 + 100)], outline=(80, 80, 80), width=2)
        images_folder = "images"
        os.makedirs(images_folder, exist_ok=True)
        gen_path = os.path.join(images_folder, "bg_generated.jpg")
        img.save(gen_path, "JPEG", quality=88)
        print(f"🖼️ Auto-generated background ready → {gen_path}")
        return gen_path
    except Exception as e:
        print(f"⚠️ Auto background generation failed: {e}")
        return None


def create_quote_image(text: str) -> str | None:
    """Random tech background + overlay text generate karo"""
    print("🖼️ Creating quote image...")
    base_image_path = download_random_tech_image()
    if not base_image_path or not os.path.exists(base_image_path):
        print("❌ Quote image ke liye background image nahi mili")
        return None

    images_folder = "images"
    os.makedirs(images_folder, exist_ok=True)
    output_path = os.path.join(images_folder, "quote_post.jpg")

    try:
        print(f"📂 Loading image: {base_image_path}")
        base_img = Image.open(base_image_path).convert("RGB")
        print(f"🖼️ Original image size: {base_img.size}")
        
        target_size = (1080, 1350)  # Instagram portrait size
        print(f"🔄 Resizing image to: {target_size}")
        base_img = ImageOps.fit(base_img, target_size, method=Image.Resampling.LANCZOS)
        print("✅ Image resized successfully")

        # Prepare overlay for readability
        overlay = Image.new("RGBA", target_size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay, "RGBA")
        box_margin = 70
        draw.rectangle(
            (
                box_margin,
                220,
                target_size[0] - box_margin,
                target_size[1] - 220,
            ),
            fill=(0, 0, 0, 150),
            outline=(255, 255, 255, 60),
            width=4,
        )

        # Load font
        try:
            font = ImageFont.truetype("arial.ttf", 64)
            font_small = ImageFont.truetype("arial.ttf", 46)
        except IOError:
            font = ImageFont.load_default()
            font_small = ImageFont.load_default()

        # Prepare text
        clean_text = text.replace("\n", " ").strip()
        wrapped_text = textwrap.fill(clean_text, width=20)

        text_x = box_margin + 30
        text_y = 260
        draw.text(
            (text_x, text_y),
            wrapped_text,
            font=font,
            fill=(255, 255, 255, 255),
            spacing=12,
        )

        footer_text = " @iamsaniydv"
        # Compute footer size robustly (use textbbox if available, fallback to textsize)
        try:
            bbox = draw.textbbox((0, 0), footer_text, font=font_small)
            footer_width = bbox[2] - bbox[0]
            footer_height = bbox[3] - bbox[1]
        except Exception:
            footer_width, footer_height = draw.textsize(footer_text, font=font_small)

        # Place footer inside the bottom margin (use box_margin so it doesn't run off the image)
        footer_x = target_size[0] - box_margin - footer_width - 20
        footer_y = target_size[1] - box_margin - footer_height - 20

        draw.text((footer_x, footer_y), footer_text, font=font_small, fill=(255, 255, 255, 200))

        final_img = Image.alpha_composite(base_img.convert("RGBA"), overlay)
        final_img.convert("RGB").save(output_path, "JPEG", quality=92)
        print(f"🖼 Quote image ready → {output_path}")
        return output_path
    except Exception as exc:
        print(f"⚠️ Quote image generate nahi ho payi: {exc}")
        return base_image_path

# ====== 2. Video Banaye (100% working - random tech image ke saath) ======
def create_reel_video(text):
    print("🎥 Video ban raha hai...")

    # Videos aur audio folders banaye agar nahi hai
    videos_folder = "videos"
    audio_folder = "audio"
    os.makedirs(videos_folder, exist_ok=True)
    os.makedirs(audio_folder, exist_ok=True)

    # Random tech image download karo
    bg_image_path = download_random_tech_image()
    if not bg_image_path or not os.path.exists(bg_image_path):
        print("❌ Background image nahi mili!")
        return None

    # Background image load + resize (new MoviePy style)
    print(f"🎥 Loading video background image: {bg_image_path}")
    bg_img = ImageClip(bg_image_path).set_duration(16)
    print(f"🖼️ Original video image size: {bg_img.size}")
    
    # Calculate new height while maintaining aspect ratio
    aspect_ratio = bg_img.size[1] / bg_img.size[0]
    new_height = int(1080 * aspect_ratio)
    print(f"🔄 Resizing video image to: (1080, {new_height}) with LANCZOS resampling")
    # Convert to PIL Image to use Pillow's resize with LANCZOS resampling
    pil_img = Image.fromarray(bg_img.img)
    resized_img = pil_img.resize((1080, new_height), Image.Resampling.LANCZOS)
    bg_img = ImageClip(np.array(resized_img)).set_duration(16)
    bg_img = bg_img.margin(left=80, right=80, top=200, bottom=200, color=(0,0,0))  # optional black border
    bg_img = bg_img.set_pos("center")

    # Background music (no robotic TTS)
    music_candidates = [
        os.path.join(audio_folder, "music.mp3"),
        os.path.join(audio_folder, "bg_music.mp3"),
        os.path.join(audio_folder, "song.mp3"),
    ]
    music_path = next((p for p in music_candidates if os.path.exists(p)), None)
    audio = None
    if music_path:
        audio = AudioFileClip(music_path).subclip(0, 16).volumex(0.6)
    else:
        gen_path = generate_background_music(audio_folder, duration_sec=16)
        if gen_path and os.path.exists(gen_path):
            audio = AudioFileClip(gen_path).subclip(0, 16).volumex(0.6)

    # Text overlay with background for better readability
    wrapped = textwrap.fill(text, width=20)
    
    # Create text clip with a semi-transparent background
    txt_clip = (TextClip(wrapped, fontsize=90, color='white', font='Arial-Bold',
                        stroke_color='black', stroke_width=3, size=(1000, None),
                        method='caption', align='center')
               .set_position('center')
               .set_duration(16))
    
    # Add a semi-transparent background behind text
    text_bg = (ColorClip(size=(1100, txt_clip.size[1] + 40), color=(0, 0, 0, 180))
              .set_position(('center', 'center'))
              .set_duration(16))
    
    # Combine text with its background
    text_with_bg = CompositeVideoClip([text_bg, txt_clip])
    
    # Position text in the center with some margin from bottom
    text_final = text_with_bg.set_position(('center', bg_img.size[1] * 0.6))

    # Combine all elements
    final = CompositeVideoClip([bg_img, text_final])
    if audio:
        final = final.set_audio(audio)
    output = os.path.join(videos_folder, "reel.mp4")
    final.write_videofile(output, fps=30, codec="libx264", audio_codec="aac", threads=6, verbose=False, logger=None)
    print(f"✅ Video successfully ban gaya → {output} (size ~10-15MB)")
    return output

def generate_background_music(audio_folder: str, duration_sec: int = 16) -> str | None:
    os.makedirs(audio_folder, exist_ok=True)
    path = os.path.join(audio_folder, "auto_music.wav")
    sr = 44100
    t = np.linspace(0, duration_sec, int(sr * duration_sec), endpoint=False)
    base_freqs = [220.0, 277.18, 329.63, 392.0, 440.0]
    pattern_len = int(duration_sec * 2)
    note_duration = duration_sec / pattern_len
    x = np.zeros_like(t)
    for i in range(pattern_len):
        start = int(i * note_duration * sr)
        end = int((i + 1) * note_duration * sr)
        freq = random.choice(base_freqs)
        env_len = end - start
        if env_len <= 0:
            continue
        env = np.concatenate([
            np.linspace(0, 1, max(1, env_len // 10)),
            np.ones(max(1, env_len // 2)),
            np.linspace(1, 0, max(1, env_len // 10))
        ])
        env = np.pad(env, (0, max(0, env_len - env.size)), 'constant')
        seg_t = np.linspace(0, note_duration, env_len, endpoint=False)
        tone = np.sin(2 * np.pi * freq * seg_t) * env
        x[start:end] += tone
    x = x / (np.max(np.abs(x)) + 1e-8)
    x = (x * 32767).astype(np.int16)
    try:
        with wave.open(path, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sr)
            wf.writeframes(x.tobytes())
        return path
    except Exception:
        return None

# ====== 3. Instagram Post (Reel) ======
def post_instagram(video_path):
    if not INSTAGRAM_USERNAME or not INSTAGRAM_PASSWORD:
        return {"ok": False, "error": "Missing Instagram credentials in config"}

    try:
        cl = Client()
        cl.set_settings({})
        cl.delay_range = [2, 6]

        # Use saved session
        if os.path.exists("session.json"):
            cl.load_settings("session.json")
            cl.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
        else:
            cl.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
            cl.dump_settings("session.json")

        # Random hashtags
        tech_hashtags = [
            "#tech #technology #coding #programming #hindi #reels #viral",
            "#tech #coding #programming #webdevelopment #hindi #reels #trending",
            "#tech #technology #ai #machinelearning #hindi #reels #viral",
            "#tech #coding #softwaredevelopment #hindi #reels #trending",
            "#tech #programming #developer #hindi #reels #viral",
            "#tech #technology #webdev #coding #hindi #reels #trending"
        ]
        
        caption = f"💻 Tech Tips & Tricks 💻\n\n{random.choice(tech_hashtags)}\n\n#tech #coding #programming #technology #developer #hindi #reels #viral #trending #techguru #codinglife #programmer #webdeveloper #technews"

        # Simple clip_upload call
        try:
            resp = cl.clip_upload(video_path, caption=caption)
            # Return instagrapi response (could be model object)
            return {"ok": True, "response": resp}
        except ValidationError as ve:
            error_str = str(ve)
            if "audio_filter_infos" in error_str:
                # Known parsing issue: upload may have succeeded
                return {"ok": True, "warning": "response parsing error (pydantic)", "detail": error_str}
            else:
                return {"ok": False, "error": error_str}

    except Exception as e:
        return {"ok": False, "error": str(e), "hint": "Check 2FA, suspicious login alerts, and session.json"}


# ====== 4. Instagram Post (Image-only) ======
def post_instagram_image(caption_text: str, image_path: str | None = None):
    """Sirf image + caption ke saath normal Instagram photo post kare"""
    if not INSTAGRAM_USERNAME or not INSTAGRAM_PASSWORD:
        return {"ok": False, "error": "Missing Instagram credentials in config"}

    try:
        # Agar image_path nahi diya, to text overlay ke saath naya image bana do
        if not image_path:
            image_path = create_quote_image(caption_text)
        if not image_path or not os.path.exists(image_path):
            raise Exception("Image path invalid ya image generate nahi ho payi")

        # PhotoUpload ke liye sirf JPG/PNG/WEBP allowed
        valid_ext = os.path.splitext(image_path)[1].lower()
        if valid_ext not in [".jpg", ".jpeg", ".png", ".webp"]:
            raise Exception(f"Invalid image format for photo upload: {valid_ext}")

        cl = Client()
        cl.set_settings({})
        cl.delay_range = [2, 6]

        # Use saved session
        if os.path.exists("session.json"):
            cl.load_settings("session.json")
            cl.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
        else:
            cl.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
            cl.dump_settings("session.json")

        # Normal post ke liye thode simple hashtags
        tech_hashtags = [
            "#tech #coding #programming #developer #hindi",
            "#technology #learncoding #programmerlife",
            "#python #javascript #kotlin #webdevelopment",
        ]

        caption = f"{caption_text}\n\n{random.choice(tech_hashtags)}"

        try:
            resp = cl.photo_upload(image_path, caption=caption)
            return {"ok": True, "response": resp}
        except ValidationError as ve:
            return {"ok": False, "error": str(ve)}
        
    except Exception as e:
        return {"ok": False, "error": str(e), "hint": "Check 2FA, suspicious login alerts, and session.json"}

# ====== MAIN ======
def main():
    print("="*70)
    print("       🚀 TECH REEL AUTO POST MACHINE FULL POWER PE!       ")
    print("="*70 + "\n")

    tech_content = generate_tech_script()
    print(f"Tech Content → {tech_content}\n")

    video = create_reel_video(tech_content)
    if video:
        post_instagram(video)

    print("\n🎉 KHTM! Ab Instagram kholo aur dekho Tech Reel live hai ya nahi 😎")

if __name__ == "__main__":
    main()
