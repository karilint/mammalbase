import csv
import pandas as pd

list1 = []
list2 = []

df = pd.read_csv("biomes_olson_1983.csv")
for column_name in df.columns:
    column_values = [column_name] + list(df[column_name])
    
    if column_values[0] == "eco_code":
        list2.extend(df[column_values])
    
    for value in column_values:
        if value != 
        
        print(value)