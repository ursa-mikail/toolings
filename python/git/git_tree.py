from git import Repo
import os

from collections import defaultdict

def print_tree(tree, indent=""):
    for blob in tree.blobs:
        print(indent + '|_ ' + blob.name)
    for subtree in tree.trees:
        print(indent + '|_ ' + subtree.name + "/")
        print_tree(subtree, indent + "  "*3)

def clone_and_print_tree(git_url, local_path="./repo"):
    # Clone repo if not already cloned
    if not os.path.exists(local_path):
        print(f"Cloning repository from {git_url} ...")
        Repo.clone_from(git_url, local_path)
    else:
        print(f"Using existing repository at {local_path}")

    repo = Repo(local_path)
    tree = repo.head.commit.tree
    print_tree(tree)


# Clone the repo
git_url = "https://github.com/ursa-mikail/data_format"
path = "/tmp/repo"

if not os.path.exists(path):
    Repo.clone_from(git_url, path)

repo = Repo(path)
tree = repo.head.commit.tree

# Print the tree
for item in tree.traverse():
    print(item.path)

print('==================================================================')
clone_and_print_tree(git_url)

"""
:
==================================================================
Using existing repository at ./repo
|_ readme.md
|_ CSV-to-HTML-table/
      |_ csv_to_html_table.py
      |_ online_html_edit_copy_paste_to_googledoc.png
      |_ readme.md
      |_ timetable.csv
      |_ timetable.html
|_ compression/
      |_ base64_zip_compression_ratio.py
|_ data_access/
      |_ data_segment_access.py
      |_ profile.json
      |_ readme.md
      |_ permit/
            |_ create_initial_permit.py
            |_ permit_expiration_check.py
            |_ readme.md
            |_ update_permit.py
|_ data_acquisition_and_format/
      |_ data_acquisition_and_format.py
      |_ readme.md
|_ data_form_and_format/
      |_ go/
            |_ data_format_conversion_and_file_conversion.go
      |_ python/
            |_ data_file_extraction_conversion.py
            |_ data_format_conversion.py
            |_ data_image_file_to_base64.py
|_ data_list_dict_csv/
      |_ data_list_dict_csv.py
      |_ readme.md
|_ fields_mapping/
      |_ fields_mapping.py
      |_ log_to_json.py
      |_ data/
            |_ mapping.json
            |_ source.json
            |_ target.json
            |_ logs/
                  |_ input.txt
                  |_ source.json
                  |_ target.json
|_ sql_csv_porting/
      |_ sql_csv_porting_example.py
      |_ sql_dump_all_example.py
      |_ sql_insert_new_data_example.py
      |_ sql_new_entry_example.py
      |_ sample_data/
            |_ california_housing_test.csv_2024-10-30_1437hr_03sec.zip
            |_ latitude_beyond_41.5_and_total_rooms_more_than_2800.csv
|_ sql_csv_yaml_json_porting/
      |_ 01_generate_data_to_csv.py
      |_ 02_csv_to_yaml_and_json.py
      |_ 03_csv_to_sql_and_display.py
      |_ 04_yaml_and_json_to_csv.py
      |_ readme.md
      |_ sample_data/
            |_ data/
                  |_ data.csv
                  |_ data.db
                  |_ data.json
                  |_ data.yaml
                  |_ json_to_csv.csv
                  |_ yaml_to_csv.csv
      |_ yaml_csv_sql_export_to_csv/
            |_ csv_sql_export_csv.png
            |_ readme.md
            |_ yaml_csv_sql_export_to_csv.py
|_ tabulated_data_markup_language_tdml_file_into_a_csv/
      |_ readme.md
      |_ method_01/
            |_ data.csv.png
            |_ data.txt.png
            |_ ensure_well_formatted_csv.py
            |_ tdml_file_into_csv.py
            |_ tdml_file_with_uri_into_csv.py
            |_ sample_data/
                  |_ data.txt
      |_ method_02/
            |_ tabulated_data_markup_language_tdml_file_into_a_csv.png
            |_ tabulated_data_markup_language_tdml_file_into_a_csv.py
|_ yaml_and_path_form/
      |_ yaml_and_path_data_weaving.py
      |_ yaml_and_path_data_weaving_single_char_node.py
      |_ yaml_path_node_name_finder.py
      |_ yaml_to_and_from_path.py
"""