from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from users.decorators import allowed_users
from django.db.models import Sum
from django.db.models import Q

from .forms import *
from .models import *
from .filters import *

#IOWA Test orders

@login_required(login_url='login')
@allowed_users(allowed_roles=['principal', 'registrar', 'staff', 'test_ordering'])
def test_order_dashboard(request, schoolID):
    school = School.objects.get(id=schoolID)
    school_year = school.current_school_year

    test_orders = TestOrder.objects.filter(school=school)

    context = dict(school=school, test_orders=test_orders)

    return render(request, 'test_order_dashboard.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['principal', 'registrar','staff', 'test_ordering'])
def test_order(request, schoolID, orderID=None):
    school = get_object_or_404(School, id=schoolID)
    order = get_object_or_404(TestOrder, id=orderID) if orderID else None

    booklet_formset = ReusableTestBookletFormSet(instance=order or TestOrder())
    answer_sheet_formset = AnswerSheetFormSet(instance=order or TestOrder())
    direction_formset = DirectionBookletFormSet(instance=order or TestOrder())

    if request.method == 'POST':

        order_form = TestOrderForm(request.POST, instance=order)

        if order_form.is_valid():
            order = order_form.save(commit=False)
            order.school = school

            booklet_formset = ReusableTestBookletFormSet(request.POST, instance=order)
            answer_sheet_formset = AnswerSheetFormSet(request.POST, instance=order)
            direction_formset = DirectionBookletFormSet(request.POST, instance=order)

            if booklet_formset.is_valid() and answer_sheet_formset.is_valid() and direction_formset.is_valid():
                order.save()
                booklet_formset.save()
                answer_sheet_formset.save()
                direction_formset.save()


                if 'submit' in request.POST:
                    order.submitted=True
                    order.save()

                return redirect('test_order_dashboard',school.id)
    else:
        order_form = TestOrderForm(instance=order)
        booklet_formset = ReusableTestBookletFormSet(instance=order or TestOrder())
        answer_sheet_formset = AnswerSheetFormSet(instance=order or TestOrder())
        direction_formset = DirectionBookletFormSet(instance=order or TestOrder())

    test_material_booklet = TestMaterialType.objects.get(name=1)
    answer_sheet = TestMaterialType.objects.get(name=2)
    admin_directions_booklet = TestMaterialType.objects.get(name=3)
    test_scoring = TestMaterialType.objects.get(name=4)

    latest_update = max(
        test_material_booklet.update,
        answer_sheet.update,
        admin_directions_booklet.update,
        test_scoring.update
    )

    context = dict(school=school.name, order_form=order_form,
                   booklet_formset=booklet_formset, answer_sheet_formset=answer_sheet_formset, direction_formset=direction_formset,
                   test_material_booklet=test_material_booklet, answer_sheet=answer_sheet, admin_directions_booklet=admin_directions_booklet,
                   test_scoring=test_scoring, latest_update=latest_update)

    return render(request, 'test_order.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['staff'])
def isei_test_order(request):

    test_orders = TestOrder.objects.exclude(school__abbreviation='SS').filter(finalized=False)
    f = TestOrderFilter(request.GET, queryset=test_orders)


    test_booklets_counts = ReusableTestBookletOrdered.objects.filter(order__in=test_orders).values('level').annotate(
        total=Sum('count')).order_by('level')
    answer_sheets_counts = AnswerSheetOrdered.objects.filter(order__in=test_orders).values('level').annotate(
        total=Sum('count')).order_by('level')
    direction_booklets_counts = DirectionBookletOrdered.objects.filter(order__in=test_orders).values('level').annotate(
        total=Sum('count')).order_by('level')

    schools=School.objects.filter(test=False, active=True)

    context=dict(test_orders=test_orders,  filter=f, schools=schools,
                 test_booklets_counts=test_booklets_counts, answer_sheets_counts=answer_sheets_counts,direction_booklets_counts=direction_booklets_counts)
    return render(request, 'isei_test_order.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['staff'])
def finalize_order(request, order_id):
    order = get_object_or_404(TestOrder, id=order_id)
    order.finalized = True
    order.save()
    return redirect('isei_test_order')


#resources page
@login_required(login_url='login')
def resources(request, school_id=None):

    accreditation_resources= Resource.objects.filter(type__name='Accreditation')
    document_resources= Resource.objects.filter(type__name='Document')
    teacher_evaluation_resources = Resource.objects.filter(type__name='Teacher Evaluation')
    admin_evaluation_resources = Resource.objects.filter(type__name='Admin Evaluation')
    safety_resources = Resource.objects.filter(type__name='Safety & Maintenance')
    meeting_materials =Resource.objects.filter(type__name='Meeting Materials')
    registrations =Resource.objects.filter(type__name='Registration').order_by('name')
    services = Resource.objects.filter(type__name='Service').order_by('name')
    misc = Resource.objects.filter(type__name='Misc')

    professional_growth_plan=Resource.objects.filter(name='Professional Growth Plan Template').first()




    context=dict(teacher_evaluation_resources = teacher_evaluation_resources,
                 admin_evaluation_resources = admin_evaluation_resources,
                 accreditation_resources = accreditation_resources,
                 document_resources = document_resources,
                 safety_resources = safety_resources,
                 meeting_materials=meeting_materials,
                 registrations=registrations,
                 services=services,
                 school_id=school_id,
                 misc = misc,
                 professional_growth_plan=professional_growth_plan)

    return render(request, 'resources.html', context)


def calendar(request):
    return render(request, 'calendar.html')