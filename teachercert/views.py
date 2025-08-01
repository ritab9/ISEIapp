from django.contrib.auth.decorators import login_required
from users.decorators import allowed_users
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from .filters import *
from .forms import *
from users.utils import is_in_group
from users.filters import SchoolFilter
from .models import *
from django.db.models import Q, F  # Q is for queries in filters, F is to update a field using an other field from the model
from django.db.models.functions import Now
from django.forms import modelformset_factory
from .myfunctions import *
from emailing.teacher_cert_functions import *

import datetime
from datetime import datetime, timedelta
from django.contrib import messages

from django.db import IntegrityError
from django.http import JsonResponse

from django.core.files.storage import default_storage


# PROFESSIONAL DEVELOPMENT ACTIVITY REPORT - CEUs

# just an info page about the CEU activities
def ceu_info(request):
    info = CEUType.objects.all()
    # first = CEUType.objects.first()
    # info = CEUType.objects.filter(~Q(id= first.id))
    list = [1, 2, 6, 7, 8, 9, 10]
    context = dict(info=info, list=list)
    return render(request, 'teachercert/ceu_info.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['staff'])
def isei_teachercert_dashboard(request):
    # all active teacher
    teachers = Teacher.objects.filter(Q(user__is_active=True), Q(user__groups__name__in=['teacher']))
    # ~Q(school__name__in={'ISEI', 'Sample School'}))

    # filter by school
    school_filter = SchoolFilter(request.GET, queryset=teachers)
    teachers = school_filter.qs

    # Teacher Certificates Section
    # number_of_teachers = teachers.count()
    # Last certificate for each active user
    tcertificates = TCertificate.objects.filter(archived=False, teacher__user__is_active=True).order_by('renewal_date', 'teacher__user__profile__school')

    # Valid certificates
    valid_tcertificates = tcertificates.filter(renewal_date__gte=date.today(), teacher__in=teachers)
    # certified teachers with unexpired certificates
    certified_teachers = teachers.filter(tcertificate__in=valid_tcertificates).distinct().order_by('school')
    number_of_certified_teachers = certified_teachers.count()

    # expired certificates and teachers with expired certificates
    expired_tcertificates = tcertificates.filter(renewal_date__lt=date.today(), teacher__in=teachers)
    expired_teachers = teachers.filter(tcertificate__in=expired_tcertificates)
    number_of_expired_teachers = expired_teachers.count()

    # not certified teachers
    non_certified_teachers = teachers.filter(~Q(tcertificate__in=tcertificates)).order_by("school")
    number_of_non_certified_teachers = non_certified_teachers.count()

    # if number_of_teachers >= 1:
    #    percent_certified = round(number_of_certified_teachers * 100 / number_of_teachers)
    # else:
    #    percent_certified = "There are no teachers registered for this school"

    today = date.today()
    in_six_months = today + timedelta(183)
    a_year_ago = today - timedelta(365)

    schools = School.objects.filter(active=True)
    cert_dict = {}
    for s in schools:
        s_teachers = teachers.filter(school=s)
        # certified teachers with unexpired certificates
        s_certified_teachers = s_teachers.filter(tcertificate__in=valid_tcertificates).distinct()
        s_number_of_teachers = s_teachers.count()
        s_number_of_certified_teachers = s_certified_teachers.count()
        # s_number_of_certified_academic_teachers = s_certified_teachers.filter(academic=True).count()
        # s_number_of_academic_teachers = s_teachers.filter(academic=True).count()
        if s_teachers.count() > 0:
            percent = round(s_number_of_certified_teachers * 100 / s_number_of_teachers)
            # percent= round(s_number_of_certified_academic_teachers * 100 / s_number_of_academic_teachers)
        else:
            percent = "-"

        #bc_complete = Teacher.objects.filter(user__is_active=True, user__profile__school__id=s.id, background_check=True)
        bc_missing = Teacher.objects.filter(user__is_active=True, user__profile__school__id=s.id, background_check=False).count()

        cert_dict[s] = {
            'teachers': s_number_of_teachers,
            'certified': s_number_of_certified_teachers,
            # 'academic': s_number_of_academic_teachers,
            # 'certified_academic':s_number_of_certified_academic_teachers,
            'percent': percent,
            'bc_missing': bc_missing,
        }

    context = dict(today=today, in_six_months=in_six_months, a_year_ago=a_year_ago,
                   # percent_certified=percent_certified,
                   valid_tcertificates=valid_tcertificates, number_of_certified_teachers=number_of_certified_teachers,
                   expired_tcertificates=expired_tcertificates, number_of_expired_teachers=number_of_expired_teachers,
                   non_certified_teachers=non_certified_teachers,
                   number_of_non_certified_teachers=number_of_non_certified_teachers,
                   # number_of_teachers=number_of_teachers,
                   school_filter=school_filter,
                   cert_dict=cert_dict,
                   )

    return render(request, 'teachercert/isei_teachercert_dashboard.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['principal','registrar', 'staff'])
def principalteachercert(request, schoolID):
    #principal = User.objects.get(id=userID).teacher

    teachers = Teacher.objects.filter(user__profile__school_id=schoolID, user__is_active=True, user__groups__name__in=['teacher'])

    # Teacher Certificates Section
    number_of_teachers = teachers.count()
    # number_of_academic_teachers = teachers.filter(academic=True).count()
    tcertificates = TCertificate.objects.filter(teacher__in=teachers, archived=False)

    # Valid certificates and certified teachers
    valid_tcertificates = tcertificates.filter(renewal_date__gte=date.today(), teacher__in=teachers).order_by('teacher')
    certified_teachers = teachers.filter(tcertificate__in=valid_tcertificates).distinct()
    number_of_certified_teachers = certified_teachers.count()
    # number_of_certified_academic_teachers = certified_teachers.filter(academic=True).count()

    # expired certificates and teachers with expired certificates
    expired_tcertificates = tcertificates.filter(renewal_date__lt=date.today(), teacher__in=teachers).order_by(
        'teacher')
    expired_teachers = teachers.filter(tcertificate__in=expired_tcertificates)
    number_of_expired_teachers = expired_teachers.count()

    # not certified teachers
    non_certified_teachers = teachers.filter(~Q(tcertificate__in=tcertificates))
    number_of_non_certified_teachers = non_certified_teachers.count()

    if number_of_teachers > 0:
        percent_certified = round(number_of_certified_teachers * 100 / number_of_teachers)
    else:
        percent_certified = 0

    today = date.today()
    in_six_months = today + timedelta(183)
    a_year_ago = today - timedelta(365)

    # Report Approval Section
    ceu_report = CEUReport.objects.filter(teacher__in=teachers)  # all the reports from this teacher's school
    ceu_report_notreviewed = ceu_report.filter(date_submitted__isnull=False, principal_reviewed='n')
    ceu_instance_notreviewed = CEUInstance.objects.filter(ceu_report__in=ceu_report, ceu_report__isei_reviewed='a',
                                                          isei_reviewed='d', date_resubmitted__isnull=False,
                                                          principal_reviewed='n')
    if ceu_report_notreviewed or ceu_instance_notreviewed:
        reports_to_review = True
    else:
        reports_to_review = False

    bc_done = complete_background_checks(schoolID)

    context = dict(today=today, in_six_months=in_six_months, a_year_ago=a_year_ago, percent_certified=percent_certified,
                   valid_tcertificates=valid_tcertificates, number_of_certified_teachers=number_of_certified_teachers,
                   expired_tcertificates=expired_tcertificates, number_of_expired_teachers=number_of_expired_teachers,
                   non_certified_teachers=non_certified_teachers,
                   number_of_non_certified_teachers=number_of_non_certified_teachers,
                   number_of_teachers=number_of_teachers, schoolid = schoolID,
                   # number_of_academic_teachers = number_of_academic_teachers, number_of_certified_academic_teachers = number_of_certified_academic_teachers,
                   reports_to_review=reports_to_review,
                   bc_done= bc_done)

    return render(request, 'teachercert/principal_teachercert.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['teacher', 'staff', 'principal', 'registrar'])
def teacherdashboard(request, userID):
    user = User.objects.get(id=userID)
    teacher = Teacher.objects.get(user=user)
    highest_degree = None
    tcertificate = None

    academic_classes = AcademicClass.objects.filter(teacher=teacher).order_by('-date_completed')

    if StandardChecklist.objects.filter(teacher=teacher):
        standard_checklist = StandardChecklist.objects.get(teacher=teacher)
    else:
        standard_checklist = None

    # current_certificates
    if never_certified(teacher):
        certification_status = None
        basic_met = None
        basic_not_met = None

        if TeacherCertificationApplication.objects.filter(teacher=teacher):
            tcert_application = TeacherCertificationApplication.objects.get(teacher=teacher)
        else:
            tcert_application = None

    else:
        tcertificate = current_certificates(teacher).first()

        basic = TeacherBasicRequirement.objects.filter(teacher=teacher)
        basic_met = basic.filter(met=True)
        basic_not_met = basic.filter(met=False)

        highest_degree = degree(teacher)
        # if CollegeAttended.objects.filter(teacher=teacher, level="d"):
        #     highest_degree = "Doctoral Degree"
        # elif CollegeAttended.objects.filter(teacher=teacher, level="m"):
        #     highest_degree = "Master's Degree"
        # elif CollegeAttended.objects.filter(teacher=teacher, level="b"):
        #     highest_degree = "Bachelor's Degree"
        # elif CollegeAttended.objects.filter(teacher=teacher, level="a"):
        #     highest_degree = "Associate Degree"
        # elif CollegeAttended.objects.filter(teacher=teacher, level="c"):
        #     highest_degree = "Certificate"
        # elif CollegeAttended.objects.filter(teacher=teacher, level="n"):
        #     highest_degree = "None"

        if certified(teacher):
            certification_status = "Valid Certification"
        else:
            certification_status = "Expired Certification"

        # if an application has been turned in after the latest Certificate was issued
        if TeacherCertificationApplication.objects.filter(teacher=teacher, date__gte=tcertificate.issue_date):
            tcert_application = TeacherCertificationApplication.objects.get(teacher=teacher)
        else:
            tcert_application = None

    today = get_today()
    # if tcert_application:
    #     if tcert_application.date > datetime.today() - timedelta(days=183):
    #         expired_application = True
    #     else:
    #         expired_application = False
    # else:
    #     expired_application = "N/A"

    context = dict(teacher=teacher, tcertificate=tcertificate, certification_status=certification_status,
                   today=today, basic_met=basic_met, basic_not_met=basic_not_met,
                   tcert_application=tcert_application, highest_degree=highest_degree,
                   checklist=standard_checklist,
                   academic_classes=academic_classes,
                  )
    return render(request, 'teachercert/teacher_dashboard.html', context)


# Teacher Views

# create report for user and school year if no report exists. It is called from myCEUDashboard - new activity addition
@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'staff', 'teacher'])
def createCEUreport(request, pk, sy):
    ceu_report = CEUReport()
    ceu_report.teacher = Teacher.objects.get(user__id=pk)
    ceu_report.school_year = SchoolYear.objects.get(id=sy)
    ceu_report.save()
    email_CEUReport_created(ceu_report.teacher, ceu_report.school_year.name)
    return redirect('create_ceu', recId=ceu_report.id)


# Unused - I think
# def add_instance(request, reportID):
#     ceu_instance = CEUInstance(ceu_report=CEUReport.objects.get(id=reportID))
#     form = CEUInstanceForm(instance=ceu_instance)
#     if request.method == 'POST':
#         form = CEUInstanceForm(request.POST, instance=ceu_instance)
#         if form.is_valid():
#             form.save()
#             return redirect('create_ceu', recId=reportID)
#     return render(request, 'teachercert/add_instance.html', {'form': form})
#

# Ajax
def load_CEUtypes(request):
    ceu_category_id = request.GET.get('ceu_category_id')
    ceu_types = CEUType.objects.filter(ceu_category_id=ceu_category_id).order_by('description')
    return render(request, 'teachercert/ceu_category_dropdown_list_options.html', {'ceu_types': ceu_types})


def load_evidence(request):
    ceu_type_id = request.GET.get('ceu_type_id')
    ceu_type = CEUType.objects.get(id=ceu_type_id)
    evidence = ceu_type.evidence
    value = ceu_type.ceu_value
    return render(request, 'teachercert/ajax_suggested_evidence.html', {'evidence': evidence, 'value': value})


# create CEU instance + allows for report submission (for report with matching pk)
@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'staff', 'teacher'])
def createCEU(request, recId):
    ceu_report = CEUReport.objects.get(id=recId)  # report
    ceu_instance = CEUInstance.objects.filter(ceu_report=ceu_report)  # list of already entered instances
    # instanceformset = CEUInstanceFormSet(queryset=CEUInstance.objects.none(), instance=ceu_report) # entering new activity

    new_instance = CEUInstance(ceu_report=ceu_report)
    instance_form = CEUInstanceForm(instance=new_instance)
    report_form = CEUReportForm(instance=ceu_report)  # form for editing current report (summary and submission)
    activity_entering_error=False

    if request.method == 'POST':
        if request.POST.get('add_activity'):  # add activity or update summary and stay on page
            instance_form = CEUInstanceForm(request.POST, request.FILES or None, instance=new_instance)
            if instance_form.is_valid():
                try:
                    instance_form.save()  # save activity
                    instance_form = CEUInstanceForm(instance=CEUInstance(ceu_report=ceu_report))  # allow for a new entry
                except IntegrityError:
                    messages.warning(request, "This activity is already entered")
                    activity_entering_error = True


        if request.POST.get('update_report'):  # update summary, stay on page
            report_form = CEUReportForm(request.POST, instance=ceu_report)
            if report_form.is_valid():
                ceu_report = report_form.save()
                messages.success(request, 'Summary was successfully updated!')


        if request.POST.get('submit_report'):  # submit report - go to CEUdashboard
            report_form = CEUReportForm(request.POST, instance=ceu_report)
            if report_form.is_valid():
                ceu_report = report_form.save()  # save report submission
                if ceu_report.date_submitted:  # if the date is entered the report is submitted to the principal for revision
                    ceu_report.principal_reviewed = 'n'  # set principal and ISEI revisions to "Not yet" just in case it is a resubmission
                    ceu_report.isei_reviewed = 'n'
                    ceu_report.save()
                    ceu_instance = CEUInstance.objects.filter(ceu_report=ceu_report)
                    ceu_instance.update(principal_reviewed='n',
                                        isei_reviewed='n')  # set all instances to not reviewed as well

                    ceu_report.last_submitted = ceu_report.date_submitted

                    principal_emails = get_principals_emails(ceu_report.teacher)
                    email_CEUReport_submitted(ceu_report.teacher, principal_emails, ceu_report.school_year.name)

                    return redirect('myCEUdashboard', pk=ceu_report.teacher.user.id)  # go back to CEUdashboard



    context = dict(ceu_instance=ceu_instance, ceu_report=ceu_report,
                   instance_form=instance_form, report_form=report_form,
                   activity_entering_error = activity_entering_error)

    return render(request, "teachercert/create_ceu.html", context)


