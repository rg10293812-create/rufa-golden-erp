from django.contrib import admin
from .models import AuditLog, CommissionShare, Deal, Document, ExternalMarketer, FinancialTransaction, Property, PropertyImage, Task, UserProfile

admin.site.register(UserProfile)
admin.site.register(Property)
admin.site.register(PropertyImage)
admin.site.register(Deal)
admin.site.register(CommissionShare)
admin.site.register(FinancialTransaction)
admin.site.register(Task)
admin.site.register(ExternalMarketer)
admin.site.register(Document)
admin.site.register(AuditLog)
