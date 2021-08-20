from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from users.decorators import unauthenticated_user, allowed_users
from .filters import *
from .forms import *
from users.utils import is_in_group
from users.models import *
from .models import *
from django.db.models import Q, F #Q is for queries in filters, F is to update a field using an other field from the model
from django.db.models.functions import Now

# import custom functions
from .myfunctions import *

# for creating the pdf
from django.http import FileResponse
import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from django.http import HttpResponse

#for emailing
from django.core.mail import EmailMessage

from datetime import datetime, timedelta
from django.contrib import messages
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse
from django.forms import inlineformset_factory


# PROFESSIONAL DEVELOPMENT ACTIVITY REPORT - CEUs

#just an info page about the PDA activities
def ceu_info(request):
    return render(request, 'teachercert/ceu_info.html')

# create report for user and school year if no report exists. It is called from myPDADashboard - new activity addition
@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'staff', 'teacher'])
def createPDAreport(request, pk, sy):
    pda_report = PDAReport()
    pda_report.teacher = Teacher.objects.get(user__id=pk)
    pda_report.school_year = SchoolYear.objects.get(id=sy)
    pda_report.save()
    return redirect('create_pda', recId =pda_report.id)


# create PDA instance + allows for report submission (for report with matching pk)
@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'staff', 'teacher'])
def createPDA(request, recId):

    pda_report = PDAReport.objects.get(id=recId) #report
    pda_instance = PDAInstance.objects.filter(pda_report=pda_report) #list of already entered instances
    instanceformset = PDAInstanceFormSet(queryset=PDAInstance.objects.none(), instance=pda_report) # entering new activity

    report_form = PDAreportForm(instance = pda_report) #form for editing current report (summary and submission)

    if request.method == 'POST':
        if request.POST.get('add_activity'): #add activity and stay on page
            instanceformset = PDAInstanceFormSet(request.POST, request.FILES or None, instance=pda_report)
            if instanceformset.is_valid():
                instanceformset.save() #save activity
                instanceformset = PDAInstanceFormSet(queryset=PDAInstance.objects.none(), instance=pda_report) #allow for a new entry


        if request.POST.get('submit_report'): #submit report - go to PDAdashboard
            report_form = PDAreportForm(request.POST, instance=pda_report)
            if report_form.is_valid():
                pda_report = report_form.save() #save report submission
                if pda_report.date_submitted: # if the date is entered the report is submitted to the principal for revision
                    pda_report.principal_reviewed = 'n' #set principal and ISEI revisions to "Not yet" just in case it is a resubmission
                    pda_report.isei_reviewed = 'n'
                    pda_report.save()
                    pda_instance = PDAInstance.objects.filter(pda_report=pda_report)
                    pda_instance.update(principal_reviewed = 'n', isei_reviewed='n') # set all instances to not reviewed as well
                    #todo work on message to principal
                    principal = Teacher.objects.get(user__groups__name='principal', school=pda_report.teacher.school) # get the principal of this teacher
                    if principal: #to avoid an error message just in case principal is not set
                        principal_email = principal.user.email
                        email = EmailMessage(
                            'Report Submission',
                            pda_report.teacher.first_name + " " +pda_report.teacher.last_name + " has submitted a PDA report. Go to www.isei.blablabla to review the submission.",
                            'ritab.isei.life@gmail.com', [principal_email])
                        email.send()
                    return redirect('myPDAdashboard', pk=pda_report.teacher.user.id) # go back to PDAdashboard

        if request.POST.get('update_report'):  # update summary, stay on page
            report_form = PDAreportForm(request.POST, instance=pda_report)
            if report_form.is_valid():
                pda_report = report_form.save()

    context = dict(pda_instance=pda_instance,  pda_report=pda_report,
                   instanceformset=instanceformset,  report_form=report_form, )

    return render(request, "teachercert/create_pda.html", context)