# update CEUInstance (by id)
@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'staff', 'teacher'])
def updateCEUinstance(request, pk):
    ceu_instance = CEUInstance.objects.get(id=pk)
    form = CEUInstanceForm(instance=ceu_instance)

    # if the report has been accepted but the instance denied by ISEI, the instance is resubmitted alone
    resubmit = False
    if ((ceu_instance.isei_reviewed == 'd') and (ceu_instance.ceu_report.isei_reviewed == 'a')):
        resubmit = True

    if request.method == 'POST':
        if request.POST.get(
                'submit'):  # if it's an update within the report, it is saved and send back to report creation
            form = CEUInstanceForm(request.POST, request.FILES or None, instance=ceu_instance)
            if form.is_valid():
                form.save()
                return redirect('create_ceu', ceu_instance.ceu_report.id)


        if request.POST.get('resubmit'):  # if it is a resubmition
            form = CEUInstanceForm(request.POST, request.FILES or None, instance=ceu_instance)
            if form.is_valid():
                form.save()  # save
                # ToDo Should I set isei_reviewed='n' here???
                CEUInstance.objects.filter(id=pk).update(principal_reviewed='n', )  # principal reviewed set to no
                ceu_report = CEUReport.objects.get(ceu_instance=ceu_instance)
                principal_emails = get_principals_emails(ceu_report.teacher)
                email_CEUReport_submitted(ceu_report.teacher, principal_emails, ceu_report.school_year.name)

                return redirect('myCEUdashboard', pk=ceu_instance.ceu_report.teacher.user.id)

    context = dict(ceu_instance=ceu_instance, form=form,
                   resubmit=resubmit)  # if resubmit=True the activity has been denied by ISEI and the report it belongs to accepted
    return render(request, "teachercert/update_ceuinstance.html", context)


