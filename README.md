# RUFA GOLD ERP

نظام إدارة شركة تسويق عقاري مبني بـ Django + PostgreSQL.

## بيانات الدخول الأولى
- اسم المستخدم: `ROFA`
- كلمة المرور: `QQ1122qq11223`

## تشغيل Render
Build Command:
```bash
pip install -r requirements.txt && python manage.py migrate && python manage.py bootstrap_admin && python manage.py collectstatic --noinput
```

Start Command:
```bash
gunicorn rufa_gold.wsgi:application
```

## متغيرات مهمة
- `DATABASE_URL`: رابط PostgreSQL للحفظ السحابي الدائم.
- `DJANGO_SECRET_KEY`: مفتاح سري.
- `DJANGO_DEBUG=False`
- `CLOUDINARY_URL`: اختياري لحفظ الصور والملفات سحابيًا.

## الحفظ
كل عملية إضافة أو تعديل تحفظ مباشرة في قاعدة البيانات. استخدم PostgreSQL في الإنتاج، ولا تعتمد على SQLite إلا للتجربة المحلية.
