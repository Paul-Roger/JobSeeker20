from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError
#----from pycbrf import ExchangeRates
from hhapp.models import Schedule, JobType, Employer, Area, Keyword, Source, Currency, Skill, KeyWordSkill, Vacancy
from utils.hhutils import getAreas, getType, getSchedule, UpdateRates
from requests import get
import re
from collections import Counter
from pprint import pprint
import time

#This command will update main hh.ru dictionaries - Area and Schedule
#new data will be added, existing records will be updated. No deletion will take place

class Command(BaseCommand):
    help = "Update DB tables from hh.ru"

    def add_arguments(self, parser):
        parser.add_argument('vac', type = str, help='название вакансии')  # ← no nargs='+'
                # Опциональный аргумент
        parser.add_argument('-P', '--pag', type=int, help='items per page')
        parser.add_argument('-W', '--whr', type=str, help='whee')
    def handle(self, *args, **options):
        vacancy = options['vac']
        pages = options['pag']
        where = options['whr']
        if not pages:
            pages = 3
        if not where:
            where = 'ALL'
        UpdateRates() #just in case - get fresh currency rates
        res = start(vacancy = vacancy, pages = pages, where = where) # parsing
        print(res)
        add_words(res)
        add_skills(res)
        add_ws(res)


def parce(url, vacancy, pages='100', where='all'):
    # url = 'https://api.hh.ru/vacancies'
    # rate = ExchangeRates()
    curr_table = Currency.objects.all()
    #create list of currencies
    rate = {}
    for i in curr_table:
        rate[i.sym] = i.rate/i.nominal
    print(rate)

    vacancy = vacancy if where == 'all' else f'NAME: {vacancy}' if where == 'name' else f'COMPANY_NAME: {vacancy}'
    p = {'text': vacancy, 'per_page': '100'} #params for get request
    print(url, p)
    r = get(url=url, params=p, verify=False).json() #get data via Rest API
    count_pages = r['pages'] #total number result pages
    result = {
        'keywords': vacancy,
        'count': 0}
    print(result, "count_pages =", count_pages, "per_page =", r['per_page'])
    print('Max pages to go = ', int(pages))
    #pprint(r)
    sal = {'from': [], 'to': [], 'cur': []} #Salary list initialization
    skillis = []                            #Skills list initialization
    print('result[] before start pages loop')
    for page in range(count_pages): #for all pages in result
        if page > int(pages):
            break
        else:
            print(f"Обрабатывается страница {page}")
        p = {'text': vacancy,
             'per_page': '100',
             'page': page}
        ress = get(url=url, params=p, verify=False).json() #get one page
        all_count = len(ress['items']) #number of item on current page
        result['count'] += all_count  #looks like wrong, as we have already counted all items??
        print(f"result[] = {result['count']} page = {page}") #TBD
        for res in ress['items']:
            vacID = int(res['id'])  #vacancy id to check if exists
            #print("VacID = ", vacID)
            vc = Vacancy.objects.filter(vacid = vacID).first()
            if vc:
                continue
            time.sleep(3)
            #pprint(res)
            skills = set()                  #skills set init
            url1 = res['alternate_url']     #http url
            area_id = res['area']['id']                 #address
            area_name = res['area']['name']
            employer_id = res['employer'].get('id', 0)  #employer
            employer_name = res['employer']['name']
            employer_link = res['employer']['logo_urls']['original'] if res['employer'].get('logo_urls', 0) else None
            title = res['name']                         #vacancy name
            published = res['published_at']             #vacancy date
            type = res['employment']['name']                  #job type
            are = Area.objects.filter(name=area_name).first()   #area
            print("999999999999999999999999999999999999999999999999999999999999")
            if not are:
                are = Area.objects.filter(code=area_id).first()  # area
            if url.startswith('https://api.hh'):                #as in hh
                if are:
                    are.ind_hh = area_id
                    are.save()
                else:
                    are = Area.objects.create(name=area_name, ind_hh=area_id)
            else:                                               #as in zarplata.ru
                if are:
                    are.ind_zarp = area_id
                    are.save()
                else:
                    are = Area.objects.create(name=area_name, ind_zarp=area_id)
            print("EMPOLYER:", employer_name, employer_id, employer_link)
            #em = Employer.objects.get_or_create(name=employer_name, ident=employer_id, link=employer_link)[0]
            em = Employer.objects.filter(ident = employer_id).first() #name = employer_name,
            if not em:
                em = Employer.objects.create(name=employer_name, ident=employer_id, link=employer_link)
            t = JobType.objects.get_or_create(name=type)[0]
            w = Keyword.objects.filter(name=vacancy).first()
            if not w:
                w = Keyword.objects.create(name=vacancy, count=1, top=1, bottom=1)
            res_full = get(res['url'], verify=False).json()   #get individual vacancy
            #pprint(res_full)
            schedule = res_full["schedule"]['name']          #vacancy schedule
            sc = Schedule.objects.get_or_create(name=schedule)[0]
            snippet = res_full['description']
            pp_re = re.findall(r'\s[A-Za-z-?]+', snippet) #get list of non-russian words fromdescription
            its = set(x.strip(' -').lower() for x in pp_re) #remove spaces
            for sk in res_full['key_skills']:
                skillis.append(sk['name'].lower()) #skills in this parce
                skills.add(sk['name'].lower()) #sklls in this item
            for it in its:                          #add skills if they are not already mentioned in key_skills
                if not any(it in x for x in skills):
                    skillis.append(it)
            if res_full['salary']:                  #vacancy salary
                code = res_full['salary']['currency']
                if code == 'BYR':  #solve problem with Belorussian ruble
                    code = 'BYN'
                if rate.get(code, None) is None:
                    code = 'RUR'
                k = 1 if code == 'RUR' or code == 'RUB' else float(rate[code])
                salary_from = k * res_full['salary']['from'] if res['salary']['from'] else k * res_full['salary']['to']
                salary_to = k * res_full['salary']['to'] if res['salary']['to'] else k * res_full['salary']['from']
                #print('SALARY', code, salary_from, salary_to)
                sal['from'].append(round(salary_from))
                sal['to'].append(round(salary_to))
            else:
                salary_from, salary_to = 0, 0
            Vacancy.objects.create(vacid = vacID, pubdate=published, name=title, url=url1, keyword=w, area=are, schedule=sc,
                                   snippet=snippet, salaryFrom=salary_from, salaryTo=salary_to, employer=em,
                                   type=t)
    sk2 = Counter(skillis)                  #dict of skills
    #pprint(sal)
    up = sum(sal['from']) / len(sal['from'])
    down = sum(sal['to']) / len(sal['to'])
    result.update({'down': round(up, 2),
                   'up': round(down, 2)})
    add = []
    for name, count in sk2.most_common(5):
        add.append({'name': name,
                    'count': count,
                    'percent': round((count / result['count']) * 100, 2)})
    result['requirements'] = add
    print("********************** PARCING END ***********************")
    return result


