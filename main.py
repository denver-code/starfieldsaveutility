import datetime
import io
import re
import os
import shutil
import sys
import uuid
from typing import BinaryIO

from utils.types.container import ContainerIndex, NotSupportedError, ContainerFile, ContainerFileList, FILETIME, Container
from utils.types.save import SaveFile
from utils.framework import Framework

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <save_file>")
        exit(1)

    source_save_path = sys.argv[1]

    framework = Framework()

    # Load source save
    framework.load_source_save(source_save_path)
    #

    framework.load_containers_index()
    framework.sfs2xgp()

if __name__ == '__main__':
    main()