# delete CEUInstance (by id)
@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'staff', 'teacher'])
def deleteCEUinstance(request, pk):
    ceuInstance = CEUInstance.objects.get(id=pk)
    if request.method == "POST":
        ceuInstance.delete()
        # if is_in_group(request.user, 'teacher'):  # teacher landing page
        return redirect('create_ceu', ceuInstance.ceu_report.id)

    context = {'item': ceuInstance}
    return render(request, 'teachercert/delete_ceuinstance.html', context)


# teacher activities for user with id=pk ... some parts not finished
@login_required(login_url='login')
@allowed_users(allowed_roles=['teacher', 'staff', 'admin'])
def myCEUdashboard(request, pk):
    teacher = Teacher.objects.get(user=User.objects.get(id=pk))

    ceu_report = CEUReport.objects.filter(teacher=teacher)  # all reports of this teacher

    ceu_instance = CEUInstance.objects.filter(ceu_report__in=ceu_report)
    # all instances run through the filter (Taking this out)
    # instance_filter = CEUInstanceFilter(request.GET, queryset=ceu_instance)
    # ceu_instance = instance_filter.qs

    # instances from denied reports are not filtered
    principal_denied_report = ceu_report.filter(Q(principal_reviewed='d'))
    isei_denied_report = ceu_report.filter(Q(isei_reviewed='d'))

    # new school year if report not yet created
    new_school_year = SchoolYear.objects.filter(Q(active_year=True), ~Q(ceureport__in=ceu_report))
    # reports not reviewed by principal, and not denied by ISEI (those are in a different group)
    active_report = ceu_report.filter(Q(principal_reviewed='n'), ~Q(isei_reviewed='d'))  # not reviewed by principal
    submitted_report = ceu_report.filter(Q(principal_reviewed='a'), Q(isei_reviewed='n'))  # submitted to ISEI
    approved_report = ceu_report.filter(isei_reviewed='a')

    isei_denied_independent_instance = ceu_instance.filter(isei_reviewed='d', ceu_report__isei_reviewed='a',
                                                           date_resubmitted=None)

    # resubmitted instance that was denied while it's report approved
    active_independent_instance = ceu_instance.filter(isei_reviewed='d', ceu_report__isei_reviewed='a',
                                                      principal_reviewed='n', date_resubmitted__isnull=False)

    submitted_instance = ceu_instance.filter(
        Q(ceu_report__in=submitted_report) | Q(isei_reviewed='n', ceu_report__in=approved_report,
                                               principal_reviewed='a'))
    approved_instance = ceu_instance.filter(isei_reviewed='a').order_by('-date_completed')

    if is_in_group(request.user, 'teacher'):
        user_not_teacher = False
    else:
        user_not_teacher = True

    # print(new_school_year)
    # print(active_report)
    context = dict(teacher=teacher, user_not_teacher=user_not_teacher,
                   # instance_filter=instance_filter,
                   new_school_year=new_school_year, active_report=active_report,
                   submitted_report=submitted_report,
                   principal_denied_report=principal_denied_report, isei_denied_report=isei_denied_report,
                   submitted_instance=submitted_instance,
                   isei_denied_independent_instance=isei_denied_independent_instance,
                   active_independent_instance=active_independent_instance,
                   approved_report=approved_report, approved_instance=approved_instance, )

    return render(request, 'teachercert/my_ceu_dashboard.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['teacher', 'staff', 'admin'])
def my_academic_classes(request, pk):
    user = User.objects.get(id=pk)
    teacher = Teacher.objects.get(user=user)
    academic_class = AcademicClass.objects.filter(teacher=teacher)

    a_class = AcademicClass(teacher=teacher)
    form = AcademicClassForm(instance=a_class)
    if request.method == 'POST':
        if request.POST.get('submit'):
            form = AcademicClassForm(request.POST, instance=a_class)
            if form.is_valid():
                form.save()
                email_AcademicClass_submitted(teacher)

    if is_in_group(request.user, 'teacher'):
        user_not_teacher = False
    else:
        user_not_teacher = True

    context = dict(teacher=teacher, academic_class=academic_class, user_not_teacher=user_not_teacher, form=form)

    return render(request, 'teachercert/my_academic_classes.html', context)


# delete academic_class (by id)
@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'staff', 'teacher'])
def delete_academic_class(request, pk):
    academic_class = AcademicClass.objects.get(id=pk)
    if request.method == "POST":
        academic_class.delete()
        # if is_in_group(request.user, 'teacher'):  # teacher landing page
        return redirect('my_academic_classes', academic_class.teacher.user.id)

    context = {'item': academic_class}
    return render(request, 'teachercert/delete_academic_class.html', context)


