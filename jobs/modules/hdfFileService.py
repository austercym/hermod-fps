import os
from hdfs.ext.kerberos import KerberosClient


class HdfsFileService:

    def __init__(self, config, hdfs_url):
        self.config = config
        self.hdfs_client = KerberosClient(hdfs_url)

    def get_file_content(self, file_path):
        content = None

        with self.hdfs_client.read(file_path) as reader:
            content = reader.read()

        return content

    def download(self, hdfs_path, local_path):
        return self.hdfs_client.download(hdfs_path, local_path)

    def get_files(self, file_path):
        files = self.hdfs_client.list(file_path, status=True)
        return files

    def upload_file(self, file_path, dest_file_path):
        files_folder = dest_file_path
        self.hdfs_client.upload(files_folder, file_path)

    def get_file_status(self, file_path):
        return self.hdfs_client.status(file_path, strict=False)

    def archive(self, file_id, file_path):

        archive_folder = self.config["hdfs_archive_folder"]

        unique_filename = file_id + '.archive'
        archive_file_path = os.path.join(archive_folder, unique_filename)

        self.hdfs_client.rename(file_path, archive_file_path)
    
    def archive_file(self, file_id, file_path, archive_folder):

        unique_filename = file_id + '.archive'
        archive_file_path = os.path.join(archive_folder, unique_filename)

        self.hdfs_client.rename(file_path, archive_file_path)

    def set_error_file(self, file_id, file_path):
        archive_folder = self.config["hdfs_error_folder"]

        unique_filename = file_id + '.error'
        archive_file_path = os.path.join(archive_folder, unique_filename)

        self.hdfs_client.rename(file_path, archive_file_path)
