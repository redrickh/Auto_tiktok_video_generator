import time
from openai import OpenAI
from pathlib import Path
from moviepy.editor import *
from quiz_db import questions_and_answers
from moviepy.video.fx.loop import loop
from tiktok_uploader.upload import upload_video
from moviepy.audio.fx.volumex import volumex
from moviepy.video.fx.margin import margin
from openai_key import *
import random


openai_client = OpenAI(api_key=key)  # your open_ai key goes here
number_of_questions = len(questions_and_answers)
print(f"There are a total of {number_of_questions} questions in the current set.")

# Choose a random question from the list
random_question = random.choice(questions_and_answers)
quiz_question = random_question["kérdés"]  # random question from quiz_db.py


def wrap_text(text, limit):
    words = text.split(' ')
    lines = []
    current_line = []
    current_length = 0
    for word in words:
        if current_length + len(word) <= limit:
            current_length += len(word) + 1  # word length + space
            current_line.append(word)
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
            current_length = len(word)
    lines.append(' '.join(current_line))  # Add remaining words
    return '\n'.join(lines)


# Create the text clip for the question, set its position
max_characters = 20

# The text wraps every 20 characters, but not mid-word
processed_text = wrap_text(quiz_question, max_characters)
# Set the fontsize based on the text length

# Dynamically calculate text position to center it
video_width = 1920
text_width = len(processed_text) * 15  # Adjust the factor based on font and size
text_position = (video_width - text_width) // 2

question = TextClip(processed_text, fontsize=60, font='Amiri-Bold', color='black').set_position(("center", 600))

# Create a list of answers
generated_text = random_question["válaszok"]  # answers from quiz_db.py
clean_answer = random_question["helyes_válasz"]  # correct answer from quiz_db.py

# Current question
print(quiz_question)
# The 'generated_text' variable contains a list of answer choices
print("Answer choices:", generated_text)

# The 'clean_answer' variable contains the correct answer
print("Correct answer:", clean_answer)

# Set the duration for the question and each answer
start_time_answer1 = 1  # start time for the FIRST answer in seconds
start_time_answer2 = 1.1  # start time for the SECOND answer in seconds
start_time_answer3 = 1.2  # start time for the THIRD answer in seconds

# Shuffle the answers
shuffled_answers = random.sample(random_question['válaszok'], len(random_question['válaszok']))

# {shuffled_answers[0]} OR {shuffled_answers[1]} OR {shuffled_answers[2]}
tts_input = f"{quiz_question}? {shuffled_answers[0]} vagy {shuffled_answers[1]} vagy {shuffled_answers[2]}"

speech_response = openai_client.audio.speech.create(
    model="tts-1-hd",
    voice="nova",
    input=f"{tts_input}?\n\n"
          f"Írd le kommentben a helyes választ, ha tudod.\n"  # Write the correct answer in the comment if you know.
)
speech_file_path = Path(__file__).parent / "generated_audio.mp3"
with open(speech_file_path, 'wb') as file:
    file.write(speech_response.content)

# Create the TextClips for each answer, with fixed labels (A, B, C) but shuffled answers
answer1 = TextClip(f"A) {shuffled_answers[0]}", fontsize=55, font='Amiri-Bold', color='black').set_start(
    start_time_answer1)
answer2 = TextClip(f"B) {shuffled_answers[1]}", fontsize=55, font='Amiri-Bold', color='black').set_start(
    start_time_answer2)
answer3 = TextClip(f"C) {shuffled_answers[2]}", fontsize=55, font='Amiri-Bold', color='black').set_start(
    start_time_answer3)

# Create a list of answers (alphabetical label order)
answers = [answer1, answer2, answer3]

# Create a list of default positions for each answer
positions = [(280, 980), (280, 1140), (280, 1300)]

# Create a list of pairs [(label, position), (label, position), (label, position)]
pairs = list(zip(answers, positions))

# Shuffle the pairs
random.shuffle(pairs)

# Load the rendered TTS audio
audio = AudioFileClip("generated_audio.mp3")

# Load the background audio and reduce its volume
background_audio = AudioFileClip("song.mp3").fx(volumex, 0.04)  # 5% of the original volume

# Get the duration of the audio
audio_duration = audio.duration

# Make sure the background_audio is the same duration as the main audio
background_audio = background_audio.subclip(0, audio_duration)

# Combine the two audio clips
composite_audio = CompositeAudioClip([background_audio, audio])

# If you want more video template
video_templates = ["quiz1.mp4", "quiz2.mp4"]
chosen_template = random.choice(video_templates)
print(chosen_template)
# Load the full video first to get its duration
full_video = VideoFileClip(chosen_template)

# Get the last 1 second (without cutting the original video)
video_last_sec = full_video.subclip(full_video.duration - 1)