# update academic class (by id)
@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'staff', 'teacher'])
def update_academic_class(request, pk):
    academic_class = AcademicClass.objects.get(id=pk)
    form = AcademicClassForm(instance=academic_class)

    if request.method == 'POST':
        if request.POST.get('submit'):
            form = AcademicClassForm(request.POST, instance=academic_class)
            if form.is_valid():
                form.save()
                return redirect('my_academic_classes', academic_class.teacher.user.id)

    context = dict(form=form)
    return render(request, "teachercert/update_academic_class.html", context)


# Common views

# isei's info page about all reports with filter
@login_required(login_url='login')
@allowed_users(allowed_roles=['staff', 'principal', 'registrar','teacher'])
def CEUreports(request):
    if request.user.groups.filter(name='staff').exists():  # ISEI staff has access to all reports
        ceu_reports = CEUReport.objects.filter(teacher__user__is_active=True)
        is_staff = True
    elif request.user.groups.filter(name='principal').exists():
        principal = request.user.teacher
        ceu_reports = CEUReport.objects.filter(teacher__user__profile__school=principal.user.profile.school,
                                               teacher__user__is_active=True)  # principal has access to reports from his/her school
        is_staff = False

    else:
        teacher = request.user.teacher
        ceu_reports = CEUReport.objects.filter(teacher=teacher)  # principal has access to reports from his/her school
        is_staff = False

    # is staff is used to show/hide certain sections in the filter and table (school)
    ceu_report_filter = CEUReportFilter(request.GET, queryset=ceu_reports)
    ceu_reports = ceu_report_filter.qs

    if request.POST.get('sendemail'):
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        for a in ceu_reports:
            complete_message = "Dear " + str(a.teacher.first_name) + "," + "\n \n" + message + "\n \n"
            send_email(subject, complete_message, [a.teacher.user.email])

    context = dict(ceu_reports=ceu_reports, ceu_report_filter=ceu_report_filter, is_staff=is_staff)
    return render(request, 'teachercert/ceu_reports.html', context)


# principal views

# principal's approval of teacher activities
@login_required(login_url='login')
@allowed_users(allowed_roles=['principal', 'registrar','staff'])
def principal_ceu_approval(request, recID=None, instID=None):
    principal = request.user
    teachers = Teacher.objects.filter(user__profile__school=principal.profile.school, user__is_active=True)

    ceu_report = CEUReport.objects.filter(teacher__in=teachers)  # all the reports from this teacher's school
    ceu_report_notreviewed = ceu_report.filter(date_submitted__isnull=False, principal_reviewed='n').order_by(
        'updated_at')  # submitted reports to the principal, not yet reviewed

    # ceu_reports approved or denied within a year
    year_ago = datetime.today() - timedelta(days=366)
    ceu_report_approved = ceu_report.filter(date_submitted__isnull=False, principal_reviewed='a',
                                            reviewed_at__gt=year_ago).order_by('reviewed_at')
    ceu_report_denied = ceu_report.filter(date_submitted__isnull=True, principal_reviewed='d',
                                          reviewed_at__gt=year_ago).order_by('reviewed_at')

    # resubmitted instance that was denied while it's report approved
    # Todo would this be enough to filter on isei_reviewed ='n', date_resubmitted not null ? (If yes, set isei_reviewed='n' at resubmission (up in PDA_update)
    ceu_instance_notreviewed = CEUInstance.objects.filter(ceu_report__in=ceu_report, ceu_report__isei_reviewed='a',
                                                          isei_reviewed='d', date_resubmitted__isnull=False,
                                                          principal_reviewed='n')

    if request.method == 'POST':
        if request.POST.get('approved'):  # update report and instances as approved by the principal
            ceu_report = CEUReport.objects.filter(id=recID).update(principal_reviewed='a', principal_comment=None,
                                                                   reviewed_at=Now())
            this_report = CEUReport.objects.get(id=recID)  # the above is a query set and we need just the object
            CEUInstance.objects.filter(ceu_report=this_report).update(principal_reviewed='a', reviewed_at=Now())
            email_CEUReport_approved_by_principal(this_report.teacher, this_report.school_year.name)

    if request.method == 'POST':
        if request.POST.get('denied'):
            ceu_report = CEUReport.objects.filter(id=recID).update(principal_reviewed='d', date_submitted=None,
                                                                   principal_comment=request.POST.get(
                                                                       'principal_comment'), reviewed_at=Now())
            this_report = CEUReport.objects.get(id=recID)  # the above is a query set and we need just the object
            CEUInstance.objects.filter(ceu_report=this_report).update(principal_reviewed='d', date_resubmitted=None,
                                                                      reviewed_at=Now())
            email_CEUReport_denied_by_principal(this_report.teacher, this_report.school_year.name, this_report.principal_comment)

    #allow principal to cancel
    # if request.method == 'POST':
    #     if request.POST.get('cancel'):
    #         ceu_report = CEUReport.objects.filter(id=recID).update(principal_reviewed='n',
    #                                                                date_submitted=F('updated_at'))
    #         this_report = CEUReport.objects.get(id=recID)
    #         CEUInstance.objects.filter(ceu_report=this_report).update(principal_reviewed='n',
    #                                                                   date_resubmitted=F('updated_at'))
    #         email_CEUReport_retracted_by_principal(this_report.teacher, this_report.school_year.name)

    if request.method == 'POST':
        if request.POST.get('approveinst'):
            # todo if ceu_instance_notreviewed filtering can be simplified, isei_reviewed ='n' doesn't need to be here
            CEUInstance.objects.filter(id=instID).update(principal_reviewed='a', isei_reviewed='n', reviewed_at=Now(),
                                                         principal_comment=None)
            this_activity = CEUInstance.objects.get(id=instID)
            email_CEUactivity_approved_by_principal(this_activity.ceu_report.teacher)

    if request.method == 'POST':
        if request.POST.get('denyinst'):
            CEUInstance.objects.filter(id=instID).update(principal_reviewed='d', date_resubmitted=None,
                                                         principal_comment=request.POST.get('principal_comment'),
                                                         reviewed_at=Now())
            this_activity = CEUInstance.objects.get(id=instID)
            email_CEUactivity_denied_by_principal(this_activity.ceu_report.teacher)

    context = dict(teachers=teachers,
                   ceu_report_notreviewed=ceu_report_notreviewed, ceu_report_approved=ceu_report_approved,
                   ceu_report_denied=ceu_report_denied,
                   ceu_instance_notreviewed=ceu_instance_notreviewed, )
    return render(request, 'teachercert/principal_ceu_approval.html', context)