# update PDAinstance (by id)
@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'staff', 'teacher'])
def updatePDAinstance(request, pk):
    pdainstance = PDAInstance.objects.get(id=pk)
    form = PDAInstanceForm(instance=pdainstance)

    # if the report has been accepted but the instance denied by ISEI, the instance is resubmitted alone
    resubmit = False
    if ((pdainstance.isei_reviewed == 'd') and (pdainstance.pda_report.isei_reviewed == 'a')):
        resubmit = True

    if request.method == 'POST':
        if request.POST.get('submit'):  #if it's an update within the report, it is saved and send back to report creation
            form = PDAInstanceForm(request.POST, request.FILES or None, instance=pdainstance)
            if form.is_valid():
                form.save()
                return redirect('create_pda', pdainstance.pda_report.id)

        if request.POST.get('resubmit'): #if it is a resubmition
            form = PDAInstanceForm(request.POST, request.FILES or None, instance=pdainstance)
            if form.is_valid():
                form.save()  #save
                # ToDo Should I set isei_reviewed='n' here???
                PDAInstance.objects.filter(id=pk).update(principal_reviewed='n', ) # principal reviewed set to no
                #ToDo work on message to principal
                principal = Teacher.objects.get(user__groups__name='principal', school=pdainstance.pda_report.teacher.school)
                if principal: #if principal assigned sent email.
                    principal_email = principal.user.email
                    email = EmailMessage(
                        'Report Submission',
                        pda_report.teacher.first_name + " " + pda_report.teacher.last_name + " has submitted an activity. Go to www.isei.blablabla to review the submission.",
                        'ritab.isei.life@gmail.com', [principal_email])
                    email.send()
                #if is_in_group(request.user, 'teacher'):        # teacher landing page

                return redirect('myPDAdashboard', pk=pdainstance.pda_report.teacher.user.id)

    context = dict(form=form, resubmit= resubmit) #if resubmit=True the activity has been denied by ISEI and the report it belongs to accepted
    return render(request, "teachercert/update_pdainstance.html", context)


# delete PDAinstance (by id)
@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'staff', 'teacher'])
def deletePDAinstance(request, pk):
    pdainstance = PDAInstance.objects.get(id=pk)
    if request.method == "POST":
        pdainstance.delete()
        #if is_in_group(request.user, 'teacher'):  # teacher landing page
        return redirect('create_pda', pdainstance.pda_report.id)

    context = {'item': pdainstance}
    return render(request, 'teachercert/delete_pdainstance.html', context)

# teacher activities for user with id=pk ... some parts not finished
@login_required(login_url='login')
@allowed_users(allowed_roles=['teacher', 'staff', 'admin'])
def my_academic_classes(request, pk):

    teacher = Teacher.objects.get(user=User.objects.get(id=pk))
    academic_class = AcademicClass.objects.filter(teacher=teacher)

    a_class = AcademicClass(teacher=teacher)
    form = AcademicClassForm(instance = a_class)
    if request.method == 'POST':
        if request.POST.get('submit'):
            form = AcademicClassForm(request.POST, instance=a_class)
            if form.is_valid():
                form.save()

    if is_in_group(request.user, 'teacher'):
        user_not_teacher = False
    else:
        user_not_teacher = True

    context = dict(teacher=teacher, academic_class=academic_class, user_not_teacher= user_not_teacher, form=form)

    return render(request, 'teachercert/my_academic_classes.html', context)


# delete academic_class (by id)
@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'staff', 'teacher'])
def delete_academic_class(request, pk):
    academic_class = AcademicClass.objects.get(id=pk)
    if request.method == "POST":
        academic_class.delete()
        #if is_in_group(request.user, 'teacher'):  # teacher landing page
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




