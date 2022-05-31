import pandas as pd

def check_all(df):

    if check_headers(df) == True:
        return True

def check_headers(df):
    import_headers = list(df.columns.values)
    accepted_headers = ['references']
    print_headers = ', '.join(accepted_headers)
    if print_headers in import_headers:
        return True
