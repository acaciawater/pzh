'''
Created on Dec 6, 2014

@author: theo
'''

from django.core.management.base import BaseCommand
from acacia.meetnet.models import Screen
from acacia.validation.models import BaseRule, Validation, RuleOrder

class Command(BaseCommand):
    args = ''
    help = 'Validatieregels aanmaken voor alle filters'

    def handle(self, *args, **options):
        rules = ['uitbijter']
        rules = BaseRule.objects.filter(name__in=rules)
        for s in Screen.objects.all():
            if s.has_data():
                for series in s.mloc.series_set.filter(name__endswith='COMP'):
                    val, _created = Validation.objects.get_or_create(series=series)
                    val.rules.clear()
                    val.reset()
                    for order,rule in enumerate(rules,start=1):
                        RuleOrder.objects.create(validation=val, rule=rule, order=order)