import fs from 'fs';
import path from 'path';
import axios from 'axios';
import { Storage } from 'megajs';

const MEGA_EMAIL = process.env.MEGA_EMAIL;
const MEGA_PASSWORD = process.env.MEGA_PASSWORD;

// Step 1: Generate Video Clip via Pollinations AI
async function generateVideoClip(prompt, outputFile) {
  const encodedPrompt = encodeURIComponent(prompt);
  // Pollinations video endpoint format update
  const url = `https://image.pollinations.ai/prompt/${encodedPrompt}?model=video&nologo=true`;

  console.log(`Generating video for prompt: "${prompt}"...`);
  
  try {
    const response = await axios({
      method: 'get',
      url: url,
      responseType: 'arraybuffer',
      timeout: 60000 // 60 seconds timeout
    });

    const buffer = Buffer.from(response.data);
    
    // File Validation: 10KB-യിൽ കുറവാണെങ്കിൽ അത് വീഡിയോ അല്ല (എറർ പേജ് ആയിരിക്കും)
    if (buffer.length < 10000) {
      console.error(`Error: Received invalid video buffer size (${buffer.length} bytes).`);
      return false;
    }

    fs.writeFileSync(outputFile, buffer);
    console.log(`Video clip generated successfully. File size: ${(buffer.length / 1024 / 1024).toFixed(2)} MB`);
    return true;
  } catch (error) {
    console.error('Video generation failed:', error.message);
    return false;
  }
}

// Step 2: Upload Video to MEGA.nz
async function uploadToMega(filePath) {
  if (!MEGA_EMAIL || !MEGA_PASSWORD) {
    throw new Error("MEGA_EMAIL and MEGA_PASSWORD environment variables are required!");
  }

  console.log("Logging in to MEGA.nz...");
  const storage = await new Storage({
    email: MEGA_EMAIL,
    password: MEGA_PASSWORD
  }).ready;

  console.log(`Uploading ${filePath} to MEGA...`);
  const fileName = path.basename(filePath);
  const fileData = fs.readFileSync(filePath);

  const uploadedFile = await storage.upload({
    name: fileName,
    size: fileData.length
  }, fileData).complete;

  const link = await uploadedFile.link();
  console.log(`Uploaded successfully to MEGA! Public Link: ${link}`);
}

// Main Automation Pipeline
async def main() {
  console.log("Starting AI Video Generation Pipeline (Node.js)...");

  const videoPath = "output_clip.mp4";
  const prompt = "A futuristic digital server network glowing blue, high quality";

  const success = await generateVideoClip(prompt, videoPath);

  if (success) {
    await uploadToMega(videoPath);
    console.log("Pipeline execution completed successfully.");
  } else {
    console.log("Skipping MEGA upload because valid video was not generated.");
  }
}

main().catch(err => {
  console.error("Error in pipeline:", err);
});
