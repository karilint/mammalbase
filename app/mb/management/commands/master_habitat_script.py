from io import StringIO
import os
import pandas as pd
from mb.models.habitat_models import MasterHabitat
from imports.importers.base_importer import BaseImporter
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    def __init__(self):
        self.importer = BaseImporter()
        self.csv_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'habitat_csv')
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
        self.user = User.objects.get(username=username)
        
    def handle(self, *args, **options):
        print("Adding Olson biomes...")
        self.add_olson_biomes()
        print("Adding WWF biomes...")
        self.add_wwf_biomes()
        print("Adding Holdridge biomes...")
        self.add_holdridge_biomes()

        print("Master Habitats created successfully")
        
        
    def add_olson_biomes(self):
        # Correct reference: Olson, J S, Watts, J A, and Allison, L J. Carbon in live vegetation of major world ecosystems. United States: N. p., 1983. Web.
        # Temporarily using same reference as WWF
        olson_reference = self.importer.get_or_create_master_reference(citation="Olson, D. M., Dinerstein, E., Wikramanayake, E. D., Burgess, N. D., Powell, G. V. N., Underwood, E. C., D'Amico, J. A., Itoua, I., Strand, H. E., Morrison, J. C., Loucks, C. J., Allnutt, T. F., Ricketts, T. H., Kura, Y., Lamoreux, J. F., Wettengel, W. W., Hedao, P., Kassem, K. R. 2001. Terrestrial ecoregions of the world: a new map of life on Earth. Bioscience 51(11):933-938.", author=self.user)
        olson_path = os.path.join(self.csv_dir, "biomes_olson_1983.csv")
        olson_df = pd.read_csv(olson_path)

        habitats = {}

        for index, row in olson_df.iterrows():
            prev_habitat = None
            for i in range(len(row)-1):
                name = row.iloc[i]
                header = olson_df.columns[i]
                if pd.notna(name) and name.strip():
                    if name not in habitats:
                        if i == len(row)-2:
                            eco_code = row.iloc[-1]
                        else:
                            eco_code = None
                        key = (name, eco_code)
                        if key not in habitats:
                            habitat = MasterHabitat.objects.create(
                                name=name,
                                reference=olson_reference,
                                parent=prev_habitat,
                                code=eco_code,
                                group=header
                            )
                            habitats[key] = habitat
                        else:
                            habitat = habitats[key]

                    prev_habitat = habitat
                else:
                    prev_habitat = None
    
    def add_wwf_biomes(self):
        wwf_reference = self.importer.get_or_create_master_reference(citation="Olson, D. M., Dinerstein, E., Wikramanayake, E. D., Burgess, N. D., Powell, G. V. N., Underwood, E. C., D'Amico, J. A., Itoua, I., Strand, H. E., Morrison, J. C., Loucks, C. J., Allnutt, T. F., Ricketts, T. H., Kura, Y., Lamoreux, J. F., Wettengel, W. W., Hedao, P., Kassem, K. R. 2001. Terrestrial ecoregions of the world: a new map of life on Earth. Bioscience 51(11):933-938.", author=self.user)
        wwf_path = os.path.join(self.csv_dir, "biomes_wwf.csv")
        wwf_df = pd.read_csv(wwf_path)

        for index, row in wwf_df.iterrows():
            biome_code = row.iloc[0]
            name = row.iloc[1]

            habitat, created = MasterHabitat.objects.get_or_create(
                        reference=wwf_reference,
                        code=biome_code,
                        name=name,
                    )

            if created:
                habitat.save()
    
    def add_holdridge_biomes(self):
        holdridge_reference = self.importer.get_or_create_master_reference(citation="Holdridge, L.R. (1947). Determination of world plant formations from simple climatic data. Science. 105 (2727): 367–8.", author=self.user)       
        holdridge_path = os.path.join(self.csv_dir, "biomes_holdridge.csv")
        holdridge_df = pd.read_csv(holdridge_path)

        for index, row in holdridge_df.iterrows():
            iiasa_code = row.iloc[0]
            name = row.iloc[1]

            habitat, created = MasterHabitat.objects.get_or_create(
                        reference=holdridge_reference,
                        code=iiasa_code,
                        name=name,
                    )

            if created:
                habitat.save()
