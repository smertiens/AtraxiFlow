from pathlib import Path
import shutil, os
from nodes.ProcessorNode import *


class FSCopyNode(ProcessorNode):
    _known_properties = {
        'dest': {
            'type': "string",
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

    def getNodeClass(self):
        return 'FSCopyNode'

    def _doCopy(self, src, dest):
        # check if src and dest exist
        src_p = Path(src)
        dest_p = Path(dest)

        if not src_p.exists():
            logging.error("Source does not exist")
            return False

        if src_p.is_file():
            if not dest_p.exists() and self.getProperty("create_if_missing") != True:
                logging.error("Destination does not exist")
                return False
            elif not dest_p.exists() and self.getProperty("create_if_missing") == True:
                os.makedirs(dest_p.absolute())

            logging.info("Copying file {0} to {1}".format(src_p, dest_p))
            shutil.copy(str(src_p.absolute()), str(dest_p.absolute()))

        elif src_p.is_dir():
            if dest_p.exists():
                logging.error("Destination directoy alread exists")
                return False

            logging.info("Copying directory {0} to {1}".format(src_p, dest_p))
            shutil.copytree(str(src_p.absolute()), str(dest_p.absolute()))

    def run(self, stream):
        self.mergeProperties()

        if self.hasErrors:
            logging.error("Cannot proceed because of previous errors")
            return False

        resources = stream.getResources("FS:*")

        for res in resources:
            src = res.getPath()
            dest = self.getProperty('dest')
            self._doCopy(src, dest)

        return True