# isei's info page about all reports with filter
@login_required(login_url='login')
@allowed_users(allowed_roles=['staff','principal', 'teacher'])
def PDAreports(request):
    if request.user.groups.filter(name='staff').exists(): #ISEI staff has access to all reports
        pda_reports = PDAReport.objects.all()
        is_staff=True
    elif request.user.groups.filter(name='staff').exists():
        principal = request.user.teacher
        pda_reports = PDAReport.objects.filter(teacher__school = principal.school) #principal has access to reports from his/her school
        is_staff=False
    else:
        teacher = request.user.teacher
        pda_reports = PDAReport.objects.filter(teacher=teacher)  # principal has access to reports from his/her school
        is_staff = False

    #is staff is used to show/hide certain sections in the filter and table (school)
    pda_report_filter = PDAReportFilter(request.GET, queryset=pda_reports)
    pda_reports = pda_report_filter.qs

    context = dict(pda_reports = pda_reports, pda_report_filter = pda_report_filter, is_staff=is_staff)
    return render(request, 'teachercert/PDAreports.html', context)


#principal's approval of teacher activities
@login_required(login_url='login')
@allowed_users(allowed_roles=['principal'])
def principal_pda_approval(request, recID=None, instID=None):
    principal = request.user.teacher
    teachers = Teacher.objects.filter(school = principal.school, active= True)

    pda_report = PDAReport.objects.filter(teacher__school=principal.school) #all the reports from this teacher's school
    pda_report_notreviewed = pda_report.filter( date_submitted__isnull=False, principal_reviewed = 'n').order_by('updated_at') #submitted reports to the principal, not yet reviewed

    #pda_reports approved or denied within a year
    year_ago = datetime.today() - timedelta(days=366)
    pda_report_approved = pda_report.filter(date_submitted__isnull=False, principal_reviewed = 'a', reviewed_at__gt=year_ago).order_by('reviewed_at')
    pda_report_denied = pda_report.filter(date_submitted__isnull=True, principal_reviewed = 'd', reviewed_at__gt=year_ago).order_by('reviewed_at')

    # resubmitted instance that was denied while it's report approved
    #Todo would this be enough to filter on isei_reviewed ='n', date_resubmitted not null ? (If yes, set isei_reviewed='n' at resubmission (up in PDA_update)
    pda_instance_notreviewed = PDAInstance.objects.filter(pda_report__in=pda_report, pda_report__isei_reviewed='a', isei_reviewed='d', date_resubmitted__isnull=False, principal_reviewed='n')


    if request.method == 'POST':
        if request.POST.get('approved'): #update report and instances as approved by the principal
            pda_report = PDAReport.objects.filter(id=recID).update(principal_reviewed='a', principal_comment=None, reviewed_at=Now())
            this_report = PDAReport.objects.get(id=recID) #the above is a query set and we need just the object
            PDAInstance.objects.filter(pda_report = this_report).update(principal_reviewed='a', reviewed_at=Now())
            #email the principal and ISEI about the approval
            #Todo workon the email messages
            email = EmailMessage(
                'Principal Approval', EmailMessage.objects.get(name="PrincipalApprovedToTeacher").message, 'ritab.isei.life@gmail.com', [this_report.teacher.user.email])
            email.send()
            email = EmailMessage(
                'Principal Approval',
                principal.last_name + " " + principal.first_name + " from " + principal.school.name + " has approved " + this_report.teacher.first_name + " " + this_report.teacher.last_name + "'s report.",
                'ritab.isei.life@gmail.com', ['ritab.isei.life@gmail.com'])
            email.send()


    if request.method == 'POST':
        if request.POST.get('denied'):
            pda_report = PDAReport.objects.filter(id=recID).update(principal_reviewed='d', date_submitted = None, principal_comment = request.POST.get('principal_comment'), reviewed_at=Now())
            this_report = PDAReport.objects.get(id=recID) #the above is a query set and we need just the object
            PDAInstance.objects.filter(pda_report=this_report).update(principal_reviewed='d',date_resubmitted = None, reviewed_at=Now())
            #Todo work on the email messages
            email = EmailMessage(
                'Principal Denial', EmailMessage.objects.get(name="PrincipalDeniedToTeacher").message, 'ritab.isei.life@gmail.com',
                [this_report.teacher.user.email])
            email.send()

    if request.method == 'POST':
        if request.POST.get('cancel'):
            pda_report = PDAReport.objects.filter(id=recID).update(principal_reviewed='n', date_submitted = F('updated_at') )
            this_report = PDAReport.objects.get(id=recID)
            PDAInstance.objects.filter(pda_report=this_report).update(principal_reviewed = 'n', date_resubmitted = F('updated_at') )
            # Todo work on the email messages
            email = EmailMessage(
                'Principal Retracted Action', 'The principal has canceled the approval/denial of the PDA submission.', 'ritab.isei.life@gmail.com',
                [this_report.teacher.user.email, 'ritab.isei.life@gmail.com'])
            email.send()

    if request.method == 'POST':
        if request.POST.get('approveinst'):
            #todo if pda_instance_notreviewed filtering can be simplified, isei_reviewed ='n' doesn't need to be here
            PDAInstance.objects.filter(id=instID).update(principal_reviewed='a', isei_reviewed='n', reviewed_at=Now())
            this_activity = PDAInstance.objects.get(id=instID)
            # Todo work on the email messages
            email = EmailMessage(
                'Principal Approval', EmailMessage.objects.get(name="PrincipalApprovedToTeacher").message, 'ritab.isei.life@gmail.com',
                [this_activity.pda_report.teacher.user.email, 'ritab.isei.life@gmail.com'])
            email.send()

    if request.method == 'POST':
        if request.POST.get('denyinst'):
            PDAInstance.objects.filter(id=instID).update(principal_reviewed='d',date_resubmitted = None, principal_comment = request.POST.get('principal_comment'), reviewed_at=Now())
            this_activity = PDAInstance.objects.get(id=instID)
            # Todo work on the email messages
            email = EmailMessage(
                'Principal Denial', EmailMessage.objects.get(name="PrincipalDeniedToTeacher").message,
                'ritab.isei.life@gmail.com',
                [this_activity.pda_report.teacher.user.email])
            email.send()


    context = dict(teachers=teachers,
                   pda_report_notreviewed=pda_report_notreviewed, pda_report_approved=pda_report_approved, pda_report_denied=pda_report_denied,
                   pda_instance_notreviewed = pda_instance_notreviewed,)
    return render(request, 'teachercert/principal_pda_approval.html', context)


