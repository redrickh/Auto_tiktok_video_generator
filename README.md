# Quiz Video Generator with OpenAI and MoviePy

This Python script leverages the power of OpenAI and MoviePy to create engaging quiz videos. It randomly selects questions and answers, generates audio using OpenAI's TTS, and assembles a dynamic video with countdowns, questions, answers, and a unique visual touch. The resulting quiz video is not only visually appealing but also includes an audio component for an immersive experience.
Something like this: https://www.tiktok.com/@emilyvilaga

## Key Features:
- Random selection of questions and answers from a predefined set.
- OpenAI TTS for generating lifelike audio responses.
- Dynamic video assembly with MoviePy, including countdowns, questions, and answers.
- Integration of a unique visual element – a colored stripe highlighting the correct answer.
- Video upload to TikTok using the [TikTok uploader library](https://github.com/redrickh/tiktok-uploader) (forked version).

## Requirements:
- Python 3.6 or above
- OpenAI library
- MoviePy library
- TikTok uploader library (Forked version: [redrickh/tiktok-uploader](https://github.com/redrickh/tiktok-uploader))

## Usage:
1. Set up your OpenAI API key in the 'openai_key.py' file.
2. Ensure the required libraries are installed using the provided 'requirements.txt' file.
3. Clone the repository using the following command:
   ```bash
   git clone https://github.com/redrickh/Auto_tiktok_video_generator.git

Feel free to customize the script for your specific needs and experiment with different video templates for added variety.

*Note: Ensure you have the necessary permissions to use the OpenAI API and adhere to TikTok's policies when uploading videos.*

