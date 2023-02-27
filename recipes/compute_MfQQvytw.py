# -*- coding: utf-8 -*-
import dataiku
import pandas as pd, numpy as np
from dataiku import pandasutils as pdu

# Read recipe inputs
data = dataiku.Dataset("data")
data_df = data.get_dataframe()
#
path = dataiku.Folder("s3_out").get_path()
full_path = path + 'top2vec_model.csv'

csv = data_df.to_csv(full_path)

