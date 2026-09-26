import pandas as pd

# Load TSV file
df = pd.read_csv("train/train_ground_truth.tsv", sep="\t")

# First 5 rows
print(df.head())

print("Shape:", df.shape)