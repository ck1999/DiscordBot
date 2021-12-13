import pandas as pd

df = pd.read_csv('data.csv')
arr = set()
for i in df['film_name']:
    arr.add(i.lower())
print(len(arr))