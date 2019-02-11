from pathlib import Path
import shutil, os
from nodes.foundation import ProcessorNode
import logging


class FSCopyNode(ProcessorNode):

    def __init__(self, name="", props=None):
        self.name = name
        self._known_properties = {
            'dest': {
                'label': "Destination folder",
                'type': "folder",
                'required': True,
                'hint': 'The destination on the filesystem to copy the source to',
                'default': ''
            },
            'create_if_missing': {
                'type': "bool",
                'required': False,
                'hint': 'Creates the destination path if it is missing',
                'default': True
            },
        }
        self.children = []
        self._listeners = {}

        if props:
            self.properties = props
        else:
            self.properties = {}

    def _do_copy(self, src, dest):
        # check if src and dest exist
        src_p = Path(src)
        dest_p = Path(dest)

        if not src_p.exists():
            logging.error("Source does not exist")
            return False

        if src_p.is_file():
            if not dest_p.exists() and self.get_property("create_if_missing") is not True:
                logging.error("Destination does not exist")
                return False
            elif not dest_p.exists() and self.get_property("create_if_missing") is True:
                os.makedirs(dest_p.absolute())

            logging.info("Copying file {0} to {1}".format(src_p, dest_p))
            shutil.copy(str(src_p.absolute()), str(dest_p.absolute()))

        elif src_p.is_dir():
            if dest_p.exists():
                logging.error("Destination directory already exists")
                return False

            logging.info("Copying directory {0} to {1}".format(src_p, dest_p))
            shutil.copytree(str(src_p.absolute()), str(dest_p.absolute()))

        return True

    def run(self, stream):
        if not self.check_properties():
            logging.error("Cannot proceed because of previous errors")
            return False

        resources = stream.get_resources("FS:*")

        for res in resources:
            src = res.get_data()

            if len(src) > 1:
                logging.error("Received more than one FSObject. Please narrow down your src-filter.")
                return False

            src = src[0].getAbsolutePath()

            dest = self.get_property('dest')
            if self._do_copy(src, dest) is not True:
               return False

        return True
