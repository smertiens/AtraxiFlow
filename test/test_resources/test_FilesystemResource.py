import unittest, logging, os
from resources.FilesystemResource import FilesystemResource

class test_FilesystemResource(unittest.TestCase):

    def setUp(self):
        logging.disable(logging.FATAL)
        self.testPath = os.path.join(os.getcwd(), "_temp")
        os.makedirs(os.path.join(self.testPath, "folder"))

        fp = open(os.path.join(self.testPath, "testfile.txt"), "w")
        fp.write("Hello world")
        fp.close()

    def tearDown(self):
        os.unlink(os.path.join(self.testPath, "testfile.txt"))
        os.rmdir(os.path.join(self.testPath, "folder"))
        os.rmdir(self.testPath)

    def test_resolve_wildcards(self):
        fs = FilesystemResource()
        fs.setProperty("sourcePattern", os.path.join(self.testPath, "*"))
        data = fs.getData()

        self.assertEqual(3, len(data))
        self.assertEqual(self.testPath, data[0].getAbsolutePath())
        self.assertEqual(os.path.join(self.testPath, "folder"), data[1].getAbsolutePath())
        self.assertEqual(os.path.join(self.testPath, "testfile.txt"), data[2].getAbsolutePath())


    def test_resolve_no_wildcards(self):
        fs = FilesystemResource()
        fs.setProperty("sourcePattern", self.testPath)
        data = fs.getData()

        self.assertEqual(1, len(data))
        self.assertEqual(self.testPath, data[0].getAbsolutePath())

if __name__ == '__main__':
    unittest.main()