# isei's approval of teacher activities
@login_required(login_url='login')
@allowed_users(allowed_roles=['staff'])
def isei_ceu_approval(request, repID=None, instID=None):
    teachers = Teacher.objects.filter(user__is_active=True)
    ceu_report_notreviewed = CEUReport.objects.filter(principal_reviewed='a', isei_reviewed='n',
                                                      teacher__in=teachers).order_by('date_submitted')

    # ceu_reports approved or denied within a year
    year_ago = datetime.today() - timedelta(days=300)
    ceu_report_approved = CEUReport.objects.filter(isei_reviewed='a', reviewed_at__gt=year_ago,
                                                   teacher__in=teachers).order_by("reviewed_at").order_by("school_year")
    ceu_report_denied = CEUReport.objects.filter(isei_reviewed='d', reviewed_at__gt=year_ago,
                                                 teacher__in=teachers).order_by("reviewed_at").order_by("school_year")
    ceu_instance_notreviewed = CEUInstance.objects.filter(ceu_report__in=ceu_report_approved, isei_reviewed='n',
                                                          date_resubmitted__isnull=False, principal_reviewed='a', )

    if request.method == 'POST':
        if request.POST.get('approveinst'):
            CEUInstance.objects.filter(id=instID).update(isei_reviewed='a',
                                                         approved_ceu=request.POST.get('approved_ceu'),
                                                         reviewed_at=Now(), isei_comment=None)
            this_activity = CEUInstance.objects.get(id=instID)
            #email_CEUactivity_approved_by_ISEI(this_activity.ceu_report.teacher)

    if request.method == 'POST':
        if request.POST.get('denyinst'):
            CEUInstance.objects.filter(id=instID).update(isei_reviewed='d',
                                                         isei_comment=request.POST.get('isei_comment'),
                                                         principal_reviewed='n', date_resubmitted=None,
                                                         reviewed_at=Now())
            this_activity = CEUInstance.objects.get(id=instID)
            #email_CEUactivity_denied_by_ISEI(this_activity.ceu_report.teacher)

    if request.method == 'POST':
        if request.POST.get('cancelinst'):
            CEUInstance.objects.filter(id=instID).update(isei_reviewed='n', principal_reviewed='a',
                                                         date_resubmitted=F('updated_at'))

    if request.method == 'POST':
        if request.POST.get('approved'):
            ceu_report = CEUReport.objects.filter(id=repID).update(isei_reviewed='a', isei_comment=None,
                                                                   reviewed_at=Now())
            CEUInstance.objects.filter(ceu_report=ceu_report).update(isei_reviewed='a', reviewed_at=Now())
            this_report = CEUReport.objects.get(id=repID)

            email_CEUReport_approved_by_ISEI(this_report.teacher, this_report.school_year.name)

    if request.method == 'POST':
        if request.POST.get('denied'):
            ceu_report = CEUReport.objects.filter(id=repID).update(isei_reviewed='d', date_submitted=None,
                                                                   principal_reviewed='n',
                                                                   isei_comment=request.POST.get('isei_comment'),
                                                                   reviewed_at=Now())
            CEUInstance.objects.filter(ceu_report=ceu_report).update(principal_reviewed='n', isei_reviewed='d',
                                                                     date_resubmitted=None, reviewed_at=Now())
            this_report = CEUReport.objects.get(id=repID)

            email_CEUReport_denied_by_ISEI(this_report.teacher, this_report.school_year.name, this_report.isei_comment)

    if request.method == 'POST':
        if request.POST.get('cancel'):
            ceu_report = CEUReport.objects.filter(id=repID).update(isei_reviewed='n', date_submitted=F('last_submitted'),
                                                                   principal_reviewed='a')
            CEUInstance.objects.filter(ceu_report=ceu_report).update(principal_reviewed='a', isei_reviewed='n',
                                                                     date_resubmitted=Now())
            this_report = CEUReport.objects.get(id=repID)

            email_CEUReport_retracted_by_ISEI(this_report.teacher, this_report.school_year.name)

    context = dict(teachers=teachers, ceu_report_notreviewed=ceu_report_notreviewed,
                   ceu_report_approved=ceu_report_approved, ceu_report_denied=ceu_report_denied,
                   ceu_instance_notreviewed=ceu_instance_notreviewed)

    return render(request, 'teachercert/isei_ceu_approval.html', context)



@login_required(login_url='login')
@allowed_users(allowed_roles=['staff'])
def isei_ceu_report_approval(request, repID, instID=None):

    ceu_report = CEUReport.objects.get(id=repID)

    if request.method == 'POST':
        if request.POST.get('approveinst'):
            CEUInstance.objects.filter(id=instID).update(isei_reviewed='a',
                                                         approved_ceu=request.POST.get('approved_ceu'),
                                                         reviewed_at=Now(), isei_comment=None)
            this_activity = CEUInstance.objects.get(id=instID)

    if request.method == 'POST':
        if request.POST.get('denyinst'):
            CEUInstance.objects.filter(id=instID).update(isei_reviewed='d',
                                                         isei_comment=request.POST.get('isei_comment'),
                                                         principal_reviewed='n', date_resubmitted=None,
                                                         reviewed_at=Now())
            this_activity = CEUInstance.objects.get(id=instID)

    if request.method == 'POST':
        if request.POST.get('cancelinst'):
            CEUInstance.objects.filter(id=instID).update(isei_reviewed='n', principal_reviewed='a',
                                                         date_resubmitted=F('updated_at'))

    if request.method == 'POST':
        if request.POST.get('approved'):
            ceu_report = CEUReport.objects.filter(id=repID).update(isei_reviewed='a', isei_comment=None,
                                                                   reviewed_at=Now())
            CEUInstance.objects.filter(ceu_report=ceu_report).update(isei_reviewed='a', reviewed_at=Now())
            this_report = CEUReport.objects.get(id=repID)

            email_CEUReport_approved_by_ISEI(this_report.teacher, this_report.school_year.name)

    if request.method == 'POST':
        if request.POST.get('denied'):
            ceu_report = CEUReport.objects.filter(id=repID).update(isei_reviewed='d', date_submitted=None,
                                                                   principal_reviewed='n',
                                                                   isei_comment=request.POST.get('isei_comment'),
                                                                   reviewed_at=Now())
            CEUInstance.objects.filter(ceu_report=ceu_report).update(principal_reviewed='n', isei_reviewed='d',
                                                                     date_resubmitted=None, reviewed_at=Now())
            this_report = CEUReport.objects.get(id=repID)

            email_CEUReport_denied_by_ISEI(this_report.teacher, this_report.school_year.name, this_report.isei_comment)

    if request.method == 'POST':
        if request.POST.get('cancel'):
            ceu_report = CEUReport.objects.filter(id=repID).update(isei_reviewed='n', date_submitted=F('last_submitted'),
                                                                   principal_reviewed='a')
            CEUInstance.objects.filter(ceu_report=ceu_report).update(principal_reviewed='a', isei_reviewed='n',
                                                                     date_resubmitted=Now())
            this_report = CEUReport.objects.get(id=repID)

            email_CEUReport_retracted_by_ISEI(this_report.teacher, this_report.school_year.name)

    context = dict(p=ceu_report)

    return render(request, 'teachercert/isei_ceu_report_approval.html', context)

