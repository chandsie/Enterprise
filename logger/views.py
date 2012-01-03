from datetime import datetime, time, timedelta, date
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render_to_response, get_object_or_404, \
    get_list_or_404, redirect
from django.template.context import RequestContext
from Enterprise.logger.forms import LogForm, RegistrationForm, PasswordUpdateForm, \
    RangeReportForm, AdminLoginForm
from Enterprise.logger.models import Log
import random
import string

def _getDiff(end, begin):
    return datetime.combine(date.today(), end) - datetime.combine(date.today(), begin)

def login_page(request): 
    if request.method == 'POST':
#        import pdb; pdb.set_trace()
        form = LogForm(request.POST)
        if form.is_valid():
            user = User.objects.get(username=form.cleaned_data['username'])
            log, created = Log.objects.get_or_create(name=user, date=datetime.date(datetime.now()))
            name = user.first_name + " " + user.last_name
            hours, minutes = 0,0
            if created:
                fileName = "loginSuccess.html"
                time = log.time_in.strftime("%I:%M %p")
            else:
                if not log.time_out:
                    fileName = "logoutSuccess.html"
                    log.time_out = datetime.time(datetime.now())
                    log.save()
                else:
                    fileName = "logError.html"
                time = log.time_out.strftime("%I:%M %p")
                hours, minutes = _getHoursAndMinutes(log)
            return render_to_response(fileName, RequestContext(request, {
                                                                     'name' : name,
                                                                     'time' : time,
                                                                     'hours' : hours,
                                                                     'minutes' : minutes
                                                                     }))                               
    else:
        form = LogForm()
    return render_to_response('main.html', RequestContext(request, {'form' : form}))

def success_page():
    pass

def passUpdate_page(request):
    if request.method == 'POST':
        form = PasswordUpdateForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['username']
            user.set_password(form.cleaned_data['newPassword'])
            user.save()
            return redirect('success/')
    else:
        form = PasswordUpdateForm()
    
    return render_to_response('passUpdate.html', RequestContext(request, {'form' : form}))

def adminLogin_page(request):
    if request.method == 'POST':
        form = AdminLoginForm(request.POST)
        if form.is_valid():
            admin = authenticate(username='admin', password=form.cleaned_data['password'])
            login(request, admin)
            return redirect('success/')    
    else:
        form = AdminLoginForm()
    return render_to_response('admin/adminLogin.html', RequestContext(request, {'form' : form}))

def adminLogout_page(request):
    logout(request)
    return redirect('/log/')

@login_required
def addUser_page(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            fname = form.cleaned_data['firstName'].strip()
            lname = form.cleaned_data['lastName'].strip()
            user = User(username=fname.lower()+'_'+lname.lower(), first_name=fname, last_name=lname)
            s = 'abcdefghijklmnopqrstuvwxyz0123456789'
            password = ''.join(random.sample(s, 10))
            user.set_password(password)
            user.save()
            return render_to_response('admin/addUserSuccess.html', RequestContext(request, {'pass' : password}))
    else:
        form = RegistrationForm()
    return render_to_response('admin/addUser.html', RequestContext(request, {'form' : form}))

def passReset_page(request):
    pass

def _getHoursAndMinutes(log):
#    import pdb; pdb.set_trace();
    hours = 0
    minutes = 0
    if not log.time_out:
        if log.date == datetime.today().date():
            return (0,0);
        if log.time_in > time(17,0): 
            log.time_out = log.time_in + time(0,1)
        else:
            log.time_out = time(hour = 17)
        log.save()
    
    deltas = str(_getDiff(log.time_out, log.time_in)).split(":")
    hours += int(deltas[0])
    minutes += int(deltas[1])
    if deltas[2] > 30:
        minutes += 1
    if(minutes >= 60):
        hours += minutes/60
        minutes = minutes%60
        
    return (hours, minutes)

@login_required
def dateReport_page(request, rawDate):
#    import pdb; pdb.set_trace()
    date = datetime.strptime(rawDate, "%Y-%m-%d").date()
    logs = get_list_or_404(Log, date = date)
    employees = 0
    times = []
    for log in logs:
        employees += 1
        hours, minutes = _getHoursAndMinutes(log)
        times.append(str(hours) + ":" + str(minutes))
    
    variables = {'date':date,
                 'logs':zip(logs,times),
                 'employees':employees
                 }
    return render_to_response('admin/dateReport.html', RequestContext(request, variables))

@login_required                             
def userReport_page(request, user):
#    import pdb; pdb.set_trace()
    person = get_object_or_404(User, username=user)
    logs = get_list_or_404(Log, name = person)
    name = person.first_name + " " + person.last_name
    
    hours = 0
    minutes = 0
    days = 0
    times = []
    for log in logs:
        days += 1
        thours, tminutes = _getHoursAndMinutes(log)
        times.append(str(thours) + ':' + str(tminutes))
        hours = hours + thours
        minutes = minutes + tminutes
    
    if(minutes >= 60):
        hours += minutes/60
        minutes = minutes%60
        
    variables = {'name':name, 
                 'days':days,
                 'hours':hours,
                 'minutes':minutes,
                 'logs':zip(logs, times)}
    return render_to_response('admin/userReport.html', RequestContext(request, variables))            

@login_required
def rangeReport_page(request):
#    import pdb; pdb.set_trace()
    if request.GET:
        form = RangeReportForm(request.GET)
        if form.is_valid():
            begin = form.cleaned_data['begin']
            end = form.cleaned_data['end']
            totalDays = (end - begin).days
            
            logs = []
            users = User.objects.all().exclude(username=u'admin').order_by('last_name')
            
            for user in users:
                userLogs = Log.objects.filter(name=user, date__range=(begin, end))
                tHours, tMinutes = 0,0
                days = 0
                for log in userLogs:
                    h, m = _getHoursAndMinutes(log)
                    tHours += h
                    tMinutes += m
                    days = days + 1
                if tMinutes >= 60:
                    tHours += tMinutes/60
                    tMinutes = tMinutes%60
                totalTime = str(tHours) + ":" + str(tMinutes)
                absents = totalDays - days
                if absents < 0:
                    absents = 0
                logs.append([user, totalTime, days, absents, ''])
                
                
            variables = {
                         'begin' : begin,
                         'end' : end,
                         'days' : totalDays,
                         'logs' : logs
                         }  
            return render_to_response('admin/rangeReport.html', RequestContext(request, variables))
    else:
        form = RangeReportForm()
    
    return render_to_response('admin/rangeRequest.html', RequestContext(request, {'form':form}))


#        daterange = [begin + timedelta(n) for n in range((end - begin).days)]
#        
#        logs = []
#        users = User.objects.all().order_by('last_name')
#        for user in users:
#            userLog = [user.first_name + ' ' + user.last_name]
#            for single_date in daterange:
#                try:
#                    record = Log.objects.get(date=single_date,name=user)
#                    if record.time_out is None:
#                        userLog.append('Still Working!')
#                    else:
#                        userLog.append(':'.join((str(_getDiff(record.time_out, record.time_in).split(':'))[:2]))
#                except:
#                    userLog.append('Absent')                        
#                                       
#            logs.append(userLog) 
#
#        title = 'From: ' + str(begin) + ' To: ' + str(end)
#                    
#        response = HttpResponse(mimetype='text/csv')
#        response['Content-Disposition'] = 'attachment; filename=Report ' + title + '.csv'
#        
#        daterange.insert(0, '')
#        writer = csv.writer(response)
#        writer.writerow(daterange)
#        for log in logs:
#            writer.writerow(log)
#        
#        return response