#principal's approval of teacher activities
@login_required(login_url='login')
@allowed_users(allowed_roles=['staff'])
def isei_pda_approval(request, repID=None, instID=None):
    teachers = Teacher.objects.filter(active = True)
    pda_report_notreviewed = PDAReport.objects.filter(principal_reviewed ='a', isei_reviewed='n').order_by('date_submitted')

    # pda_reports approved or denied within a year
    year_ago = datetime.today() - timedelta(days=366)
    pda_report_approved = PDAReport.objects.filter(isei_reviewed ='a', reviewed_at__gt= year_ago).order_by("reviewed_at")
    pda_report_denied = PDAReport.objects.filter(isei_reviewed ='d', reviewed_at__gt= year_ago).order_by("reviewed_at")
    pda_instance_notreviewed = PDAInstance.objects.filter(pda_report__in=pda_report_approved, isei_reviewed='n', date_resubmitted__isnull=False, principal_reviewed='a')


    if request.method == 'POST':
        if request.POST.get('approveinst'):
           PDAInstance.objects.filter(id=instID).update(isei_reviewed='a', approved_ceu=request.POST.get('approved_ceu'), reviewed_at=Now())
           #this_activity = PDAInstance.objects.get(id=instID)
           #email = EmailMessage(
           #    'ISEI Approval', "Your submission has been rejected by ISEI. Go to www.blablabla",
           #    'ritab.isei.life@gmail.com',
           #    [this_activity.pda_report.teacher.user.email])
           #email.send()

    if request.method == 'POST':
        if request.POST.get('denyinst'):
           PDAInstance.objects.filter(id=instID).update(isei_reviewed='d', isei_comment=request.POST.get('isei_comment'),
                                                        principal_reviewed = 'n', date_resubmitted = None, reviewed_at=Now())
           this_activity = PDAInstance.objects.get(id=instIDID)
           #email = EmailMessage(
           #    'ISEI Denial', EmailMessage.objects.get(name="ISEIDeniedToTeacher").message,
           #    'ritab.isei.life@gmail.com',
           #    [this_activity.pda_report.teacher.user.email])
           #email.send()

    if request.method == 'POST':
        if request.POST.get('cancelinst'):
           PDAInstance.objects.filter(id=instID).update(isei_reviewed='n', principal_reviewed = 'a', date_resubmitted = F('updated_at'))

    if request.method == 'POST':
        if request.POST.get('approved'):
            pda_report = PDAReport.objects.filter(id=repID).update(isei_reviewed='a', isei_comment=None, reviewed_at=Now())
            PDAInstance.objects.filter(pda_report=pda_report).update(isei_reviewed='a', reviewed_at=Now())
            this_report=PDAReport.objects.get(id=repID)
            email = EmailMessage(
                'ISEI Approval', "ISEI has approved your PDA submission. Go to www.blabla for details",
                'ritab.isei.life@gmail.com',
                [this_report.teacher.user.email])
            email.send()

    if request.method == 'POST':
        if request.POST.get('denied'):
            pda_report = PDAReport.objects.filter(id=repID).update(isei_reviewed='d', date_submitted = None, principal_reviewed ='n', isei_comment = request.POST.get('isei_comment'), reviewed_at=Now())
            PDAInstance.objects.filter(pda_report=pda_report).update(principal_reviewed='n',isei_reviewed='d',date_resubmitted = None, reviewed_at=Now())
            this_report = PDAReport.objects.get(id=repID)
            email = EmailMessage(
                'ISEI Denial', "ISEI has approved your PDA submission. Go to www.blabla for details",
                'ritab.isei.life@gmail.com',
                [this_report.teacher.user.email])
            email.send()

    if request.method == 'POST':
        if request.POST.get('cancel'):
            pda_report = PDAReport.objects.filter(id=repID).update(isei_reviewed='n', date_submitted = F('updated_at'), principal_reviewed ='a')
            PDAInstance.objects.filter(pda_report=pda_report).update(principal_reviewed = 'a', isei_reviewed = 'n', date_resubmitted = Now())


    context = dict(teachers=teachers, pda_report_notreviewed=pda_report_notreviewed, pda_report_approved=pda_report_approved, pda_report_denied=pda_report_denied, pda_instance_notreviewed = pda_instance_notreviewed)
    return render(request, 'teachercert/isei_pda_approval.html', context)



