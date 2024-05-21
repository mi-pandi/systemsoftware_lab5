class infoStatic:
    FS = None
    CWD = None
    BLOCK_SIZE = 128
    MAX_FILE_NAME_LENGTH = 20


class FS:
    def __init__(self, descriptors_max_num):
        self.descriptors_max_num = descriptors_max_num
        self.descriptors_num = 0
        self.descriptors = []
        self.descriptorsBitmap = [0 for i in range(descriptors_max_num)]
        self.Blocks = {}
        self.opened_files_num_descriptors = []
        self.opened_files = []
        rootDescriptor = Desc(0, 'directory', 0, '/')
        rootDescriptor.links_num -= 1
        self.descriptors.append(rootDescriptor)
        self.descriptors_num += 1
        self.descriptorsBitmap[0] = 1
        rootDirectory = Dir('/', rootDescriptor, None)
        self.root = rootDirectory
        infoStatic.CWD = rootDirectory


class Desc:
    def __init__(self, num, file_type, length, name, content=None):
        self.NUM = num
        self.TYPE = file_type
        self.links_num = 1
        self.length = length
        self.blocks = []
        self.name = name
        self.links = [self]
        if file_type == 'symlink':
            self.content = content

    def show_info(self):
        if self.TYPE == 'symlink':
            printname = f'{self.name}->{self.content}'
        else:
            printname = self.name
        print(
            '%10d  %10s  %10d  %10d  %10d  %s' %
            (self.NUM,
             self.TYPE,
             self.links_num,
             self.length,
             len(self.blocks),
             printname))


class Link:
    def __init__(self, descriptor, name):
        descriptor.links_num += 1
        self.descriptor = descriptor
        self.name = name

    def show_info(self):
        print('%10d  %10s  %10d  %10d  %10d  %s' %
              (self.descriptor.NUM,
               self.descriptor.TYPE,
               self.descriptor.links_num,
               self.descriptor.length,
               len(self.descriptor.blocks),
               f'{self.name}->{self.descriptor.name}'))


class FileDesc:
    def __init__(self, descriptor):
        if isinstance(descriptor, Link):
            self.descriptor = descriptor.descriptor
        else:
            self.descriptor = descriptor
        num_desc = 0
        while num_desc in infoStatic.FS.opened_files_num_descriptors:
            num_desc += 1
        infoStatic.FS.opened_files_num_descriptors.append(num_desc)
        self.num_descriptor = num_desc
        self.offset = 0


class Sym:
    def __init__(self, name: str, descriptor: Desc, parent, content):
        self.name = name
        self.descriptor = descriptor
        self.parent = parent
        self.content = content


class Dir:
    def __init__(self, name: str, descriptor: Desc, parent):
        self.name = name
        if parent is None:
            self.parent = self
        else:
            self.parent = parent
        self.descriptor = descriptor
        self.child_descriptors = []
        self.child_directories = []
        if parent is None:
            parentLink = Link(descriptor, '..')
        else:
            parentLink = Link(parent.descriptor, '..')
        self.child_descriptors.append(parentLink)
        self.child_descriptors.append(Link(descriptor, '.'))