from django.contrib import admin
from .models import Employer, Area, JobType, Schedule, Keyword, Source, Currency, Skill, KeyWordSkill, Vacancy

# Register your models here.
admin.site.register(Employer)
admin.site.register(Area)
admin.site.register(JobType)    #getType()
admin.site.register(Schedule)   #getSchedule()
admin.site.register(Keyword)
admin.site.register(Source)
admin.site.register(Currency)
admin.site.register(Skill)
admin.site.register(KeyWordSkill)
admin.site.register(Vacancy)