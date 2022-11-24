import dataiku
df = dataiku.Dataset("data").get_dataframe()
print(df.isin(["Infinity", "-Infinity"]).sum())
