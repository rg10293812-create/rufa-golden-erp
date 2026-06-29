from decimal import Decimal, InvalidOperation
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import DealForm, ExternalMarketerForm, FinancialTransactionForm, PropertyForm, TaskCompleteForm, TaskForm, UserCreateForm
from .models import AuditLog, CommissionShare, Deal, ExternalMarketer, FinancialTransaction, Property, PropertyImage, Task, UserProfile
from .permissions import is_executive, role_required


def audit(user, action, details=''):
    AuditLog.objects.create(user=user if user.is_authenticated else None, action=action, details=details)


@login_required
def dashboard(request):
    income = FinancialTransaction.objects.filter(transaction_type='income').aggregate(s=Sum('amount'))['s'] or Decimal('0')
    expenses = FinancialTransaction.objects.filter(transaction_type='expense').aggregate(s=Sum('amount'))['s'] or Decimal('0')
    commission_total = Deal.objects.aggregate(s=Sum('commission_amount'))['s'] or Decimal('0')
    context = {
        'properties_count': Property.objects.count(),
        'sold_count': Property.objects.filter(status='sold').count(),
        'open_tasks': visible_tasks(request.user).filter(status='open').count(),
        'commission_total': commission_total,
        'company_balance': income - expenses,
        'expenses': expenses,
        'latest_properties': visible_properties(request.user)[:6],
        'latest_logs': AuditLog.objects.select_related('user')[:10] if is_executive(request.user) else [],
    }
    return render(request, 'core/dashboard.html', context)


def visible_properties(user):
    if is_executive(user):
        return Property.objects.select_related('created_by').all()
    # المسوق يرى عقاراته، والمسؤول الميداني يرى كل العقارات للبحث والمتابعة
    profile = getattr(user, 'profile', None)
    if profile and profile.role == 'field':
        return Property.objects.select_related('created_by').all()
    return Property.objects.select_related('created_by').filter(created_by=user)


def visible_tasks(user):
    if is_executive(user):
        return Task.objects.select_related('assigned_to', 'related_property').all()
    return Task.objects.select_related('assigned_to', 'related_property').filter(assigned_to=user)


@login_required
def property_list(request):
    q = request.GET.get('q', '').strip()
    properties = visible_properties(request.user)
    if q:
        properties = properties.filter(Q(title__icontains=q) | Q(district__icontains=q) | Q(property_type__icontains=q) | Q(price__icontains=q) | Q(code__icontains=q))
    return render(request, 'core/property_list.html', {'properties': properties, 'q': q})


@login_required
def property_detail(request, pk):
    prop = get_object_or_404(visible_properties(request.user), pk=pk)
    return render(request, 'core/property_detail.html', {'property': prop, 'is_executive': is_executive(request.user)})


@login_required
def property_add(request):
    if request.method == 'POST':
        form = PropertyForm(request.POST)
        images = request.FILES.getlist('images')
        if form.is_valid():
            prop = form.save(commit=False)
            prop.created_by = request.user
            prop.save()
            for i, img in enumerate(images):
                PropertyImage.objects.create(property=prop, image=img, is_cover=(i == 0))
            audit(request.user, 'إضافة عقار', prop.title)
            messages.success(request, 'تم حفظ العقار تلقائيًا.')
            return redirect('property_detail', pk=prop.pk)
    else:
        form = PropertyForm()
    return render(request, 'core/property_form.html', {'form': form, 'title': 'إضافة عقار'})


@login_required
def property_edit(request, pk):
    prop = get_object_or_404(visible_properties(request.user), pk=pk)
    if not is_executive(request.user) and prop.created_by != request.user:
        messages.error(request, 'لا تستطيع تعديل هذا العقار.')
        return redirect('property_list')
    if request.method == 'POST':
        form = PropertyForm(request.POST, instance=prop)
        images = request.FILES.getlist('images')
        if form.is_valid():
            prop = form.save()
            for img in images:
                PropertyImage.objects.create(property=prop, image=img)
            audit(request.user, 'تعديل عقار', prop.title)
            messages.success(request, 'تم الحفظ تلقائيًا.')
            return redirect('property_detail', pk=prop.pk)
    else:
        form = PropertyForm(instance=prop)
    return render(request, 'core/property_form.html', {'form': form, 'title': 'تعديل عقار'})


@login_required
@role_required('executive')
def property_delete(request, pk):
    prop = get_object_or_404(Property, pk=pk)
    if request.method == 'POST':
        title = prop.title
        prop.delete()
        audit(request.user, 'حذف عقار', title)
        messages.success(request, 'تم حذف العقار.')
        return redirect('property_list')
    return render(request, 'core/confirm_delete.html', {'object_name': prop.title})


@login_required
@role_required('executive')
def deal_list(request):
    deals = Deal.objects.select_related('property', 'external_marketer').all()
    return render(request, 'core/deal_list.html', {'deals': deals})


@login_required
@role_required('executive')
def deal_add(request):
    if request.method == 'POST':
        form = DealForm(request.POST)
        if form.is_valid():
            deal = form.save(commit=False)
            deal.created_by = request.user
            deal.save()
            if deal.property and deal.status == 'closed':
                deal.property.status = 'sold'
                deal.property.save(update_fields=['status', 'updated_at'])
            FinancialTransaction.objects.create(
                transaction_type='income', title=f'سعي {deal.title}', amount=deal.commission_amount,
                notes=f'تم تسجيله من الصفقة {deal.code}', related_deal=deal, created_by=request.user
            )
            audit(request.user, 'إضافة صفقة وسعي', f'{deal.code} - {deal.commission_amount}')
            messages.success(request, 'تم تسجيل السعي وإضافته للإدارة المالية.')
            return redirect('deal_share', pk=deal.pk)
    else:
        form = DealForm()
    return render(request, 'core/deal_form.html', {'form': form, 'title': 'إضافة صفقة / تسجيل سعي'})


