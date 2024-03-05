from django.db import models

class WordCount(BaseModel):
    word = models.ForeignKey('Word', on_delete=models.CASCADE)
    master_attribute = models.ForeignKey('MasterAttribute', on_delete=models.CASCADE)
    count = models.IntegerField()

