from django.core.management.base import BaseCommand, CommandError
from utils.hhutils import UpdateRates

class Command(BaseCommand):
    help = "Fill up currency rates"
    def handle(self, *args, **options):
        #Get currency data from CBR.ru
        UpdateRates()

