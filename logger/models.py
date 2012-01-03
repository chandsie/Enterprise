from django.contrib.auth.models import User
from django.db import models
from datetime import datetime

class Log(models.Model):
    name = models.ForeignKey(User)
    date = models.DateField()
    time_in = models.TimeField(default=lambda: datetime.time(datetime.now()))
    time_out = models.TimeField(blank=True, null=True)
    
    def __unicode__ (self):
        if self.time_out is not None:
            time_out = self.time_out.strftime("%H%M")
        else:
            time_out = "Blank"
        return self.name.username + " " + str(self.date) + " " + self.time_in.strftime("%H%M") + " " + time_out

