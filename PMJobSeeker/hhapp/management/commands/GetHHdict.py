from django.core.management.base import BaseCommand, CommandError
from hhapp.models import Area, Schedule, JobType
from utils.hhutils import getAreas, getType, getSchedule

#This command will update main hh.ru dictionaries - Area and Schedule
#new data will be added, existing records will be updated. No deletion will take place

class Command(BaseCommand):
    help = "Update dictionaries from hh.ru"
    def handle(self, *args, **options):
        #Get Areas from hh.ru
        areas = getAreas()
        #print(areas)
        #store areas into DB
        for i in areas:
            #print(i[0], i[1], i[2])
            are = Area.objects.filter(code=i[0]).first()
            if are:
               are.name = i[1]
               are.parentCode = i[2]
               are.save()
            else:
               are = Area.objects.create(code=i[0], name=i[1], parentCode=i[2])

        # Get Type from hh.ru
        jobtypes = getType()
        #store job types into DB
        for i in jobtypes:
            jt = JobType.objects.filter(charid=i[0]).first()
            if jt:
               jt.name = i[1]
               jt.save()
            else:
               jt = JobType.objects.create(charid=i[0], name=i[1])

        # Get Schedules from hh.ru
        schedules = getSchedule()
        #store schedules into DB
        for i in schedules:
            sche = Schedule.objects.filter(charid=i[0]).first()
            if sche:
               sche.name = i[1]
               sche.save()
            else:
               sche = Schedule.objects.create(charid=i[0], name=i[1])