# teacher activities for user with id=pk ... some parts not finished
@login_required(login_url='login')
@allowed_users(allowed_roles=['teacher', 'staff', 'admin'])
def myPDAdashboard(request, pk):
    teacher = Teacher.objects.get(user=User.objects.get(id=pk))

    pda_report = PDAReport.objects.filter(teacher=teacher) #all reports of this teacher

    #all instances run through the filter
    pda_instance = PDAInstance.objects.filter(pda_report__in=pda_report)
    instance_filter = PDAInstanceFilter(request.GET, queryset=pda_instance)
    pda_instance = instance_filter.qs

    #instances from denied reports are not filtered
    principal_denied_report = pda_report.filter(Q(principal_reviewed='d'))
    isei_denied_report = pda_report.filter(Q(isei_reviewed='d'))

    #new school year if report not yet created
    new_school_year = SchoolYear.objects.filter(Q(active_year=True), ~Q(pdareport__in=pda_report))
    #reports not reviewed by principal, and not denied by ISEI (those are in a different group)
    active_report = pda_report.filter(Q(principal_reviewed='n'),~Q(isei_reviewed = 'd')) #not reviewed by principal
    submitted_report = pda_report.filter(Q(principal_reviewed='a'), ~Q(isei_reviewed='a'))  # submitted to ISEI
    approved_report = pda_report.filter(isei_reviewed='a')

    isei_denied_independent_instance = pda_instance.filter(isei_reviewed='d', pda_report__isei_reviewed='a',
                                                           date_resubmitted=None)

    #resubmitted instance that was denied while it's report approved
    active_independent_instance = pda_instance.filter(isei_reviewed = 'd', pda_report__isei_reviewed='a', principal_reviewed = 'n', date_resubmitted__isnull = False)


    submitted_instance = pda_instance.filter(Q(pda_report__in=submitted_report)|Q(isei_reviewed='n', pda_report__in=approved_report,
                                                      principal_reviewed='a'))
    approved_instance = pda_instance.filter(isei_reviewed='a')

    if is_in_group(request.user, 'teacher'):
        user_not_teacher = False
    else:
        user_not_teacher = True
    context = dict(teacher=teacher,user_not_teacher=user_not_teacher, instance_filter=instance_filter,
                   new_school_year = new_school_year, active_report=active_report,
                   submitted_report=submitted_report,
                   principal_denied_report =principal_denied_report, isei_denied_report = isei_denied_report,
                   submitted_instance = submitted_instance,
                   isei_denied_independent_instance = isei_denied_independent_instance,
                   active_independent_instance = active_independent_instance,
                   approved_report = approved_report, approved_instance = approved_instance,)

    return render(request, 'teachercert/myPDAdashboard.html', context)

