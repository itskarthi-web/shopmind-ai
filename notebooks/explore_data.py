import pandas as pd

# Use the correct file!
df = pd.read_csv('data/raw/Amazon-Products.csv', on_bad_lines='skip')

print("=" * 50)
print(f"Total products : {len(df)}")
print(f"Total columns  : {len(df.columns)}")

print("\nColumns:")
for col in df.columns:
    print(f"  → {col}")

print("\nFirst 2 rows:")
print(df.head(2).to_string())

print("\nMissing values:")
print(df.isnull().sum())

print("\nSample categories:")
if 'category' in df.columns:
    print(df['category'].value_counts().head(10))
elif 'main_category' in df.columns:
    print(df['main_category'].value_counts().head(10))