# -*- coding: utf-8 -*-
import dataiku
import pandas as pd, numpy as np
from dataiku import pandasutils as pdu

# Read recipe inputs
unlabeled_customers = dataiku.Dataset("unlabeled_customers")
unlabeled_customers_df = unlabeled_customers.get_dataframe()


# Compute recipe outputs from inputs
# TODO: Replace this part by your actual code that computes the output, as a Pandas dataframe
# NB: DSS also supports other kinds of APIs for reading and writing data. Please see doc.

Weee_df = unlabeled_customers_df # For this sample code, simply copy input to output

# Read recipe inputs
data = dataiku.Dataset("data")
data_df = data.get_dataframe()
#
path = dataiku.Folder("s3_out").get_path()
full_path = path + '/models/top2vec_model.csv'

csv = data_df.to_csv(full_path)

# Write recipe outputs
Weee = dataiku.Dataset("Weee")
Weee.write_with_schema(Weee_df)