# todo create layout in myPDAdashboard template for it to look nicer
# todo adjust template so that it would allow for the choosing of a different teacher if user_not_teacher


#create a pdf with approved CEUs
@login_required(login_url='login')
@allowed_users(allowed_roles=['staff'])
def approved_pdf(request):
    #Create a Bytestream buffer
    buf = io.BytesIO()
    #Create a canvas
    c = canvas.Canvas (buf, pagesize = letter, bottomup=0)
    #Create text object - what will be on the canvas
    textob = c.beginText()
    textob.setFont("Helvetica", 12)
    textob.setTextOrigin(inch, inch)

    #Add text
    lines = []
    approved_report = PDAReport.objects.filter(isei_reviewed = 'a')
    #approved_instance = PDAInstance.objects.filter(isei_reviewed='a')
    #for a in approved_instance:
    for a in approved_report:
        lines.append("")
        #lines.append(a.pda_report.teacher.first_name +" "+a.pda_report.teacher.last_name)
        lines.append(a.teacher.first_name + " " + a.teacher.last_name+ ", " + a.school_year.name)
        lines.append("")
        for i in a.pdainstance_set.all():
            categ = i.pda_type.get_category_display()
            lines.append(categ + " " + str(i.date_completed))
            lines.append(i.description)
            lines.append(str(i.approved_ceu))

    for line in lines:
        textob.textLine(line)

    #Finish up
    c.drawText(textob)
    c.showPage()
    c.save()
    pdf=buf.getvalue()
    buf.close()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="mypdf.pdf"'
    response.write(pdf)
    #return response
    return pdf
    #(to use it with approved_pdf2) comment response and uncomment return pdf

# email a pdf with approved CEUs
@login_required(login_url='login')
@allowed_users(allowed_roles=['staff'])
def approved_pdf2(request):
    email = EmailMessage(
        'Subject here', 'Here is the message.', 'ritab.isei.life@gmail.com', ['oldagape@yahoo.com'])
    pdf= approved_pdf(request)
    email.attach("Approved_CEUs.pdf", pdf, 'application/pdf')
    email.send()

    return render(request, 'teachercert/isei_pda_approval.html')




# TEACHER CERTIFICATE FUNCTIONS


