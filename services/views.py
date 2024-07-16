from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from .forms import *
from .models import *
from .functions import *
from django.db import transaction


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
                # Save the forms only if count > 0
                for form in booklet_formset:
                    count = form.cleaned_data.get('count', 0)
                    if count is not None and int(count) > 0:
                        form.save()

                for form in answer_sheet_formset:
                    count = form.cleaned_data.get('count', 0)
                    if count is not None and int(count) > 0:
                        form.save()

                for form in direction_formset:
                    count = form.cleaned_data.get('count', 0)
                    if count is not None and int(count) > 0:
                        form.save()

                if 'submit' in request.POST:
                    order.submitted=True
                    order.save()

                return redirect('school_dashboard',school.id)
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
