import dataiku
import os

handle = dataiku.Folder('pretrained_models')
folder_name = 'sentence-transformers_all-MiniLM-L6-v2'
original_folder_path = os.path.join(os.getcwd(), 'cache/sentence-transformers_all-MiniLM-L6-v2')

for root, _, files in os.walk(original_folder_path):
    for file in files:
        original_file_path = os.path.join(root, file)
		# Find the index of the substring
        index = original_file_path.index(folder_name)
        # Get the substring and everything after it
        mgmt_file_path = original_file_path[index:]
        
        handle.upload_file(mgmt_file_path, original_file_path)