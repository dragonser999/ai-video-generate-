import os
import asyncio
import requests
import urllib.parse
import edge_tts
from mega2 import Mega

# Environment Variables
MEGA_EMAIL = os.getenv("MEGA_EMAIL")
MEGA_PASSWORD = os.getenv("MEGA_PASSWORD")

# Step 1: Generate Audio using Edge-TTS
async def generate_audio(text, output_file):
    communicate = edge_tts.Communicate(text, "en-US-ChristopherNeural")
    await communicate.save(output_file)

# Step 2: Generate Video Clip via Pollinations AI (100% Free)
def generate_video_clip(prompt, output_file):
    encoded_prompt = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?model=video"
    
    print(f"Generating video for prompt: '{prompt}'...")
    response = requests.get(url)
    
    if response.status_code == 200:
        with open(output_file, "wb") as f:
            f.write(response.content)
        return True
    else:
        print(f"Pollinations API Error Status: {response.status_code}")
        return False

# Step 3: Upload Video to MEGA.nz
def upload_to_mega(file_path):
    if not MEGA_EMAIL or not MEGA_PASSWORD:
        raise ValueError("MEGA_EMAIL and MEGA_PASSWORD environment variables are required in Railway!")
        
    print("Logging in to MEGA.nz...")
    mega = Mega()
    m = mega.login(MEGA_EMAIL, MEGA_PASSWORD)
    
    print(f"Uploading {file_path} to MEGA...")
    file = m.upload(file_path)
    link = m.get_upload_link(file)
    print(f"Uploaded successfully to MEGA! Public Link: {link}")

# Main Automation Pipeline
async def main():
    print("Starting AI Video Generation Pipeline...")
    
    # 1. Text to Audio
    audio_path = "output_audio.mp3"
    script = "Welcome to the automated AI video creator system running on Railway!"
    await generate_audio(script, audio_path)
    print("Audio generated.")

    # 2. Prompt to Video
    video_path = "output_clip.mp4"
    prompt = "A futuristic digital server network glowing blue, high quality"
    if generate_video_clip(prompt, video_path):
        print("Video clip generated successfully.")
        
        # 3. Upload Result to MEGA
        upload_to_mega(video_path)
        print("Pipeline execution completed successfully.")
    else:
        print("Video generation failed. Skipping MEGA upload.")

if __name__ == "__main__":
    asyncio.run(main())
