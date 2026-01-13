#!/usr/bin/env python3
"""
translate_video.py
مثال عملي: استخراج تفريغ من فيديو ثم ترجمة المقاطع للعربية وإنشاء ملف SRT.
الاعتماديات: whisper, transformers (Helsinki-NLP), langdetect, ffmpeg
"""
import argparse
import os
import subprocess
import tempfile
from pathlib import Path
from langdetect import detect
from tqdm import tqdm
import whisper
import math

# lazy import transformers to avoid heavy import if not used
def load_translator_for(src_lang):
    """
    يحاول تحميل نموذج Marian مناسب من Helsinki-NLP لـ <src_lang> -> ar
    دَعْم للغات شائعة: en, fr, es, de, ru, pt, it, nl
    """
    from transformers import pipeline
    mapping = {
        "en": "Helsinki-NLP/opus-mt-en-ar",
        "fr": "Helsinki-NLP/opus-mt-fr-ar",
        "es": "Helsinki-NLP/opus-mt-es-ar",
        "de": "Helsinki-NLP/opus-mt-de-ar",
        "ru": "Helsinki-NLP/opus-mt-ru-ar",
        "pt": "Helsinki-NLP/opus-mt-pt-ar",
        "it": "Helsinki-NLP/opus-mt-it-ar",
        "nl": "Helsinki-NLP/opus-mt-nl-ar",
    }
    model_name = mapping.get(src_lang)
    if model_name:
        device = 0 if is_cuda_available() else -1
        return pipeline("translation", model=model_name, device=device)
    return None

def is_cuda_available():
    try:
        import torch
        return torch.cuda.is_available()
    except Exception:
        return False

def extract_audio(infile, out_audio):
    # استخدام ffmpeg لاستخراج صوت mono 16kHz (مناسب للـ ASR)
    cmd = [
        "ffmpeg", "-y", "-i", str(infile),
        "-ac", "1", "-ar", "16000",
        "-vn", str(out_audio)
    ]
    subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def seconds_to_srt_timestamp(seconds):
    # SRT: HH:MM:SS,mmm
    ms = int(round(seconds * 1000))
    s, ms = divmod(ms, 1000)
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

def write_srt(segments, out_path):
    with open(out_path, "w", encoding="utf-8") as f:
        for i, seg in enumerate(segments, start=1):
            start = seconds_to_srt_timestamp(seg["start"])
            end = seconds_to_srt_timestamp(seg["end"])
            text = seg["text"].replace("-->", "->")
            f.write(f"{i}\n{start} --> {end}\n{text}\n\n")

def batch_translate_segments(segments, translator, batch_size=8):
    """
    translator expected to be a Hugging Face pipeline that accepts list[str] and returns list of dicts with 'translation_text'
    """
    translated = []
    texts = [seg["text"] for seg in segments]
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        out = translator(batch)
        # pipeline returns list of dicts or strings depending on version
        for o in out:
            if isinstance(o, dict) and "translation_text" in o:
                translated.append(o["translation_text"])
            elif isinstance(o, str):
                translated.append(o)
            else:
                translated.append(str(o))
    # attach to segments
    for seg, tr in zip(segments, translated):
        seg["text"] = tr
    return segments

def main():
    p = argparse.ArgumentParser(description="ترجمة فيديو إلى العربية وانتاج SRT")
    p.add_argument("--input", "-i", required=True, help="ملف الفيديو")
    p.add_argument("--output", "-o", default="out.srt", help="ملف SRT الناتج")
    p.add_argument("--whisper-model", default="small", help="حجم نموذج Whisper (tiny, base, small, medium, large)")
    p.add_argument("--burn", action="store_true", help="حرق الترجمة داخل الفيديو باستخدام ffmpeg")
    p.add_argument("--out-video", default="out_subbed.mp4", help="اسم الفيديو الناتج لو اخترت --burn")
    args = p.parse_args()

    infile = Path(args.input)
    if not infile.exists():
        raise SystemExit("ملف الفيديو غير موجود")

    with tempfile.TemporaryDirectory() as tmpdir:
        audio_path = Path(tmpdir) / "audio.wav"
        print("1) استخراج الصوت...")
        extract_audio(infile, audio_path)

        print(f"2) تحميل نموذج Whisper ({args.whisper_model}) وبدء التفريغ (transcription)...")
        model = whisper.load_model(args.whisper_model)
        # task transcribe: سيحاول كشف اللغة إذا لم تُعطَ
        result = model.transcribe(str(audio_path), verbose=False)
        # segments: قائمة dicts مع start, end, text
        segments = []
        for seg in result.get("segments", []):
            segments.append({
                "start": seg["start"],
                "end": seg["end"],
                "text": seg["text"].strip()
            })

        if not segments:
            print("لم يتم الحصول على مقاطع؛ ربما فشل التفريغ.")
            return

        # كشف اللغة (اعتمادًا على نص أول مقطع)
        raw_text_for_lang = " ".join(s["text"] for s in segments[:3])
        try:
            detected = detect(raw_text_for_lang)
            print("تم كشف اللغة المصدر كـ:", detected)
        except Exception:
            detected = None
            print("فشل كشف اللغة؛ سيتم الافتراض أنها إنجليزية.")

        print("3) تحميل نموذج الترجمة أو اختيار طريقة بديلة...")
        translator = None
        if detected:
            translator = load_translator_for(detected)
        if translator is None:
            print("لم يتم العثور على نموذج Marian مناسب للغة المصدر، سأحاول استخدام الإنجليزية كبديل.")
            translator = load_translator_for("en")
            if translator is None:
                raise SystemExit("لا يوجد نموذج ترجمة متاح محليًا. يمكنك تثبيت نموذج مناسب أو استخدام API خارجي.")

        print("4) ترجمة المقاطع إلى العربية...")
        segments = batch_translate_segments(segments, translator, batch_size=4)

        print("5) كتابة ملف SRT:", args.output)
        write_srt(segments, args.output)

        if args.burn:
            print("6) حرق الترجمة داخل الفيديو (عملية ffmpeg)...")
            # ملاحظة: قد تحتاج إلى تحديد ملف فونت يدعم العربية وlibass
            cmd = [
                "ffmpeg", "-y", "-i", str(infile),
                "-vf", f"subtitles={args.output}:force_style='Fontname=Arial,Fontsize=24'",
                "-c:a", "copy", args.out_video
            ]
            print("تشغيل:", " ".join(cmd))
            subprocess.check_call(cmd)
            print("الفيديو الناتج:", args.out_video)

    print("انتهت المعالجة. ملف SRT جاهز.")

if __name__ == "__main__":
    main()