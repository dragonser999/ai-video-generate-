import os
import json
import asyncio
import requests
import edge_tts
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Environment Variables
HF_API_KEY = os.getenv("HF_API_KEY")
GDRIVE_FOLDER_ID = os.getenv("GDRIVE_FOLDER_ID")
GDRIVE_JSON_STR = os.getenv("GDRIVE_SERVICE_ACCOUNT_JSON")

# Hugging Face Video Model Endpoint (Free Inference API)
HF_API_URL = "https://api-inference.huggingface.co/models/damo-vilab/text-to-video-ms-1.7b"

# Google Drive Auth Setup
def get_drive_service():
    service_account_info = json.loads(GDRIVE_JSON_STR)
    credentials = Credentials.from_service_account_info(
        service_account_info,
        scopes=['https://www.googleapis.com/auth/drive.file']
    )
    return build('drive', 'v3', credentials=credentials)

# Step 1: Generate Audio using Edge-TTS
async def generate_audio(text, output_file):
    communicate = edge_tts.Communicate(text, "en-US-ChristopherNeural")
    await communicate.save(output_file)

# Step 2: Generate Video Clip via Hugging Face API
def generate_video_clip(prompt, output_file):
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    payload = {"inputs": prompt}
    
    response = requests.post(HF_API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        with open(output_file, "wb") as f:
            f.write(response.content)
        return True
    else:
        print(f"Hugging Face API Error: {response.status_code} - {response.text}")
        return False

# Step 3: Upload Video to Google Drive
def upload_to_drive(file_path, folder_id):
    service = get_drive_service()
    file_metadata = {
        'name': os.path.basename(file_path),
        'parents': [folder_id]
    }
    media = MediaFileUpload(file_path, resumable=True)
    uploaded_file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()
    print(f"Uploaded successfully! File ID: {uploaded_file.get('id')}")

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
    prompt = "A cinematic view of a futuristic digital server network, 4k"
    if generate_video_clip(prompt, video_path):
        print("Video clip generated.")
        
        # 3. Stitch & Merge (Placeholder for FFmpeg)
        # Note: You can add FFmpeg subprocess commands here to combine audio & video
        
        # 4. Upload Result to Drive
        upload_to_drive(video_path, GDRIVE_FOLDER_ID)
        print("Pipeline execution completed successfully.")

if __name__ == "__main__":
    asyncio.run(main())
