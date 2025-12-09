Legal Specs App (FastAPI + SQLite) – V3

- لا يتم عرض JSON للمستخدم.
- مفاتيح الـ JSON تظهر كعناوين وحقول نصية في الواجهة.
- القيم تظهر في TextBoxes و TextAreas يمكن تعديلها.
- كل تعديل يحفظ كـ Version جديد في قاعدة البيانات مع الاحتفاظ بكل الإصدارات.
- صفحة "سجل النسخ" تعرض جميع الإصدارات، مع رابط لعرض أي نسخة.

المجلدات المهمة:
  app/data   : ملفات Markdown للأشجار (اختياري).
  app/specs  : ضع هنا ملفات JSON الخاصة بالـ specs.

التشغيل:
  1) cd legal_specs_app_v3
  2) python -m venv .venv   (اختياري)
     ثم تفعيل الـ venv
  3) pip install -r requirements.txt
  4) uvicorn app.main:app --reload
  5) افتح http://127.0.0.1:8000/

التعديل:
  - ادخل إلى أي بند (Node).
  - سترى عرضًا منسقًا للقيم (بدون JSON).
  - اضغط على "تعديل" (Basic Auth: admin / change-this-password).
  - عدل الحقول ثم "حفظ كنسخة جديدة".
  - من "سجل النسخ" يمكنك فتح أي نسخة سابقة وعرض محتواها.
