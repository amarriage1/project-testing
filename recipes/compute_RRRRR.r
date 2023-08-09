library(dataiku)

# Recipe inputs
metrics <- dkuReadDataset("metrics", samplingMethod="head", nbRows=100000)

# Compute recipe outputs from inputs
# TODO: Replace this part by your actual code that computes the output, as a R dataframe or data table
RRRRR <- metrics # For this sample code, simply copy input to output


# Recipe outputs
dkuWriteDataset(RRRRR,"RRRRR")
