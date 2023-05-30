import dataiku
import pandas as pd
from flask import request


# Example:
# As the Python webapp backend is a Flask app, refer to the Flask
# documentation for more information about how to adapt this
# example to your needs.
# From JavaScript, you can access the defined endpoints using
# getWebAppBackendUrl('first_api_call')

@app.route('/first_api_call')
def first_call():
    max_rows = request.args.get('max_rows') if 'max_rows' in request.args else 500

    mydataset = dataiku.Dataset("REPLACE_WITH_YOUR_DATASET_NAME")
    mydataset_df = mydataset.get_dataframe(sampling='head', limit=max_rows)

    # Pandas dataFrames are not directly JSON serializable, use to_json()
    data = mydataset_df.to_json()
    return json.dumps({"status": "ok", "data": data})

@app.route('/submit', methods=['POST'])

def submit():
    name = request.form.get('name')
    email = request.form.get('email')
    folder_id ='PauErurp'
    dataset_name = 'data'
    client = dataiku.api.client()
    folder = client.get_managed_folder(folder_id)
    dataset - folder.get_dataset(dataset_name)
    dataset.write.schema_from_dataframe(dataiku.Dataset("input").get_dataframe())
    dataset.write_dataframe(dataiku.Dataset("input").get_dataframe())
    
    return "Sign-off recorded"