# create a pdf with approved CEUs
# @login_required(login_url='login')
# @allowed_users(allowed_roles=['staff'])
# def approved_pdf(request):
#     # Create a Bytestream buffer
#     buf = io.BytesIO()
#     # Create a canvas
#     c = canvas.Canvas(buf, pagesize=letter, bottomup=0)
#     # Create text object - what will be on the canvas
#     textob = c.beginText()
#     textob.setFont("Helvetica", 12)
#     textob.setTextOrigin(inch, inch)
#
#     # Add text
#     lines = []
#     approved_report = CEUReport.objects.filter(isei_reviewed='a')
#     # approved_instance = CEUInstance.objects.filter(isei_reviewed='a')
#     # for a in approved_instance:
#     for a in approved_report:
#         lines.append("")
#         # lines.append(a.ceu_report.teacher.first_name +" "+a.ceu_report.teacher.last_name)
#         lines.append(a.teacher.first_name + " " + a.teacher.last_name + ", " + a.school_year.name)
#         lines.append("")
#         for i in a.ceuinstance_set.all():
#             categ = i.ceu_category
#             lines.append(categ + " " + str(i.date_completed))
#             lines.append(i.description)
#             lines.append(str(i.approved_ceu))
#
#     for line in lines:
#         textob.textLine(line)
#
#     # Finish up
#     c.drawText(textob)
#     c.showPage()
#     c.save()
#     pdf = buf.getvalue()
#     buf.close()
#
#     response = HttpResponse(content_type='application/pdf')
#     response['Content-Disposition'] = 'inline; filename="mypdf.pdf"'
#     response.write(pdf)
#     # return response
#     return pdf
#     # (to use it with approved_pdf2) comment response and uncomment return pdf
#
#
# # email a pdf with approved CEUs
# @login_required(login_url='login')
# @allowed_users(allowed_roles=['staff'])
# def approved_pdf2(request):
#     email = EmailMessage(
#         'Subject here', 'Here is the message.', 'ritab.isei.life@gmail.com', ['oldagape@yahoo.com'])
#     pdf = approved_pdf(request)
#     email.attach("Approved_CEUs.pdf", pdf, 'application/pdf')
#     email.send()
#
#     return render(request, 'teachercert/isei_ceu_approval.html')


# TEACHER CERTIFICATE FUNCTIONS

def load_renewal(request):
    certification_type_id = request.GET.get('certification_type_id')
    renewal = Renewal.objects.filter(certification_type__id=certification_type_id)
    return render(request, 'teachercert/ajax_renewal_list.html', {'renewal': renewal})


