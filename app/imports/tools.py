import pandas as pd

def test_headers(csv_file):

    df = pd.read_csv(csv_file)
    for line in df:
        print(line)
    
    import_headers = list(df.columns.values)
    accepted_headers = ['references']
    print_headers = ', '.join(accepted_headers)

    if print_headers not in import_headers:
        return True
