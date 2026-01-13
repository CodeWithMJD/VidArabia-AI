# VidArabia-AI
#Tarjim-Whisper: AI Video Transcription & Translation
ترجم-ويسبر: تفريغ وترجمة الفيديوهات بالذكاء الاصطناعي
Overview | نبذة عن المشروع
EN: An automated tool designed to extract audio from videos, transcribe it using OpenAI's Whisper, and translate the text into Arabic using Helsinki-NLP models. The final output is a professional .srt file or a video with burned-in subtitles.

AR: أداة مؤتمتة مصممة لاستخراج الصوت من الفيديوهات، وتحويله إلى نص باستخدام تقنية Whisper من OpenAI، ثم ترجمة النص إلى العربية باستخدام نماذج Helsinki-NLP. النتيجة النهائية هي ملف ترجمة .srt احترافي أو فيديو مترجم جاهز.

Key Features | المميزات الرئيسية
Automatic Transcription: Converts speech to text with high accuracy.

AI Translation: Uses MarianMT models for high-quality Arabic translation.

Subtitle Generation: Automatically generates .srt files with precise timestamps.

Video Subtitle Burning: Optional feature to hardcode subtitles onto the video using FFmpeg.

Language Detection: Automatically detects the source language of the video.

Tech Stack | التقنيات المستخدمة
Python 3.x

OpenAI Whisper: (Speech-to-Text)

Hugging Face Transformers: (Translation Models)

FFmpeg: (Audio/Video Processing)

Langdetect: (Language Identification)

Installation | التثبيت
Bash

# Clone the repository
git clone https://github.com/YourUsername/Tarjim-Whisper.git

# Install dependencies
pip install openai-whisper transformers torch langdetect tqdm
Note: You must have FFmpeg installed on your system.

Usage | طريقة الاستخدام
EN: To translate a video and generate an SRT file, run: AR: لترجمة فيديو وإنشاء ملف SRT، قم بتشغيل الأمر:

Bash

python translate_video.py -i input_video.mp4 -o output_subtitles.srt
To burn subtitles into the video | لحرق الترجمة داخل الفيديو:

Bash

python translate_video.py -i video.mp4 --burn
Future Improvements | التحديثات المستقبلية
[ ] Add support for multiple target languages (not just Arabic).

[ ] Implement an AI-based Executive Summary for the video content.

[ ] Build a simple Web Interface using Streamlit.

💡 لماذا هذا المشروع في ملفي الشخصي؟ (For Recruiters)
هذا المشروع يثبت مهاراتي في:

التعامل مع البيانات غير المهيكلة (Unstructured Data Processing).

دمج نماذج الذكاء الاصطناعي (AI Integration) في تطبيقات عملية.

إدارة العمليات المعقدة والملفات عبر لغة بايثون.