@login_required(login_url='login')
@allowed_users(allowed_roles=['staff'])
def manage_tcertificate(request, certID=None):
    prev_certificates = None #previous certificates set to NONE
    #TODO once teacher is selected initialize prev_certificates
    pda_reports = None
    academic_class = None

    if certID: # if the certificate already exists
        tcertificate = TCertificate.objects.get(pk=certID)
        # previous certificates to be listed with current one
        prev_certificates = TCertificate.objects.filter(Q(teacher = tcertificate.teacher), ~Q(id = certID))
        #pda_reports and academic classes submitted for this certificate
        pda_reports = pdareports_for_certificate(tcertificate)
        academic_class = academic_classes_for_certificate(tcertificate)
    else:
        tcertificate = TCertificate() #initialize a new certificate

    tcertificate_form = TCertificateForm(instance=tcertificate) #Certificate form, defined in forms.py
    tendorsement_formset = TEndorsementFormSet(instance = tcertificate) # Endorsement formset, define in forms.py

    if request.method == "POST" and (request.POST.get('add_endorsement') or request.POST.get('submit_certificate')):
    # if the certificate is modified
        if certID:
            tcertificate_form = TCertificateForm(request.POST, instance=tcertificate)
        else:
            tcertificate_form = TCertificateForm(request.POST)

        tendorsement_formset = TEndorsementFormSet(request.POST)
        if tcertificate_form.is_valid(): #validate the certificate info
            tcertificate = tcertificate_form.save()
            tendorsement_formset = TEndorsementFormSet(request.POST, instance = tcertificate)

            if tendorsement_formset.is_valid(): #validate the endorsement info
                tendorsement_formset.save()
                if request.POST.get('add_endorsement'): #if more rows are needed for endorsements reload page
                    return redirect('manage_tcertificate', certID=tcertificate.id)
                if request.POST.get('submit_certificate'): #if certificate is submitted return to teacher_cert page
                    return redirect('manage_tcertificate',  certID=tcertificate.id )

    #certID is used in the template to reload page after previous certificates are archived
    context = dict( tcertificate_form = tcertificate_form, tendorsement_formset = tendorsement_formset,
                    prev_certificates = prev_certificates, certID=certID,
                    pda_reports=pda_reports, academic_class=academic_class)
    return render(request, 'teachercert/manage_tcertificate.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['staff'])
def archive_tcertificate(request, cID, certID):
    TCertificate.objects.filter(id=cID).update(archived=True)
    return redirect('manage_tcertificate', certID=certID)

@login_required(login_url='login')
@allowed_users(allowed_roles=['staff'])
def de_archive_tcertificate(request, cID, certID):
    TCertificate.objects.filter(id=cID).update(archived=False)
    return redirect('manage_tcertificate', certID=certID)

# principal's info page about teacher certification
#Todo to be worked on
@login_required(login_url='login')
@allowed_users(allowed_roles=['principal'])
def principal_teachercert(request):
    principal = request.user.teacher
    teachers = Teacher.objects.filter(school = principal.school, user__is_active = True)

    teachers_filter = TeacherFilter(request.GET, queryset=teachers)
    teachers = teachers_filter.qs

    context = dict(teachers=teachers, teachers_filter = teachers_filter)
    return render(request, 'teachercert/principal_teachercert.html', context)

# isei's info page about teacher certification
#Todo to be worked on
@login_required(login_url='login')
@allowed_users(allowed_roles=['staff'])
def isei_teachercert(request):
    teachers = Teacher.objects.filter(user__is_active = True)
    school_year = SchoolYear.objects.get(active_year = True)

    teachers_filter = TeacherFilter(request.GET, queryset=teachers)
    teachers = teachers_filter.qs

    tcertificates = TCertificate.objects.filter()
    tcertificates_filter = TCertificateFilter(request.GET, queryset=tcertificates)
    tcertificates = tcertificates_filter.qs

    context = dict(teachers=teachers, teachers_filter = teachers_filter, school_year=school_year,
                   tcertificates = tcertificates, tcertificates_filter= tcertificates_filter)
    return render(request, 'teachercert/isei_teachercert.html', context)
