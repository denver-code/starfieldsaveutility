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

    def xgp2sfs(self, save):
        pass

    def sfs2xgp(self):
        if not self.source_file:
            print("Error: No source save file loaded")
            exit(5)
            return

        print("Loading SFS2XGP")
        # Check if already in containers

        # Create save container
        print("Creating new container")
        files = [
            ContainerFile("BETHESDAPFH", uuid.uuid4(), self.source_file.header_bytes()),
        ]
        for index, chunk in enumerate(self.source_file.chunks):
            files.append(ContainerFile(f"P{index}P", uuid.uuid4(), chunk.data))
        container_file_list = ContainerFileList(seq=1, files=files)

        # 4.2 create container index entry
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


        # Update container.index

        # Update container file list
        container_content_path = os.path.join("./export/", container_uuid.bytes_le.hex().upper())
        os.makedirs(container_content_path, exist_ok=True)
        container_file_list.write_container(container_content_path)
        print(f"Wrote new container to {container_content_path}")
