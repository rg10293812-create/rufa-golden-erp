from decimal import Decimal
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UserProfile(TimeStampedModel):
    EXECUTIVE = 'executive'
    MARKETER = 'marketer'
    FIELD = 'field'
    ROLE_CHOICES = [
        (EXECUTIVE, 'مدير تنفيذي'),
        (MARKETER, 'مسوق عقاري'),
        (FIELD, 'مسؤول ميداني'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=MARKETER)
    phone = models.CharField(max_length=40, blank=True)
    can_delete_properties = models.BooleanField(default=False)
    can_manage_permissions = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.get_full_name() or self.user.username} - {self.get_role_display()}'


class Property(TimeStampedModel):
    AVAILABLE = 'available'
    RESERVED = 'reserved'
    SOLD = 'sold'
    STATUS_CHOICES = [
        (AVAILABLE, 'متاح'),
        (RESERVED, 'محجوز'),
        (SOLD, 'مباع'),
    ]
    code = models.CharField(max_length=20, unique=True, blank=True)
    title = models.CharField('اسم المشروع', max_length=255)
    property_type = models.CharField('نوع العقار', max_length=100, blank=True)
    district = models.CharField('الحي', max_length=120, blank=True)
    price = models.DecimalField('السعر', max_digits=14, decimal_places=2, default=0)
    area = models.CharField('المساحة', max_length=80, blank=True)
    specifications = models.TextField('المواصفات', blank=True)
    notes = models.TextField('ملاحظات', blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=AVAILABLE)
    owner_name = models.CharField('اسم المالك', max_length=160, blank=True)
    owner_phone = models.CharField('جوال المالك', max_length=50, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='properties')

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.code:
            last = Property.objects.order_by('-id').first()
            next_id = 1 if not last else last.id + 1
            self.code = f'RG-{next_id:06d}'
        super().save(*args, **kwargs)

    @property
    def cover_image(self):
        cover = self.images.filter(is_cover=True).first() or self.images.first()
        return cover.image.url if cover and cover.image else ''

    def __str__(self):
        return f'{self.code} - {self.title}'


class PropertyImage(TimeStampedModel):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='properties/%Y/%m/')
    is_cover = models.BooleanField(default=False)


class ExternalMarketer(TimeStampedModel):
    name = models.CharField(max_length=160)
    phone = models.CharField(max_length=50, blank=True)
    company = models.CharField(max_length=160, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Deal(TimeStampedModel):
    OPEN = 'open'
    CLOSED = 'closed'
    STATUS_CHOICES = [(OPEN, 'مفتوحة'), (CLOSED, 'مكتملة')]
    code = models.CharField(max_length=30, unique=True, blank=True)
    property = models.ForeignKey(Property, on_delete=models.SET_NULL, null=True, blank=True, related_name='deals')
    title = models.CharField(max_length=255)
    commission_amount = models.DecimalField('قيمة السعي', max_digits=14, decimal_places=2, default=0)
    company_percentage = models.DecimalField('نسبة الشركة', max_digits=5, decimal_places=2, default=Decimal('0'))
    external_marketer = models.ForeignKey(ExternalMarketer, on_delete=models.SET_NULL, null=True, blank=True, related_name='deals')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=OPEN)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.code:
            year = timezone.now().year
            count = Deal.objects.filter(created_at__year=year).count() + 1
            self.code = f'SALE-{year}-{count:04d}'
        super().save(*args, **kwargs)

    @property
    def company_share(self):
        return (self.commission_amount * self.company_percentage / Decimal('100')).quantize(Decimal('0.01'))

    def __str__(self):
        return self.code


class CommissionShare(TimeStampedModel):
    deal = models.ForeignKey(Deal, on_delete=models.CASCADE, related_name='shares')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='commission_shares')
    percentage = models.DecimalField(max_digits=5, decimal_places=2)

    @property
    def amount(self):
        return (self.deal.commission_amount * self.percentage / Decimal('100')).quantize(Decimal('0.01'))


class FinancialTransaction(TimeStampedModel):
    INCOME = 'income'
    EXPENSE = 'expense'
    TYPE_CHOICES = [(INCOME, 'إيراد'), (EXPENSE, 'مصروف')]
    SALARY = 'salary'
    ADS = 'ads'
    PHOTO = 'photo'
    OPERATIONS = 'operations'
    FUEL = 'fuel'
    OTHER = 'other'
    CATEGORY_CHOICES = [
        (SALARY, 'رواتب'), (ADS, 'إعلانات'), (PHOTO, 'تصوير'),
        (OPERATIONS, 'تشغيل'), (FUEL, 'وقود'), (OTHER, 'أخرى'),
    ]
    transaction_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    title = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, blank=True)
    date = models.DateField(default=timezone.now)
    notes = models.TextField(blank=True)
    related_deal = models.ForeignKey(Deal, on_delete=models.SET_NULL, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-date', '-created_at']


class Task(TimeStampedModel):
    OPEN = 'open'
    DONE = 'done'
    ARCHIVED = 'archived'
    STATUS_CHOICES = [(OPEN, 'مفتوحة'), (DONE, 'تم التنفيذ'), (ARCHIVED, 'مؤرشفة')]
    code = models.CharField(max_length=30, unique=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    related_property = models.ForeignKey(Property, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=OPEN)
    result_notes = models.TextField(blank=True)
    attachment = models.FileField(upload_to='tasks/%Y/%m/', blank=True, null=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_tasks')

    def save(self, *args, **kwargs):
        if not self.code:
            count = Task.objects.count() + 1
            self.code = f'TASK-{count:05d}'
        super().save(*args, **kwargs)


class Document(TimeStampedModel):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='documents/%Y/%m/')
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)


class AuditLog(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=255)
    details = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
