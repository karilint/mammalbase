import pandas as pd
from mb.models.habitat_models import MasterHabitat


def create_habitat_models():
    df = pd.read_csv("biomes_olson_1983.csv")
        
    for index, row in df.iterrows():
        eco_code = row['eco_code']
        other_columns = [col for col in df.columns if col != 'eco_code']

        name = ', '.join(row[col] for col in other_columns)

        habitat = MasterHabitat(eco_code=eco_code, name=name)
        habitat.save()
        
if __name__ == "__main__":
    create_habitat_models()