# Play the whole video first (5 seconds long)
video_first_part = full_video.subclip(0, 5)

# Loop the last second of video until it matches the remaining duration of the audio
looped_video = loop(video_last_sec, duration=audio_duration - 5)


# Concatenate the first part of the video with the looped part
final_video = concatenate_videoclips([video_first_part, looped_video])

# Set the audio of the video
final_video_with_audio_and_music = final_video.set_audio(composite_audio)

# full video length, but make it shorter for the Countdown
duration = final_video.duration - 3

# Now we divide the total time by 5 (counting down from 5)
time_per_number = duration / 5

clips = []

for i in range(5, -1, -1):  # Countdown from 5 to 0
    clip = TextClip(str(i), fontsize=150, color='black').set_duration(time_per_number)
    clips.append(clip)

# Creating the countdown clip
countdown_clip = concatenate_videoclips(clips).set_pos(('center', 'bottom'))

# Setting the position of the countdown clip
countdown_clip = countdown_clip.set_position(lambda t: ('center', countdown_clip.h - -1400))

# Applying crossfade
countdown_clip = countdown_clip.crossfadein(1).crossfadeout(1)

clean_answer_pos = None
answers_texts = [f"A) {shuffled_answers[0]}", f"B) {shuffled_answers[1]}", f"C) {shuffled_answers[2]}"]

shuffled_pairs = list(zip(answers, positions, answers_texts))

for pair in shuffled_pairs:
    if clean_answer in pair[2]:
        clean_answer_pos = pair[1]
        break

if clean_answer_pos is None:
    print(f"Didn't find this answer: {clean_answer}")

random_values = random.sample(range(256), 3)  # random colours


# Setting the number of pixels per character
pix_per_char = 55

# Calculating the length of the stripe based on the length of the cleaned answer
stripe_len = len(clean_answer) * pix_per_char

# Creating a colored stripe clip with a specified length and color (green in this case)
stripe = ColorClip((stripe_len, 10), col=(0, 102, 51))

# Adjusting the position of the stripe relative to the cleaned answer position
stripe = stripe.set_position((clean_answer_pos[0], clean_answer_pos[1] + 60))

# Calculating the start time for the stripe, ensuring it begins after all previous clips
stripe_start_time = sum(clip.duration for clip in clips)

# Setting the start time and duration of the stripe to fit within the remaining duration of the final video
stripe = stripe.set_start(stripe_start_time + 1).set_duration(final_video.duration - stripe_start_time)

# Applying a crossfade effect to smoothly fade in the stripe
stripe = stripe.crossfadein(0)


# Set stripe start time
stripe_start_time = sum(clip.duration for clip in clips)

# Lay out all components to add to the video
comps = [final_video_with_audio_and_music, question.set_start(0).set_duration(audio_duration)]

# Add answers to comps with their FIXED positions
comps.extend(answer.set_position(pos).set_duration(audio_duration) for answer, pos in pairs)

comps.append(countdown_clip.set_start(0))

# Add stripe to comps
comps.append(stripe.set_start(stripe_start_time))

final_video = CompositeVideoClip(comps)
# Add the margin to the final_video
final_video = margin(final_video, 30, color=(random_values[0], random_values[1], random_values[2]))

final_video = final_video.subclip(0, final_video.duration - 1.1)

timestamp = time.time()

# Define the directory path
directory = "quiz_videos"

# Create the directory
os.makedirs(directory, exist_ok=True)

# Define the full file path with the filename
full_path = os.path.join(directory, f"quiz_output_{timestamp}.mp4")

# Save the file
final_video.write_videofile(full_path, codec="libx264")

desc_title = (f"Írj 3 releváns hastaget, plusz ezeket is add hozzá: #fyp #talaloskerdes #rejtveny #riddle"
              f" Erről a szövegről: {quiz_question}"
              f"Csak a hastageket kérem a válaszodban, vesszővel és szóközzel elválasztva egymástól!")
#  Write 3 relevant hashtags, and also add these: #fyp #riddle #puzzle #quiz
#  About this text: {quiz_question}
#  Please provide only the hashtags in your answer, separated by commas and spaces!

desc_title_text = openai_client.chat.completions.create(
    model="gpt-4-0125-preview",
    messages=[
        {"role": "user", "content": desc_title}
    ],
    max_tokens=4000,
)

desc_title_final = desc_title_text.choices[0].message.content.strip('"')
print(desc_title_final)

# single video upload
upload_video(f"{full_path}",
             description=f"Tetszett a találós kérdés? A megfejtés: {clean_answer} / {desc_title_final}",
             #  Liked the riddle? The solution: {clean_answer} / {desc_title_final}
             cookies='cookies.txt',
             browser='chrome',
             )
print("Script is finished!")