def start(vacancy, pages='100', where='all'):
    res = parce(url='https://api.hh.ru/vacancies', vacancy=vacancy, pages=pages, where=where)
    #pprint(res)
    """    result = {'keywords': vacancy}
    res = (it for it in (sk1, sk2, sk3) if it)
    sk = {}
    for item in res:
        pprint(item)
        result['count'] = result.get('count', 0) + item.get('count',0)
        result['down'] = item['down'] if not result.get('down', None) else (result['down'] + item['down']) / 2
        result['up'] = item['up'] if not result.get('up', None) else (result['up'] + item['up']) / 2
        for it in item['requirements']:
            if sk.get(it['name'], {}):
                sk[it['name']] = {'count': sk[it['name']]['count'] + it['count'],
                                  'percent': round((sk[it['name']]['percent'] + it['percent']) / 2, 2)}
            else:
                sk[it['name']] = {'count': it['count'],
                                  'percent': it['percent']}
    #print(sk)
    result['requirements'] = sorted([{'name': it,
                                      'count': sk[it]['count'],
                                      'percent': sk[it]['percent']} for it in sk.keys() if it],
                                    key=lambda x: x['percent'],
                                    reverse=True)
    """
    return res


def add_words(res):
    try:
        #print(res['keywords'], res['up'], ['down'])
        obj = Keyword.objects.get(name=res['keywords'])
        #print("OBJect")
        #print(obj)
        if obj.count < res['count']:
            obj.count = res['count']
            obj.top = res['up']
            obj.bottom = res['down']
            obj.save()
            print('Edit')
        #else:
            #print('Not edit')
    except ObjectDoesNotExist:
        Keyword.objects.create(name=res['keywords'], count=res['count'], top=res['up'], bottom=res['down'])


def add_skills(res):
    print("ADD SKILLS")
    pprint(res)
    for item in res['requirements']:
        try:
            r = Skill.objects.get(name=item['name'])
            print('skill not added')
        except ObjectDoesNotExist:
            Skill.objects.create(name=item['name'])


def add_ws(res):
    word = Keyword.objects.get(name=res['keywords'])
    for item in res['requirements']:
        skill = Skill.objects.get(name=item['name'])
        print(word, skill)
        r = KeyWordSkill.objects.filter(keyword=word, skill=skill).first()
        if not r:
            KeyWordSkill.objects.create(keyword=word, skill=skill, count=item['count'], percent=item['percent'])
            print('ws done')
        elif word.count < res['count']:
            r.count = item['count']
            r.percent = item['percent']
            print('ws edit')
        else:
            print('ws not edit')
