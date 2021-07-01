from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from users.decorators import unauthenticated_user, allowed_users
from .filters import *
from .forms import *
from users.utils import is_in_group
from users.models import *
from .models import *
from django.db.models import Q
from django.contrib import messages
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse
from django.forms import inlineformset_factory




#principal's approval of teacher activities
@login_required(login_url='login')
@allowed_users(allowed_roles=['principal'])
def principal_pda_approval(request, recID=None):
    principal = request.user.teacher
    teachers = Teacher.objects.filter(school = principal.school, active= True)
    pda_record_notreviewed = PDARecord.objects.filter(teacher__school=principal.school, date_submitted__isnull=False, principal_reviewed = 'n')
    pda_record_approved = PDARecord.objects.filter(teacher__school=principal.school, date_submitted__isnull=False, principal_reviewed = 'a')
    pda_record_denied = PDARecord.objects.filter(teacher__school=principal.school, date_submitted__isnull=True, principal_reviewed = 'd')

    if request.method == 'POST':
        if request.POST.get('approved'):
            pda_record = PDARecord.objects.filter(id=recID).update(principal_reviewed='a')
            PDAInstance.objects.filter(pda_record=pda_record).update(principal_signed=True)

    if request.method == 'POST':
        if request.POST.get('denied'):
            pda_record = PDARecord.objects.filter(id=recID).update(principal_reviewed='d', date_submitted = None, principal_comment = request.POST.get('principal_comment'))
            #PDAInstance.objects.filter(pda_record=pda_record).update(principal_reviewed='d')
            #PDAInstance.objects.filter(pda_record=pda_record).update(date_submitted = None)

    context = dict(teachers=teachers, pda_record_notreviewed=pda_record_notreviewed, pda_record_approved=pda_record_approved, pda_record_denied=pda_record_denied)
    return render(request, 'teachercert/principal_pda_approval.html', context)



#principal's approval of teacher activities
@login_required(login_url='login')
@allowed_users(allowed_roles=['staff'])
def isei_pda_approval(request, recID=None, instID=None):
    teachers = Teacher.objects.filter(active = True)
    pda_record_notreviewed = PDARecord.objects.filter(principal_reviewed = 'a', isei_reviewed='n')
    pda_record_approved = PDARecord.objects.filter( isei_reviewed = 'a')
    pda_record_denied = PDARecord.objects.filter( isei_reviewed = 'd')

    if request.method == 'POST':
        if request.POST.get('approveinst'):
           PDAInstance.objects.filter(id=instID).update(isei_reviewed='a', approved_ceu=request.POST.get('approved_ceu'))

    if request.method == 'POST':
        if request.POST.get('denyinst'):
           PDAInstance.objects.filter(id=instID).update(isei_reviewed='d', isei_comment=request.POST.get('isei_comment'),
                                                        princpial_reviewed = 'n', date_submitted = None)

    if request.method == 'POST':
        if request.POST.get('approved'):
            PDARecord.objects.filter(id=recID).update(isei_reviewed='a')

    if request.method == 'POST':
        if request.POST.get('denied'):
            pda_record = PDARecord.objects.filter(id=recID).update(isei_reviewed='d', date_submitted = None, principal_reviewed ='n', isei_comment = request.POST.get('isei_comment'))
            PDAInstance.objects.filter(pda_record=pda_record).update(principal_reviewed='n')
            PDAInstance.objects.filter(pda_record=pda_record).update(date_submitted = None)

    context = dict(teachers=teachers, pda_record_notreviewed=pda_record_notreviewed, pda_record_approved=pda_record_approved, pda_record_denied=pda_record_denied,)
    return render(request, 'teachercert/isei_pda_approval.html', context)


# teacher activities for user with id=pk ... some parts not finished
@login_required(login_url='login')
@allowed_users(allowed_roles=['teacher', 'admin'])
def myPDAdashboard(request, pk):
    teacher = Teacher.objects.get(user=User.objects.get(id=pk))
    pda_record = PDARecord.objects.filter(teacher=teacher )
    pda_instance = PDAInstance.objects.filter(pda_record__in=pda_record)

    active_record = pda_record.filter(Q(principal_reviewed='n'), Q(isei_reviewed = 'n'))
    denied_record = pda_record.filter(Q(principal_reviewed='d')| Q(isei_reviewed = 'd'))
    submitted_record = pda_record.filter(principal_reviewed='a')
    approved_record = pda_record.filter(isei_reviewed = 'a')

    instance_filter = PDAInstanceFilter(request.GET, queryset=pda_instance)
    pda_instance = instance_filter.qs

    active_instance = pda_instance.filter(pda_record__in= active_record)
    submitted_instance = pda_instance.filter(pda_record__in=submitted_record)
    denied_instance = pda_instance.filter(pda_record__in=denied_record)

    count = active_instance.count()+submitted_instance.count()

    no_record_school_years = SchoolYear.objects.exclude(pdarecord__in=pda_record)


    if is_in_group(request.user, 'teacher'):
        user_not_teacher = False
    else:
        user_not_teacher = True
    context = dict(teacher=teacher,user_not_teacher=user_not_teacher, instance_filter=instance_filter, count=count,
                   no_record_school_years=no_record_school_years, pda_instance=pda_instance,
                   active_record=active_record, submitted_record=submitted_record, denied_record =denied_record,
                   active_instance = active_instance, submitted_instance = submitted_instance, denied_instance = denied_instance)
    return render(request, 'teachercert/myPDAdashboard.html', context)
