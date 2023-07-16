from django.db import models

# Create your models here.
class Employer(models.Model):
    name = models.CharField(max_length=32)
    ident = models.IntegerField(null=True, unique=True)
    link = models.URLField(max_length=64, blank=True, null=True)

    def __str__(self):
        return self.name
    #int, bool, float, smallint, deciaml
    #python manage.py makemigration
    #python manage.py migrate


class Area(models.Model):
    name = models.CharField(max_length=64, unique=False, verbose_name='Region')
    code = models.DecimalField(max_digits=5, decimal_places=0, unique=True, verbose_name='RgionCode')
    parentCode = models.DecimalField(max_digits=5, decimal_places=0, verbose_name='ParrentCode')
    def __str__(self):
        return self.name


class JobType(models.Model): #employment
    charid = models.CharField(max_length=16, unique=True, verbose_name='Type ID')
    name = models.CharField(max_length=32, unique=True, verbose_name='Type')
    def __str__(self):
        return self.name

class Schedule(models.Model):
    charid = models.CharField(max_length=16, unique=True, verbose_name='Schedule ID')
    name = models.CharField(max_length=32, unique=True, verbose_name='Schedule')

    def __str__(self):
        return self.name


class Keyword(models.Model):
    name = models.CharField(max_length=32, unique=True, verbose_name='KeyWord')
    count = models.PositiveIntegerField(verbose_name='Quantity')
    top = models.FloatField(verbose_name='Upper Limit')
    bottom = models.FloatField(verbose_name='Lower Limit')

    def __str__(self):
        return self.name


class Source(models.Model): #source of vacancy
    name = models.CharField(max_length=32, unique=True, verbose_name='Source')
    url = models.URLField()
    lastRefresh = models.DateTimeField(verbose_name='Last refreshed')
    lastCnt = models.BigIntegerField(verbose_name='last added')

    def __str__(self):
        return self.name


class Currency(models.Model):
    name = models.CharField(max_length=32, unique=True, verbose_name='Currency')
    sym = models.CharField(max_length=4, unique=True, blank=False)
    code = models.DecimalField(max_digits=3, decimal_places=0,verbose_name='CurrencyCode')
    cbid = models.CharField(max_length=8)
    rate = models.FloatField()
    nominal = models.IntegerField(blank=False)

    def __str__(self):
        return self.sym


class Skill(models.Model):
    name = models.CharField(max_length=32, unique=True, verbose_name='Skill')

    def __str__(self):
        return self.name


class KeyWordSkill(models.Model):
    keyword = models.ForeignKey(Keyword, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    count = models.FloatField()
    percent = models.FloatField()


class Vacancy(models.Model):
    vacid = models.BigIntegerField(default=0)
    pubdate = models.DateTimeField()
    name = models.CharField(max_length=64)
    url = models.URLField()
    keyword = models.ForeignKey(Keyword, on_delete=models.CASCADE)
    area = models.ForeignKey(Area, on_delete=models.CASCADE)
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    snippet = models.TextField()
    salaryFrom = models.FloatField(default=0)
    salaryTo = models.FloatField(default=0)
    employer = models.ForeignKey(Employer, on_delete=models.CASCADE)
    type = models.ForeignKey(JobType, on_delete=models.CASCADE)

    def __str__(self):
        return self.name