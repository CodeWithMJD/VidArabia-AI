# مشروع: ترجمة أي ملف فيديو إلى العربية

هذا مشروع بسيط يقوم بـ:
1. استخراج الصوت من ملف فيديو.
2. تفريغ الكلام (transcription) مع توقيتات باستخدام Whisper (محليًا).
3. ترجمة كل مقطع إلى العربية باستخدام نماذج Marian (Helsinki-NLP) من Hugging Face أو بدائل سحابية.
4. إخراج ملف ترجمات SRT، وخيار لحرق الترجمة في الفيديو بواسطة ffmpeg.

المتطلبات الأساسية
- Python 3.8+
- ffmpeg مثبت ومرئي في PATH
- GPU (اختياري) لتسريع عمليات Whisper وTransformer

التثبيت (بيئة افتراضية موصى بها)
```bash
python -m venv venv
source venv/bin/activate   # أو venv\Scripts\activate على ويندوز
pip install -r requirements.txt
```

كيفية الاستخدام
1. توليد ملف SRT فقط:
```bash
python translate_video.py --input input.mp4 --output out.srt
```

2. توليد SRT ثم حرقها داخل الفيديو:
```bash
python translate_video.py --input input.mp4 --output out.srt --burn --out-video output_subbed.mp4
```

خيارات مهمة
- `--whisper-model`: اختر حجم نموذج Whisper مثل `small`, `base`, `medium`, `large`. كلما كبر النموذج تحسنت الدقة لكن احتاج GPU وذاكرة أكبر.
- الترجمة: السكربت يحاول اختيار نموذج Marian مناسب للغة المصدر (en->ar, fr->ar, es->ar, ...). إذا كانت اللغة غير مدعومة يختار طريقًا بديلاً (سيندر إرشادات في المخرجات).

ملاحظات
- جودة الترجمة تعتمد على دقة التفريغ الأصلي. لغات نادرة أو جودة صوت منخفضة تتطلب ضبط/نماذج أكبر.
- لحرق ترجمات عربية بشكل صحيح قد تحتاج إلى ملف فونت يدعم العربية ويُمكّن libass من عرض الحروف، مثال: `ffmpeg -i in.mp4 -vf "subtitles=out.srt:force_style='Fontname=Arial,Fontsize=24'" ...`