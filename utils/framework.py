from utils.types.container import ContainerIndex, NotSupportedError, ContainerFile, ContainerFileList, FILETIME, Container
from utils.types.save import SaveFile
import datetime
import io
import re
import os
import shutil
import sys
import uuid
from typing import BinaryIO


class Framework():
    def __init__(self):
        self.container_location = "data/Packages/BethesdaSoftworks.ProjectGold_3275kfvn8vcwc"
        self.containers_index = None

        self.source_file = None
        self.source_path = ""


    def load_source_save(self, source_path):
        if not os.path.exists(source_path):
            print(f"Error: Source save file does not exist: {source_path}")
            exit(4)

        self.source_path = source_path
        self.source_file = open(source_path, "rb")

        self.parse_source_save(self.source_file)

        return self.source_file


    def parse_source_save(self, stream_binary):
        self.source_file = SaveFile.from_stream(stream_binary)
        stream_binary.close()

        self.source_file = self.source_file


    def load_containers_index(self):
        _p = r"%LOCALAPPDATA%\Packages\BethesdaSoftworks.ProjectGold_3275kfvn8vcwc"
        _p = self.container_location
        if not os.path.exists(_p):
            print("Error: Could not find the package path. Make sure you have Xbox Starfield installed.")
            exit(2)

        wgs_path = os.path.join(_p, "SystemAppData", "wgs")

        if not os.path.exists(wgs_path):
            print("Error: Could not find the wgs path. Make sure you have Xbox Starfield installed and saved at least once.")
            exit(3)

        container_index_path = os.path.join(wgs_path, "containers.index")
        container_index_file = open(container_index_path, "rb")

        try:
            container_index = ContainerIndex.from_stream(container_index_file)
        except NotSupportedError as e:
            print(f"Error: Detected unsupported container format, please report this issue: {e}")
            exit(3)

        container_index_file.close()
        self.containers_index = container_index

        return container_index


    def xgp2sfs(self, save):
        pass


    def backup(self):
        if not os.path.exists(self.container_location):
            print("Error: Could not find the package path. Make sure you have Xbox Starfield installed.")
            exit(2)

        container_backup_path = os.path.join(self.container_location, f"{self.container_location}.backup.{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}")
        shutil.copytree(self.container_location, container_backup_path)
        print(f"Created backup of container: {container_backup_path}")


    def sfs2xgp(self):
        if not self.source_file:
            print("Error: No source save file loaded")
            exit(5)

        if not self.containers_index:
            print("Error: No containers index loaded")
            exit(6)

        print("Loading SFS2XGP")

        # Check if already in containers
        for container in self.containers_index.containers:
            if container.container_name == self.source_file.filename:
                print("Save already in containers")
                return

        # Create save container
        print("Creating new container")
        files = [
            ContainerFile("BETHESDAPFH", uuid.uuid4(), self.source_file.header_bytes()),
        ]
        for index, chunk in enumerate(self.source_file.chunks):
            files.append(ContainerFile(f"P{index}P", uuid.uuid4(), chunk.data))
        container_file_list = ContainerFileList(seq=1, files=files)

        container_name = f"{self.source_file.filename}"
        container_uuid = uuid.uuid4()
        mtime = FILETIME.from_timestamp(os.path.getmtime(self.source_path))
        size = self.source_file.real_header_size + sum(chunk.size for chunk in self.source_file.chunks)
        container = Container(
            container_name=container_name,
            cloud_id="",
            seq=1,
            flag=5,
            container_uuid=container_uuid,
            mtime=mtime,
            size=size,
        )

        # Backup
        self.backup()

        # Update container.index
        self.containers_index.containers.append(container)
        self.containers_index.mtime = FILETIME.from_timestamp(datetime.datetime.now().timestamp())

        # Update container file list
        container_content_path = os.path.join(self.container_location, "SystemAppData", "wgs", container_uuid.bytes_le.hex().upper())
        os.makedirs(container_content_path, exist_ok=True)
        container_file_list.write_container(container_content_path)
        print(f"Wrote new container to {container_content_path}")

        self.containers_index.write_file(os.path.join(self.container_location, "SystemAppData", "wgs"))
        print("Updated container index")