@login_required
@role_required('executive')
def deal_share(request, pk):
    deal = get_object_or_404(Deal, pk=pk)
    users = User.objects.filter(is_active=True).exclude(profile__role='executive').order_by('first_name', 'username')
    if request.method == 'POST':
        deal.company_percentage = Decimal(request.POST.get('company_percentage') or '0')
        deal.save(update_fields=['company_percentage', 'updated_at'])
        deal.shares.all().delete()
        user_ids = request.POST.getlist('user')
        percentages = request.POST.getlist('percentage')
        for user_id, pct in zip(user_ids, percentages):
            if user_id and pct:
                try:
                    percentage = Decimal(pct)
                    if percentage > 0:
                        CommissionShare.objects.create(deal=deal, user_id=user_id, percentage=percentage)
                except (InvalidOperation, ValueError):
                    continue
        audit(request.user, 'توزيع سعي', deal.code)
        messages.success(request, 'تم حفظ مشاركة السعي تلقائيًا.')
        return redirect('deal_share', pk=deal.pk)
    return render(request, 'core/deal_share.html', {'deal': deal, 'users': users})


@login_required
@role_required('executive')
def finance(request):
    transactions = FinancialTransaction.objects.select_related('created_by').all()[:100]
    income = FinancialTransaction.objects.filter(transaction_type='income').aggregate(s=Sum('amount'))['s'] or Decimal('0')
    expenses = FinancialTransaction.objects.filter(transaction_type='expense').aggregate(s=Sum('amount'))['s'] or Decimal('0')
    return render(request, 'core/finance.html', {'transactions': transactions, 'income': income, 'expenses': expenses, 'balance': income - expenses})


@login_required
@role_required('executive')
def finance_add(request):
    if request.method == 'POST':
        form = FinancialTransactionForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.created_by = request.user
            item.save()
            audit(request.user, 'إضافة عملية مالية', f'{item.title} - {item.amount}')
            messages.success(request, 'تم حفظ العملية المالية.')
            return redirect('finance')
    else:
        form = FinancialTransactionForm()
    return render(request, 'core/simple_form.html', {'form': form, 'title': 'إضافة عملية مالية'})


@login_required
def task_list(request):
    tasks = visible_tasks(request.user)
    return render(request, 'core/task_list.html', {'tasks': tasks, 'is_executive': is_executive(request.user)})


@login_required
@role_required('executive')
def task_add(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.created_by = request.user
            task.save()
            audit(request.user, 'إنشاء مهمة', task.title)
            messages.success(request, 'تم إرسال المهمة.')
            return redirect('task_list')
    else:
        form = TaskForm()
    return render(request, 'core/simple_form.html', {'form': form, 'title': 'إنشاء مهمة'})


@login_required
def task_complete(request, pk):
    task = get_object_or_404(visible_tasks(request.user), pk=pk)
    if request.method == 'POST':
        form = TaskCompleteForm(request.POST, request.FILES, instance=task)
        if form.is_valid():
            task = form.save(commit=False)
            task.status = 'done'
            task.completed_at = timezone.now()
            task.save()
            audit(request.user, 'تنفيذ مهمة', task.title)
            messages.success(request, 'تم تنفيذ المهمة.')
            return redirect('task_list')
    else:
        form = TaskCompleteForm(instance=task)
    return render(request, 'core/simple_form.html', {'form': form, 'title': 'تنفيذ مهمة'})


@login_required
@role_required('executive')
def task_archive(request, pk):
    task = get_object_or_404(Task, pk=pk)
    task.status = 'archived'
    task.save(update_fields=['status', 'updated_at'])
    messages.success(request, 'تمت أرشفة المهمة.')
    return redirect('task_list')


@login_required
@role_required('executive')
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    task.delete()
    messages.success(request, 'تم حذف المهمة.')
    return redirect('task_list')


@login_required
@role_required('executive')
def user_list(request):
    users = User.objects.select_related('profile').all().order_by('id')
    return render(request, 'core/user_list.html', {'users': users})


@login_required
@role_required('executive')
def user_add(request):
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            user.first_name = form.cleaned_data['full_name']
            user.save()
            UserProfile.objects.update_or_create(user=user, defaults={'role': form.cleaned_data['role'], 'phone': form.cleaned_data['phone']})
            audit(request.user, 'إضافة مستخدم', user.username)
            messages.success(request, 'تم إضافة المستخدم.')
            return redirect('user_list')
    else:
        form = UserCreateForm()
    return render(request, 'core/simple_form.html', {'form': form, 'title': 'إضافة مستخدم'})


@login_required
@role_required('executive')
def external_marketer_list(request):
    marketers = ExternalMarketer.objects.all()
    return render(request, 'core/external_marketer_list.html', {'marketers': marketers})


@login_required
@role_required('executive')
def external_marketer_add(request):
    if request.method == 'POST':
        form = ExternalMarketerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم إضافة المسوق الخارجي.')
            return redirect('external_marketer_list')
    else:
        form = ExternalMarketerForm()
    return render(request, 'core/simple_form.html', {'form': form, 'title': 'إضافة مسوق خارجي'})