# ISEI only views
@login_required(login_url='login')
@allowed_users(allowed_roles=['staff'])
def standard_checklist(request, teacherID):

    teacher = Teacher.objects.get(id=teacherID)

    checklist = StandardChecklist.objects.filter(teacher = teacher)
    if not checklist:
        checklist = StandardChecklist(teacher = teacher)
        checklist.save()
    checklist = StandardChecklist.objects.get(teacher = teacher)
    checklist_form=StandardChecklistForm(instance=checklist)

    if request.method == "POST":
        form = StandardChecklistForm(request.POST, instance=checklist)
        if form.is_valid():
            form.save()
        if request.POST.get('save'):
            return redirect('manage_tcertificate', teacherID)

    context = dict(teacher = teacher, checklist_form= checklist_form)
    return render(request, 'teachercert/standard_checklist.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['staff'])
def manage_tcertificate(request, pk, certID=None):
    # pk is teacher.id

    teacher = Teacher.objects.get(id=pk)
    userID = teacher.user.id

    prev_certificates = TCertificate.objects.filter(Q(teacher=teacher), ~Q(id=certID))
    ceu_reports = None
    academic_class = None

    if certID:  # if the certificate already exists
        tcertificate = TCertificate.objects.get(pk=certID)
        # ceu_reports and academic classes submitted for this certificate
        ceu_reports = ceureports_for_certificate(tcertificate)
        academic_class = academic_classes_for_certificate(tcertificate)
    else:
        tcertificate = TCertificate(teacher=teacher)  # initialize a new certificate

    if teacher.teacherbasicrequirement_set.all():
        basic_requirements = TeacherBasicRequirement.objects.filter(teacher=teacher)
        tbasic_requirement_formset = TeacherBasicRequirementFormSet(queryset=basic_requirements)
    else:
    #    basics = Requirement.objects.filter(category='b')
    #    for basic in basics:
    #        b = TeacherBasicRequirement(basic_requirement=basic, teacher=teacher)
    #        b.save()
        basic_requirements = None
        tbasic_requirement_formset = None

    tcertificate_form = TCertificateForm(instance=tcertificate)  # Certificate form, defined in forms.py
    tendorsement_formset = TEndorsementFormSet(instance=tcertificate)  # Endorsement formset, define in forms.py


    if request.method == "POST" and (request.POST.get('add_endorsement') or request.POST.get('submit_certificate')):
        # if the certificate is modified
        if certID:
            tcertificate_form = TCertificateForm(request.POST, instance=tcertificate)
        else:
            tcertificate_form = TCertificateForm(request.POST)

        tendorsement_formset = TEndorsementFormSet(request.POST)

        if tcertificate_form.is_valid():  # validate the certificate info
            tcertificate = tcertificate_form.save()
            tendorsement_formset = TEndorsementFormSet(request.POST, instance=tcertificate)

            if basic_requirements:
                tbasic_requirement_formset = TeacherBasicRequirementFormSet(request.POST)
                tbasic_requirement_formset.save()

            if tendorsement_formset.is_valid():  # validate the endorsement info
                tendorsement_formset.save()

            if request.POST.get('add_endorsement'):  # if more rows are needed for endorsements reload page
                return redirect('manage_tcertificate', pk=pk, certID=tcertificate.id)
            if request.POST.get('submit_certificate'):  # if certificate is submitted return to teacher_cert page
                messages.success(request, 'Certificate was successfully saved!')
                email_Certificate_issued_or_modified(teacher)
                return redirect('manage_tcertificate', pk=pk, certID=tcertificate.id)

    if StandardChecklist.objects.filter(teacher=teacher):
        checklist=StandardChecklist.objects.get(teacher=teacher)
    else:
        checklist=None

    # certID is used in the template to reload page after previous certificates are archived
    context = dict(pk=pk, userID=userID, is_staff=True, tcertificate_form=tcertificate_form,
                   tendorsement_formset=tendorsement_formset, tbasic_requirement_formset=tbasic_requirement_formset,
                   prev_certificates=prev_certificates, certID=certID,
                   ceu_reports=ceu_reports, academic_class=academic_class,
                   checklist=checklist,
                   )
    return render(request, 'teachercert/manage_tcertificate.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['staff'])
def delete_tcertificate(request, certID=None):
    tcertificate = TCertificate.objects.get(id=certID)
    if request.method == "POST":
        tcertificate.delete()
        return redirect('isei_teachercert')

    context = dict(item=tcertificate)
    return render(request, 'teachercert/delete_tcertificate.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['staff'])
def archive_tcertificate(request, cID, certID):
    tcertificate = TCertificate.objects.get(id=cID)
    TCertificate.objects.filter(id=cID).update(archived=True)
    return redirect('manage_tcertificate', pk=tcertificate.teacher.id, certID=certID)


@login_required(login_url='login')
@allowed_users(allowed_roles=['staff'])
def de_archive_tcertificate(request, cID, certID):
    tcertificate = TCertificate.objects.get(id=cID)
    TCertificate.objects.filter(id=cID).update(archived=False)
    return redirect('manage_tcertificate', pk=tcertificate.teacher.id, certID=certID)


# isei's info page about teacher certification
@login_required(login_url='login')
@allowed_users(allowed_roles=['staff'])
def isei_teachercert(request):
    teachers = Teacher.objects.filter(user__is_active=True)
    # school_year = SchoolYear.objects.get(active_year = True)
    # school_year = SchoolYear.objects.filter(active_year= True).first()

    tcertificates = TCertificate.objects.filter(teacher__user__is_active=True)
    tcertificates_filter = TCertificateFilter(request.GET, queryset=tcertificates)
    tcertificates = tcertificates_filter.qs

    if request.POST.get('sendemail'):
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        for a in tcertificates:
            complete_message = "Dear "+ str(a.teacher.first_name)+"," + "\n \n" + message + "\n \n"
            send_email(subject, complete_message, [a.teacher.user.email])

    context = dict(teachers=teachers,
                   tcertificates=tcertificates, tcertificates_filter=tcertificates_filter)
    return render(request, 'teachercert/isei_teachercert.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['teacher', 'staff', 'principal','registrar'])
def teachercert_application(request, pk):
    # pk - teacher ID

    teacher = Teacher.objects.get(id=pk)
    if TeacherCertificationApplication.objects.filter(teacher=teacher):
        application = TeacherCertificationApplication.objects.get(teacher=teacher)
    else:
        application = TeacherCertificationApplication(teacher=teacher)


    previous_date = application.date
    # print(previous_date)
    application.date = None
    application.signature = None
    application.closed = False
    # print(application.date)

    address = Address.objects.get(teacher=teacher)
    application_form = TeacherCertificationApplicationForm(instance=application)
    school_of_employment = SchoolOfEmployment.objects.filter(teacher=teacher).order_by('-start_date')
    college_attended = CollegeAttended.objects.filter(teacher=teacher).order_by('-start_date')

    if request.method == 'POST':
        application_form = TeacherCertificationApplicationForm(request.POST, request.FILES or None,
                                                               instance=application)
        if application_form.is_valid():
            application = application_form.save(commit=False)
            expired = False
            if application.date_initial == None:
                initial = True
                application.date_initial = application.date
                update = False

            else:
                if newest_certificate(teacher):
                    initial = False
                else:
                    initial = True

                if application.date > previous_date + timedelta(183):
                    application.billed = 'n'
                    expired = True
                    update = False
                else:
                    update = True

            application = application_form.save()
            email_Application_submitted(teacher, initial, update, expired)
            return redirect('teachercert_application_done', pk=teacher.id)

    context = dict(teacher=teacher, address=address,
                   application_form=application_form,
                   school_of_employment=school_of_employment, college_attended=college_attended,
                   )
    return render(request, 'teachercert/teachercert_application.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['teacher', 'staff', 'principal','registrar'])
def teachercert_application_done(request, pk):
    # pk - teacher ID

    teacher = Teacher.objects.get(id=pk)
    address = Address.objects.get(teacher=teacher)
    application = TeacherCertificationApplication.objects.get(teacher=teacher)

    school_of_employment = SchoolOfEmployment.objects.filter(teacher=teacher).order_by('-start_date')
    college_attended = CollegeAttended.objects.filter(teacher=teacher).order_by('-start_date')

    context = dict(teacher=teacher, address=address,
                   application=application,
                   school_of_employment=school_of_employment, college_attended=college_attended,
                   )
    return render(request, 'teachercert/teachercert_application_done.html', context)


# list of applications from current teachers
@login_required(login_url='login')
@allowed_users(allowed_roles=['staff'])
def isei_teacher_applications(request):
    applications = TeacherCertificationApplication.objects.filter(teacher__user__is_active=True).order_by('-date', 'closed', 'billed', '-isei_revision_date',
                                                                                                          )
    application_filter = TeacherCertificationApplicationFilter(request.GET, queryset=applications)
    applications = application_filter.qs
    if request.POST.get('sendemail'):
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        for a in applications:
            complete_message = "Dear "+ str(a.teacher.first_name)+"," + "\n \n" + message + "\n \n" + str(a.public_note)
            send_email(subject, complete_message, [a.teacher.user.email])
    context = dict(applications=applications, application_filter=application_filter)
    return render(request, 'teachercert/isei_teacher_applications.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['staff'])
def isei_manage_application(request, appID):
    application = TeacherCertificationApplication.objects.get(id=appID)

    teacher = application.teacher
    address = Address.objects.get(teacher=teacher)
    school_of_employment = SchoolOfEmployment.objects.filter(teacher=teacher).order_by('-end_date')
    college_attended = CollegeAttended.objects.filter(teacher=teacher).order_by('-end_date')

    application_form = TeacherCertificationApplicationISEIForm(instance=application)

    if request.method == "POST":
        application_form = TeacherCertificationApplicationISEIForm(request.POST, instance=application)
        if application_form.is_valid():
            application = application_form.save()
            if application.closed:
                email_Application_processed(teacher)
            elif application.isei_revision_date:
                email_Application_on_hold(teacher, application.public_note)

            # return redirect('isei_teacher_applications')

    context = dict(application=application, application_form=application_form,
                   teacher=teacher, address=address,
                   school_of_employment=school_of_employment, college_attended=college_attended)
    return render(request, 'teachercert/isei_manage_application.html', context)



#in works
@login_required(login_url='login')
@allowed_users(allowed_roles=['staff', 'principal'])
def bulk_ceu_entry(request):
    is_isei = request.user.groups.filter(name='staff').exists()
    is_principal = request.user.groups.filter(name='principal').exists()

    if is_principal:
        teachers = Teacher.objects.filter(user__is_active=True, school=request.user.profile.school)
    else:
        teachers = Teacher.objects.filter(user__is_active=True)  # Show all active teachers for ISEI

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if request.GET.get('school'):
            school_id = request.GET['school']
            teachers = Teacher.objects.filter(school_id=school_id, user__is_active=True)
        else:
            teachers = Teacher.objects.filter(user__is_active=True)
        teacher_list = [{'id': teacher.id, 'name': teacher.name()} for teacher in teachers]
        return JsonResponse({'teachers': teacher_list})


    if request.method == 'POST':
        form = BulkCEUForm(request.POST, request.FILES)
        if form.is_valid():
            school = form.cleaned_data.get('school') if not is_principal else request.user.profile.school
            school_year = form.cleaned_data['school_year']
            ceu_type = form.cleaned_data['ceu_type']
            description = form.cleaned_data['description']
            evidence = form.cleaned_data['evidence']
            approved_ceu = form.cleaned_data['approved_ceu']
            date_completed = form.cleaned_data['date_completed']
            file = form.cleaned_data['file']

            if school:
                teachers =Teacher.objects.filter(school=school, user__is_active=True)

            if file:
                current_year = datetime.now().year
                saved_file_path = default_storage.save(f'Supporting_Files/{current_year}/{file.name}', file)
            else:
                saved_file_path=None

            for teacher in teachers:
                individual_ceu = request.POST.get(f'approved_ceu_{teacher.id}', approved_ceu)
                try:
                    individual_ceu = float(individual_ceu) if individual_ceu.strip() else 0
                except ValueError:
                    individual_ceu = 0

                if individual_ceu > 0:
                    ceu_report, _ = CEUReport.objects.get_or_create(
                        teacher=teacher, school_year=school_year
                    )

                    ceu_instance, created = CEUInstance.objects.get_or_create(
                        ceu_report=ceu_report, ceu_type=ceu_type, date_completed=date_completed,
                        defaults={
                            'description': description,
                            'evidence': evidence,
                            'approved_ceu': individual_ceu,
                            'amount':individual_ceu,
                            'units': 'c',
                            'file': saved_file_path,
                            'isei_reviewed': 'a' if is_isei else 'n',
                            'principal_reviewed': 'a' if is_principal else 'n',
                        }
                    )
                    #if created:
                    #    print(teacher)
            return redirect('CEUreports')
    else:
        form = BulkCEUForm(teachers=teachers)

    context = dict(form=form, teachers=teachers, is_principal=is_principal)

    return render(request, 'teachercert/bulk_ceu_entry.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['staff'])
def add_ISEI_CEUs(request):
    school_list = School.objects.filter(active=True)
    school_year_list = SchoolYear.objects.filter(active_year=True)

    iseiCEUformset = modelformset_factory(CEUInstance, fields=('approved_ceu',), extra=0, can_delete=True)
    case = "blank"

    if request.method == 'POST' and request.POST.get('submit_ceus'):
        school = School.objects.get(id=request.POST['selected_school'])
        school_year = SchoolYear.objects.get(id=request.POST['selected_school_year'])
        date_completed = request.POST['date_completed']
        description = request.POST['description']
        CEUs = request.POST['CEUs']
        teachers = Teacher.objects.filter(user__profile__school=school, user__is_active=True)
        ceu_category = CEUCategory.objects.get(name="Group")
        ceu_type = CEUType.objects.get(description__contains="ISEI")
        for t in teachers:
            ceu_report = CEUReport.objects.filter(teacher=t, school_year=school_year).first()
            if not ceu_report:
                ceu_report = CEUReport(teacher=t, school_year=school_year)
                ceu_report.save()
                #email_CEUReport_created(ceu_report.teacher, ceu_report.school_year.name)

            ceu_instance = CEUInstance(ceu_report=ceu_report, ceu_category=ceu_category, ceu_type=ceu_type,
                                       date_completed=date_completed, description=description,
                                       isei_reviewed='a', approved_ceu=CEUs, amount=CEUs, units='c')

            try:
                ceu_instance.save()
                new = True
            except:
                new = False


        if new == False:
            messages.success(request,
                             "This activity has already been recorded. You can adjust CEUs or delete activity for individual teachers below.")
        else:
            messages.success(request, "New CEU activities have been recorded for the following teachers.")

        ceu_instances = CEUInstance.objects.filter(date_completed=date_completed, description=description)
        ceu_form = iseiCEUformset(queryset=ceu_instances)
        case = str(school.name) + ", " + str(school_year.name) + ',' + "\n" + str(date_completed) + ", " + str(
            description) + ", " + str(CEUs) + " CEUs"

    else:
        if request.method == 'POST' and request.POST.get('submit_changes'):
            ceu_form = iseiCEUformset(request.POST)
            case = "Changes were not saved"
            if ceu_form.is_valid():
                ceu_form.save()
                case = "Changes were saved"
        else:
            ceu_form = iseiCEUformset(queryset=CEUInstance.objects.none())

    if request.method == 'POST' and request.POST.get('submit_changes'):
        reports = CEUReport.objects.filter(school_year__id__in= school_year_list)
        for r in reports:
            if not CEUInstance.objects.filter(ceu_report=r):
                r.delete()

    context = dict(school_list=school_list, school_year_list=school_year_list, ceu_form=ceu_form, case=case)

    return render(request, 'teachercert/add_ISEI_CEUs.html', context)


# Background Checks
@login_required(login_url='login')
@allowed_users(allowed_roles=['staff', 'principal','registrar'])
def mark_background_check(request, schoolid):

    teachers= Teacher.objects.filter(user__profile__school__id=schoolid, user__is_active=True).order_by('background_check')

    #formset for all teachers to mark background check
    bcformset = modelformset_factory(Teacher, fields=('background_check',),extra=0, can_delete=False)

    if request.method == 'POST':
        bc_form = bcformset(request.POST)
        case = "Changes were not saved"
        if bc_form.is_valid():
            bc_form.save()
            case = "Changes were saved"
    else:
        bc_form = bcformset(queryset=teachers)
        case = None

    context = dict(bc_form=bc_form, case=case)

    return render(request, 'teachercert/mark_background_check.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['staff'])
def create_certificate(request, certID=None):
    certificate = TCertificate.objects.get(id=certID)
    highest_degree = degree(certificate.teacher)
    endorsements = TEndorsement.objects.filter(certificate = certificate)

    context = dict(certificate = certificate, highest_degree=highest_degree, endorsements=endorsements)
    return render(request, 'teachercert/create_certificate.html', context)



#Count missing requirments for a given school

from collections import defaultdict

FIELDS_TO_CHECK = [
    "sop", "sda_doctrine", "sda_history", "sda_health",
    "sda_education", "psychology",
    "assessment", "exceptional_child", "technology",
    "sec_methods"
]

RECOMMENDED_FIELDS = ["dev_psychology", "sec_rw_methods"]

def get_missing_checklist_counts(teachers):

    checklists = StandardChecklist.objects.filter(teacher__in=teachers)
    total = checklists.count()
    if total == 0:
        return [], 0

    missing_counts = defaultdict(int)

    for checklist in checklists:
        for field in FIELDS_TO_CHECK:
            value = getattr(checklist, field)
            if isinstance(value, bool):
                if not value:
                    missing_counts[field] += 1
            else:
                if not value or value <= 0:
                    missing_counts[field] += 1

    result = []
    for field in FIELDS_TO_CHECK:
        count = missing_counts.get(field, 0)
        percent = round((count / total) * 100, 1)
        verbose_name = StandardChecklist._meta.get_field(field).verbose_name
        result.append((verbose_name, count, percent))

    result.sort(key=lambda x: x[1], reverse=True)
    return result, total

def school_checklist_summary(request, school_id):
    school = get_object_or_404(School, id=school_id)
    teachers = Teacher.objects.filter(school=school)
    missing_data, total = get_missing_checklist_counts(teachers)

    context = dict(
        school=school, missing_data=missing_data, total=total,
    )
    return render(request, "teachercert/checklist_school_summary.html", context)

def isei_checklist_summary(request):
    selected_school_id = request.GET.get("school")
    selected_region = request.GET.get("region")  # 'us', 'intl', or None
    all_schools = School.objects.filter(active=True, test=False).select_related('street_address')

    if selected_school_id:
        all_schools = all_schools.filter(id=selected_school_id)

    # Apply region filter
    if selected_region == "us":
        schools = all_schools.filter(street_address__country__code="US")
    elif selected_region == "intl":
        schools = all_schools.exclude(street_address__country__code="US")
    else:
        schools = all_schools  # all

    summaries = []
    counts = defaultdict(int)
    total_teachers = 0

    for school in schools:
        teachers = Teacher.objects.filter(school=school)
        missing_data, total = get_missing_checklist_counts(teachers)
        summaries.append({
            "school": school,
            "missing_data": missing_data,
            "total": total,
        })
        total_teachers += total
        for verbose_name, count, _ in missing_data:
            counts[verbose_name] += count

    overall_data = []
    for field in FIELDS_TO_CHECK:
        verbose_name = StandardChecklist._meta.get_field(field).verbose_name
        count = counts.get(verbose_name, 0)
        percent = round((count / total_teachers) * 100, 1) if total_teachers else 0
        overall_data.append((verbose_name, count, percent))

    overall_data.sort(key=lambda x: x[1], reverse=True)

    context = dict(
        school_summaries=summaries,
        overall_data=overall_data,
        overall_total=total_teachers,
        schools=schools,
        selected_school_id=int(selected_school_id) if selected_school_id else None,
        selected_region=selected_region,
    )

    return render(request, "teachercert/checklist_isei_summary.html", context)