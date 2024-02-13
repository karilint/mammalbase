#script_path = 'scripts/master_habitats.py'
#exec(open(script_path).read(), {'__file__': script_path})

import os
import pandas as pd
from mb.models.habitat_models import MasterHabitat
from imports.importers.base_importer import BaseImporter
from django.contrib.auth.models import User


username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')

user = User.objects.get(username=username)
importer = BaseImporter()
reference = importer.get_or_create_master_reference(citation="Olson, D. M., Dinerstein, E., Wikramanayake, E. D., Burgess, N. D., Powell, G. V. N., Underwood, E. C., D'Amico, J. A., Itoua, I., Strand, H. E., Morrison, J. C., Loucks, C. J., Allnutt, T. F., Ricketts, T. H., Kura, Y., Lamoreux, J. F., Wettengel, W. W., Hedao, P., Kassem, K. R. 2001. Terrestrial ecoregions of the world: a new map of life on Earth. Bioscience 51(11):933-938.", author=user)

script_dir = os.path.dirname(os.path.realpath(__file__))
csv_path = os.path.join(script_dir, "biomes_olson_1983.csv")

df = pd.read_csv(csv_path)

for index, row in df.iterrows():
    prev_habitat = None
    for i in range(len(row)-1):
        name = row.iloc[i]
        eco_code = row.iloc[-1]
        if pd.notna(name) and name.strip():
            habitat, created = MasterHabitat.objects.get_or_create(
                reference=reference, 
                eco_code=eco_code, 
                name=name, 
            )
            
        if created:
            habitat.parent = prev_habitat
            habitat.save()
        elif habitat.parent is None and prev_habitat is not None:
            habitat.parent = prev_habitat
            habitat.save()
        
            
        prev_habitat = habitat
        
    #for col in other_columns:
    #    print(row[col])

    #habitat = MasterHabitat(reference=reference,eco_code=eco_code, name=name)
    #habitat.save()