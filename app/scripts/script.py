from django.shortcuts import get_object_or_404
from mb.models import FoodItem, ViewProximateAnalysisTable
from itis.models import TaxonomicUnits
def run():
    food_items = FoodItem.objects.all().filter(tsn__gt=0).filter(pa_tsn__isnull=True).order_by('-tsn')
    for x in food_items:
        food_item = get_object_or_404(FoodItem, pk=x.id)
        tsn_hierarchy = food_item.tsn.hierarchy_string.split("-")
        i=len(tsn_hierarchy)-1
        while(i>=0):
            print(tsn_hierarchy[i], food_item.part.caption)
            part=food_item.part.caption
            if part=='CARRION':
                part='WHOLE'
            pa=ViewProximateAnalysisTable.objects.filter(tsn__hierarchy_string__endswith=tsn_hierarchy[i])
            if len(pa)==1:
                break
            i=i-1
        if pa.exists():
            proximate_analysis=pa.all()[0]
            food_item.pa_tsn=pa.all()[0].tsn
            food_item.save()
        else:
            proximate_analysis=pa.none()

        print(food_item, proximate_analysis.tsn.tsn, proximate_analysis.tsn.completename)
