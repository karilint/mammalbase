from django.db import models
from mb.models import BaseModel, MasterAttribute

#class WordCount(BaseModel):
#    word = models.CharField(max_length=200)
#    master_attribute = models.ForeignKey(MasterAttribute, on_delete=models.CASCADE)
#    count = models.IntegerField()
    
#class ProbabilityTable(BaseModel):
#     word = models.ForeignKey(WordCount, on_delete=models.CASCADE)
#     master_attribute = models.ForeignKey(MasterAttribute, on_delete=models.CASCADE)
#     probability = models.IntegerField()
