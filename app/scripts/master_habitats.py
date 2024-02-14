#script_path = 'scripts/master_habitats.py'
#exec(open(script_path).read(), {'__file__': script_path})

import os
import pandas as pd
from mb.models.habitat_models import MasterHabitat
from imports.importers.base_importer import BaseImporter
from django.contrib.auth.models import User

importer = BaseImporter()

username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
user = User.objects.get(username=username)

csv_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'habitat_csv')

olson_reference = importer.get_or_create_master_reference(citation="Olson, D. M., Dinerstein, E., Wikramanayake, E. D., Burgess, N. D., Powell, G. V. N., Underwood, E. C., D'Amico, J. A., Itoua, I., Strand, H. E., Morrison, J. C., Loucks, C. J., Allnutt, T. F., Ricketts, T. H., Kura, Y., Lamoreux, J. F., Wettengel, W. W., Hedao, P., Kassem, K. R. 2001. Terrestrial ecoregions of the world: a new map of life on Earth. Bioscience 51(11):933-938.", author=user)
olson_path = os.path.join(csv_dir, "biomes_olson_1983.csv")
olson_df = pd.read_csv(olson_path)

for index, row in olson_df.iterrows():
    prev_habitat = None
    for i in range(len(row)-1):
        name = row.iloc[i]
        eco_code = row.iloc[-1]
        if pd.notna(name) and name.strip():
            habitat, created = MasterHabitat.objects.get_or_create(
                reference=olson_reference,
                eco_code=eco_code,
                name=name,
            )

        if created:
            habitat.parent = prev_habitat
            habitat.save()

        prev_habitat = habitat

wwf_path = os.path.join(csv_dir, "biomes_wwf.csv")
wwf_df = pd.read_csv(wwf_path)

for index, row in wwf_df.iterrows():
    biome_code = row.iloc[0]
    name = row.iloc[1]

    habitat, created = MasterHabitat.objects.get_or_create(
                reference=olson_reference,
                biome_code=biome_code,
                name=name,
            )

    if created:
        habitat.save()

holdridge_reference = importer.get_or_create_master_reference(citation="Holdridge, L.R. (1947). Determination of world plant formations from simple climatic data. Science. 105 (2727): 367–8.", author=user)       
holdridge_path = os.path.join(csv_dir, "biomes_holdridge.csv")
holdridge_df = pd.read_csv(holdridge_path)

for index, row in holdridge_df.iterrows():
    iiasa_code = row.iloc[0]
    name = row.iloc[1]

    habitat, created = MasterHabitat.objects.get_or_create(
                reference=holdridge_reference,
                iiasa_code=iiasa_code,
                name=name,
            )

    if created:
        habitat.save()
