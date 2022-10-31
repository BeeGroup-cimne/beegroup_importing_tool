import os
import subprocess
from tempfile import NamedTemporaryFile


def put_file_to_hdfs(source_file_path, destination_file_path):
    subprocess.call(f"hdfs dfs -put -f {source_file_path} {destination_file_path}", shell=True)
    return destination_file_path + source_file_path.split('/')[-1]


def remove_file_from_hdfs(file_path):
    subprocess.call(f"hdfs dfs -rm {file_path}", shell=True)


def remove_file(file_path):
    os.remove(file_path)


def generate_input_tsv(data, values):
    with NamedTemporaryFile(delete=False, suffix=".tsv", mode='w') as file:
        for i in data:
            tsv_str = "\t".join([str(i[k]) for k in values]) + "\n"
            file.write(tsv_str)
    return file.name
