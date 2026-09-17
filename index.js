import fs from 'fs';
import path from 'path';
import axios from 'axios';
import { Storage } from 'megajs';

// Railway Variables-ൽ നിന്ന് Email, Password എടുക്കുന്നു
const MEGA_EMAIL = process.env.MEGA_EMAIL;
const MEGA_PASSWORD = process.env.MEGA_PASSWORD;

// Step 1: Pollinations AI വഴി വീഡിയോ ജനറേറ്റ് ചെയ്യുന്നു
async function generateVideoClip(prompt, outputFile) {
  const encodedPrompt = encodeURIComponent(prompt);
  const url = `https://image.pollinations.ai/prompt/${encodedPrompt}?model=video`;

  console.log(`Generating video for prompt: "${prompt}"...`);
  
  try {
    const response = await axios({
      method: 'get',
      url: url,
      responseType: 'arraybuffer'
    });

    fs.writeFileSync(outputFile, response.data);
    console.log('Video clip generated successfully.');
    return true;
  } catch (error) {
    console.error('Video generation failed:', error.message);
    return false;
  }
}

// Step 2: MEGA.nz അക്കൗണ്ടിലേക്ക് അപ്‌ലോഡ് ചെയ്യുന്നു
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
async function main() {
  console.log("Starting AI Video Generation Pipeline (Node.js)...");

  const videoPath = "output_clip.mp4";
  const prompt = "A futuristic digital server network glowing blue, high quality";

  const success = await generateVideoClip(prompt, videoPath);

  if (success) {
    await uploadToMega(videoPath);
    console.log("Pipeline execution completed successfully.");
  } else {
    console.log("Skipping upload due to video generation failure.");
  }
}

main().catch(err => {
  console.error("Error in pipeline:", err);
});