# todo create layout in myPDAdashboard template for it to look nicer
# todo adjust template so that it would allow for the choosing of a different teacher if user_not_teacher

# create record for user and school year
@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'teacher'])
def createrecord(request, pk, sy):

    pda_record = PDARecord()
    pda_record.teacher = Teacher.objects.get(user__id=pk)
    pda_record.school_year = SchoolYear.objects.get(id=sy)

    pda_record.save()

    return redirect('create_pda', recId =pda_record.id)


# create PDA instance + allows for record submission (for record with matching pk)
@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'teacher'])
def createPDA(request, recId):

    pda_record = PDARecord.objects.get(id=recId)

    pda_instance = PDAInstance.objects.filter(pda_record=pda_record) #list of already entered instances
    instanceformset = PDAInstanceFormSet(queryset=PDAInstance.objects.none(), instance=pda_record) # entering new activity
    record_form = PDARecordForm(instance = pda_record) #form for editing current record (summary and submission)
    #upload_form = DocumentForm() #uploading documentation
    #helper = PDAInstanceFormSetHelper()

    if request.method == 'POST':
        if request.POST.get('add_activity'): #add activity and stay on page
            instanceformset = PDAInstanceFormSet(request.POST, request.FILES or None, instance=pda_record)
            if instanceformset.is_valid():
                instanceformset.save()
                instanceformset = PDAInstanceFormSet(queryset=PDAInstance.objects.none(), instance=pda_record)


        if request.POST.get('submit_record'): #update summary, stay on page, submit record - go to PDAdashboard
            record_form = PDARecordForm(request.POST, instance=pda_record)
            if record_form.is_valid():
                pda_record = record_form.save()
                if pda_record.date_submitted:
                    pda_record.principal_reviewed = 'n'
                    pda_record.save()
                    pda_instance = PDAInstance.objects.filter(pda_record=pda_record)
                    pda_instance.update(submitted = True)

                if is_in_group(request.user, 'teacher'):
                    if request.POST.get('submit_record'):
                        return redirect('myPDAdashboard', pk=pda_record.teacher.user.id)

        if request.POST.get('update_summary'):  # update summary, stay on page, submit record - go to PDAdashboard
            record_form = PDARecordForm(request.POST, instance=pda_record)
            if record_form.is_valid():
                pda_record = record_form.save()

    if is_in_group(request.user, 'teacher'):
        user_not_teacher = False
    else:
        user_not_teacher = True

    context = dict(user_not_teacher=user_not_teacher,
                   pda_instance=pda_instance,
                   #helper= helper,
                   pda_record=pda_record,
                   record_form=record_form, instanceformset=instanceformset)
    return render(request, "teachercert/create_pda.html", context)



# update PDAinstance (by id)
@login_required(login_url='login')
def updatePDAinstance(request, pk):
    pdainstance = PDAInstance.objects.get(id=pk)
    form = PDAInstanceForm(instance=pdainstance)

    if request.method == 'POST':
        form = PDAInstanceForm(request.POST, request.FILES or None, instance=pdainstance)
        if form.is_valid():
            form.save()
            if is_in_group(request.user, 'teacher'):        # teacher landing page
                return redirect('myPDAdashboard', pk=pdainstance.pda_record.teacher.user.id)

    context = {'form': form}
    return render(request, "teachercert/update_pdainstance.html", context)


# delete PDAinstance (by id)
@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'teacher'])
def deletePDAinstance(request, pk):
    pdainstance = PDAInstance.objects.get(id=pk)

    if request.method == "POST":
        pdainstance.delete()
        if is_in_group(request.user, 'teacher'):  # teacher landing page
            return redirect('myPDAdashboard', pk=pdainstance.pda_record.teacher.user.id)

    context = {'item': pdainstance}
    return render(request, 'teachercert/delete_pdainstance.html', context)



# all teachers (for staff)
@login_required(login_url='login')
@allowed_users(allowed_roles=['staff'])
def teachers_NOTUSED(request):
    teachers = Teacher.objects.all()
    total_teachers = teachers.count()

    my_filter = TeacherFilter(request.GET, queryset=teachers)
    teachers = my_filter.qs

    context = {'teachers': teachers, 'total_teachers': total_teachers, 'my_filter': my_filter}
    return render(request, 'teachercert/unused_teachers.html', context)


