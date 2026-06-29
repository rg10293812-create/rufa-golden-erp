{% extends 'base.html' %}
{% block page_title %}الإدارة المالية{% endblock %}
{% block content %}
<div class="grid stats"><div class="cardx"><span>إجمالي الإيرادات</span><strong>{{ income|floatformat:0 }}</strong></div><div class="cardx"><span>إجمالي المصروفات</span><strong>{{ expenses|floatformat:0 }}</strong></div><div class="cardx"><span>رصيد الشركة</span><strong>{{ balance|floatformat:0 }}</strong></div></div>
<div class="section-card mt-4"><div class="section-head"><h3>سجل العمليات المالية</h3><a class="btn btn-gold" href="{% url 'finance_add' %}">إضافة عملية</a></div><div class="table-responsive"><table class="table table-darkish"><thead><tr><th>النوع</th><th>الاسم</th><th>المبلغ</th><th>التاريخ</th><th>ملاحظات</th></tr></thead><tbody>{% for t in transactions %}<tr><td>{{ t.get_transaction_type_display }}</td><td>{{ t.title }}</td><td>{{ t.amount|floatformat:0 }}</td><td>{{ t.date }}</td><td>{{ t.notes }}</td></tr>{% endfor %}</tbody></table></div></div>
{% endblock %}
