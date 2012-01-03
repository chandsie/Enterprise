from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from Enterprise.logger.views import login_page, userReport_page, dateReport_page, \
    addUser_page, passUpdate_page, success_page, passReset_page, rangeReport_page, \
    adminLogin_page, adminLogout_page
from django.contrib.auth.decorators import login_required

urlpatterns = patterns('',

#    Employee Interface

    (r'^$', login_page),
    #(r'success/^$', success_page),
    (r'^update/$', passUpdate_page),
    (r'^update/success/$', direct_to_template, {'template' : 'passUpdateSuccess.html'}),
    
    
#    Administrator Interface
    (r'^admin/$', login_required(direct_to_template), {'template' : 'admin/adminMain.html'}),
    (r'^admin/login/$', adminLogin_page),
    (r'^admin/login/success/$', direct_to_template, {'template' : 'admin/adminSuccess.html'}),
    (r'^admin/logout/$', adminLogout_page),
    
    # User Management
    (r'^admin/add/$', addUser_page),
    #(r'^admin/add/success/$', direct_to_template),
    #(r'^admin/reset/$', passReset_page), 
    
    # Reports
    (r'^report/user/(\w+)/$', userReport_page),
    (r'^report/date/([\d]{4}-[\d]{1,2}-[\d]{1,2})/$', dateReport_page),
    (r'^report/date/range/$', rangeReport_page),
      
    
)
