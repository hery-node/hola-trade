import pandas as pd

# Creating a DataFrame from a dictionary
data = {'Name': ['Alice', 'Bob', 'Charlie', 'David'],
        'Age': [25, 30, 35, 40],
        'City': ['New York', 'Los Angeles', 'Chicago', 'Houston']}

df = pd.DataFrame(data)
print("Original DataFrame:")
print(df)
print()

# Accessing specific columns
print("Accessing specific columns:")
print(df['Age'].iloc[-1])
print(df['Age'].iloc[-2])
print(len(df["Age"]))
