{% extends 'base.html' %}
{% block page_title %}مشاركة السعي{% endblock %}
{% block content %}
<div class="section-card">
  <h3>{{ deal.title }}</h3><p class="muted">إجمالي السعي: <b class="gold">{{ deal.commission_amount|floatformat:0 }} ريال</b></p>
  <form method="post" id="share-form">{% csrf_token %}
    <label>نسبة الشركة %</label><input class="form-control" name="company_percentage" type="number" step="0.01" value="{{ deal.company_percentage }}">
    <hr><div id="shares"></div><button type="button" class="btn btn-outline-gold" onclick="addShare()">+ إضافة موظف مشارك</button>
    <button class="btn btn-gold mt-3 d-block">حفظ التوزيع</button>
  </form>
  <hr><h4>التوزيع الحالي</h4><ul>{% for s in deal.shares.all %}<li>{{ s.user.first_name|default:s.user.username }} - {{ s.percentage }}% = {{ s.amount|floatformat:0 }} ريال</li>{% empty %}<li class="muted">لا يوجد مشاركون حتى الآن.</li>{% endfor %}</ul>
  <p>نصيب الشركة: <b>{{ deal.company_share|floatformat:0 }} ريال</b></p>
</div>
<script>
const users = [{% for u in users %}{id:'{{u.id}}', name:'{{u.first_name|default:u.username}}'},{% endfor %}];
function addShare(){const wrap=document.getElementById('shares');const row=document.createElement('div');row.className='share-row';let opts=users.map(u=>`<option value="${u.id}">${u.name}</option>`).join('');row.innerHTML=`<select class="form-select" name="user">${opts}</select><input class="form-control" name="percentage" type="number" step="0.01" placeholder="النسبة %"><button class="btn btn-danger" type="button" onclick="this.parentElement.remove()">حذف</button>`;wrap.appendChild(row)}
</script>
{% endblock %}
