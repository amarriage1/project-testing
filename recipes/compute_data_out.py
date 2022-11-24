import dataiku
df = dataiku.Dataset("data").get_dataframe()
print(df.isin(["Infinity", "-Infinity"]).sum())

out_df = df.isin(["Infinity", "-Infinity"]).sum()

# Write recipe outputs
out = dataiku.Dataset("out")
out.write_with_schema(out_df)
