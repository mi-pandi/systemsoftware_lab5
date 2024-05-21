from fs_classes import *


def print_error(*message):
    print('\033[91m', *message, '\033[0m')


def print_ok(*message):
    print('\033[92m', *message, '\033[0m')


def print_descriptor_header():
    print('%10s  %10s  %10s  %10s  %10s  %s' % ('№', 'type', 'links', 'length', 'blocks', 'name'))


def check_fs():
    if infoStatic.FS is None:
        print_error('The file system is not initialised')
        return 1
    return 0


def register_descriptor(descriptor):
    infoStatic.FS.descriptors.append(descriptor)
    infoStatic.FS.descriptors_num += 1


def check_path_exist(pathname: str, isLastFile: bool = False):
    if pathname == "":
        return infoStatic.CWD
    if pathname == '/':
        return infoStatic.FS.root
    pathArray = pathname.split('/')
    if pathname.startswith('/'):
        localCWD = infoStatic.FS.root
        pathArray.pop(0)
    else:
        localCWD = infoStatic.CWD
    new_localCWD = localCWD
    symlink_counter = 0
    if isLastFile:
        j = 0
        while j < len(pathArray):
            if symlink_counter > 20:
                print_error('Too much symlink')
                return None
            pathPart = pathArray[j]
            if pathPart == '.':
                j += 1
                continue
            if pathPart == '..':
                new_localCWD = localCWD.parent
                localCWD = new_localCWD
                j += 1
                continue
            arrsize = len(pathArray)
            for i in range(len(localCWD.child_directories)):
                if pathPart == localCWD.child_directories[i].name:
                    if localCWD.child_directories[i].descriptor.TYPE == 'symlink':
                        symlink_counter += 1
                        symPath = localCWD.child_directories[i].content
                        symPathArr = symPath.split('/')
                        if symPath.startswith('/'):
                            new_localCWD = infoStatic.FS.root
                            symPathArr.pop(0)
                        for ind, symm in enumerate(symPathArr):
                            pathArray.insert(j + ind + 1, symm)
                        break
                    elif j == len(pathArray) - 1 and localCWD.child_directories[i].descriptor.TYPE == 'regular':
                        return new_localCWD, localCWD.child_directories[i].descriptor
                    elif j == len(pathArray) - 1:
                        return None, None
                    else:
                        new_localCWD = localCWD.child_directories[i]
                        break
            if new_localCWD == localCWD and arrsize == len(pathArray):
                return None, None
            localCWD = new_localCWD
            j += 1
        return new_localCWD
    else:
        j = 0
        while j < len(pathArray):
            if symlink_counter > 20:
                print_error('Too much symlink')
                return None
            pathPart = pathArray[j]
            if pathPart == '.':
                j += 1
                continue
            if pathPart == '..':
                new_localCWD = localCWD.parent
                localCWD = new_localCWD
                j += 1
                continue
            arrsize = len(pathArray)
            for i in range(len(localCWD.child_directories)):
                if pathPart == localCWD.child_directories[i].name:
                    if localCWD.child_directories[i].descriptor.TYPE == 'symlink':
                        symlink_counter += 1
                        symPath = localCWD.child_directories[i].content
                        symPathArr = symPath.split('/')
                        if symPath.startswith('/'):
                            new_localCWD = infoStatic.FS.root
                            symPathArr.pop(0)
                        for ind, symm in enumerate(symPathArr):
                            pathArray.insert(j+ind+1, symm)
                        break
                    else:
                        new_localCWD = localCWD.child_directories[i]
                        break
            if new_localCWD == localCWD and arrsize == len(pathArray):
                return None
            localCWD = new_localCWD
            j += 1
        return new_localCWD


def fs_mkfs(n):
    if infoStatic.FS is not None:
        print_error('The file system was already been initialised')
        return
    if not type(n) is int:
        print_error('Type should be int')
        return
    infoStatic.FS = FS(n)
    print_ok('File system is initialised')


def fs_ls(pathname=''):
    if check_fs():
        return
    if pathname == '':
        print_descriptor_header()
        for descriptor in infoStatic.CWD.child_descriptors:
            descriptor.show_info()
        return
    workingDir = check_path_exist(pathname)
    if workingDir is None:
        print_error(f'There is no directory with this path: {pathname}')
        return
    print_descriptor_header()
    for descriptor in workingDir.child_descriptors:
        descriptor.show_info()


def fs_stat(name):
    if check_fs():
        return
    oldPath = "/".join(name.split('/')[:-1])
    if len(name.split('/')) == 2 and oldPath == '':
        oldPath = '/'
    descName = name.split('/')[-1]
    workingDir = check_path_exist(oldPath)
    if workingDir is None:
        print_error(f"There is no directory with this path: {oldPath}")
        return
    for descriptor in workingDir.child_descriptors:
        if descriptor.name == descName:
            print_descriptor_header()
            descriptor.show_info()
            return
    print_error(f'There is no file with this name: {name}')


def fs_create(name):
    if check_fs():
        return
    oldPath = "/".join(name.split('/')[:-1])
    if len(name.split('/')) == 2 and oldPath == '':
        oldPath = '/'
    descName = name.split('/')[-1]
    if len(str(descName)) > infoStatic.MAX_FILE_NAME_LENGTH:
        print_error(f'File name is too large. should be less then {infoStatic.MAX_FILE_NAME_LENGTH}')
    if infoStatic.FS.descriptors_num >= infoStatic.FS.descriptors_max_num:
        print_error('All descriptors were used')
        return
    workingDir = check_path_exist(oldPath)
    if workingDir is None:
        print_error(f"There is no directory with this path: {oldPath}")
        return
    for descriptor in workingDir.child_descriptors:
        if descriptor.name == name:
            print_error('File with this name exist')
            return
    descriptor_num = None
    for i, value in enumerate(infoStatic.FS.descriptorsBitmap):
        if not value:
            infoStatic.FS.descriptorsBitmap[i] = 1
            descriptor_num = i
            break
    descriptor = Desc(descriptor_num, 'regular', 0, descName)
    register_descriptor(descriptor)
    workingDir.child_descriptors.append(descriptor)
    print_descriptor_header()
    descriptor.show_info()


def fs_open(name):
    if check_fs():
        return
    oldPath = "/".join(name.split('/')[:-1])
    if len(name.split('/')) == 2 and oldPath == '':
        oldPath = '/'
    descName = name.split('/')[-1]
    workingDir = check_path_exist(oldPath)
    if workingDir is None:
        print_error(f"There is no directory with this path: {oldPath}")
        return
    for descriptor in workingDir.child_descriptors:
        if descriptor.name == descName:
            if isinstance(descriptor, Desc) and descriptor.TYPE == 'symlink':
                print_error('We can\'t open symlink as file')
                return
            openedFile = FileDesc(descriptor)
            infoStatic.FS.opened_files.append(openedFile)
            print_ok(f'File {name} is opened with id {openedFile.num_descriptor}')
            return
    print_error(f'There is no file with name {name}')


def fs_truncate(name, size):
    if check_fs():
        return
    oldPath = "/".join(name.split('/')[:-1])
    if len(name.split('/')) == 2 and oldPath == '':
        oldPath = '/'
    descName = name.split('/')[-1]
    workingDir = check_path_exist(oldPath)
    if workingDir is None:
        print_error(f"There is no directory with this path: {oldPath}")
        return
    for descriptor in workingDir.child_descriptors:
        if descriptor.name == descName and descriptor.TYPE == 'regular':
            if size < descriptor.length:
                num = len(descriptor.blocks)
                while num * infoStatic.BLOCK_SIZE > size + infoStatic.BLOCK_SIZE:
                    descriptor.blocks.pop(num - 1)
                    num -= 1
                descriptor.length = size
            if size > descriptor.length:
                num = len(descriptor.blocks) - 1
                for i in range(descriptor.length, size):
                    if i == infoStatic.BLOCK_SIZE * num + infoStatic.BLOCK_SIZE:
                        descriptor.blocks.append(['\0' for i in range(infoStatic.BLOCK_SIZE)])
                        num += 1
                    descriptor.blocks[num][i - num * infoStatic.BLOCK_SIZE] = 0
                descriptor.length = size
            print_ok(f'File {name} was successfully truncated')
            return
    print_error(f'There is no file with path {name}')


def fs_link(name1, name2):
    if check_fs():
        return
    filePath = "/".join(name1.split('/')[:-1])
    if len(name1.split('/')) == 2 and filePath == '':
        filePath = '/'
    descFileName = name1.split('/')[-1]
    workingFileDir = check_path_exist(filePath)
    if workingFileDir is None:
        print_error(f"There is no directory with this path: {filePath}")
        return
    linkPath = "/".join(name2.split('/')[:-1])
    if len(name2.split('/')) == 2 and linkPath == '':
        linkPath = '/'
    descLinkName = name2.split('/')[-1]
    workingLinkDir = check_path_exist(linkPath)
    if workingLinkDir is None:
        print_error(f"There is no directory with this path: {linkPath}")
        return
    if len(str(descLinkName)) > infoStatic.MAX_FILE_NAME_LENGTH:
        print_error(f'File name is too large. should be less then {infoStatic.MAX_FILE_NAME_LENGTH}')
    for descriptor in workingLinkDir.child_descriptors:
        if descriptor.name == descLinkName:
            print_error(f'An instance with this name was already created {name2}')
            return
    for descriptor in workingFileDir.child_descriptors:
        if descriptor.name == descFileName:
            if isinstance(descriptor, Desc) and descriptor.TYPE == 'symlink':
                print_error('We can\'t do link to symlink file')
                return
            if isinstance(descriptor, Link):
                print_error('You can\'t create link to link')
                return
            new_link = Link(descriptor, descLinkName)
            descriptor.links.append(new_link)
            workingLinkDir.child_descriptors.append(new_link)
            print_descriptor_header()
            new_link.show_info()
            return
    print_error(f'There is no file with name {name1}')


def fs_unlink(name):
    if check_fs():
        return
    oldPath = "/".join(name.split('/')[:-1])
    if len(name.split('/')) == 2 and oldPath == '':
        oldPath = '/'
    descName = name.split('/')[-1]
    workingDir = check_path_exist(oldPath)
    if workingDir is None:
        print_error(f"There is no directory with this path: {oldPath}")
        return
    for descriptor in workingDir.child_descriptors:
        if descriptor.name == descName:
            if isinstance(descriptor, Desc):
                if descriptor.TYPE == 'directory':
                    print_error('You can\'t unlink directory')
                    return
                workingDir.child_descriptors.remove(descriptor)
                descriptor.links_num -= 1
                if descriptor.links_num == 0:
                    infoStatic.FS.descriptorsBitmap[descriptor.NUM] = 0
                    del descriptor
                print_ok('Unlinked')
            else:
                descriptor.descriptor.links_num -= 1
                descriptor.descriptor.links.remove(descriptor)
                workingDir.child_descriptors.remove(descriptor)
                if descriptor.descriptor.links_num == 0:
                    infoStatic.FS.descriptorsBitmap[descriptor.descriptor.NUM] = 0
                    del descriptor.descriptor
                print_ok('Unlinked')
            return
    print_error(f'There is no link with name {name}')


def fs_close(fd):
    if check_fs():
        return
    if fd in infoStatic.FS.opened_files_num_descriptors:
        infoStatic.FS.opened_files_num_descriptors.remove(fd)
        for openedFile in infoStatic.FS.opened_files:
            if openedFile.num_descriptor == fd:
                infoStatic.FS.opened_files.remove(openedFile)
                del openedFile
                print_ok(f'File with id {fd} is closed')
                return
    print_error(f'There is no file opened with ID = {fd}')


def fs_seek(fd, offset):
    if check_fs():
        return
    if fd not in infoStatic.FS.opened_files_num_descriptors:
        print_error(f'There is no opened file with ID = {fd}')
        return
    for openedFile in infoStatic.FS.opened_files:
        if openedFile.num_descriptor == fd:
            openedFile.offset = offset
            print_ok('Offset was set')
            return


def fs_write(fd, size, val):
    if check_fs():
        return
    if len(str(val)) != 1:
        print_error('Val should be 1 byte size')
        return
    if fd not in infoStatic.FS.opened_files_num_descriptors:
        print_error(f'There is no opened file with ID = {fd}')
        return
    for openedFile in infoStatic.FS.opened_files:
        if openedFile.num_descriptor == fd:
            num = len(openedFile.descriptor.blocks)
            while openedFile.offset + size > num * infoStatic.BLOCK_SIZE:
                openedFile.descriptor.blocks.append(['\0' for i in range(infoStatic.BLOCK_SIZE)])
                num += 1
            num = 0
            for i in range(openedFile.offset + size):
                if i == infoStatic.BLOCK_SIZE * num + infoStatic.BLOCK_SIZE:
                    num += 1
                if i >= openedFile.offset:
                    openedFile.descriptor.blocks[num][i - num * infoStatic.BLOCK_SIZE] = val
            if openedFile.descriptor.length < openedFile.offset + size:
                openedFile.descriptor.length = openedFile.offset + size
            print_ok('Data were written to file')
            return


def fs_read(fd, size):
    if check_fs():
        return
    if fd not in infoStatic.FS.opened_files_num_descriptors:
        print_error(f'There is no opened file with ID = {fd}')
        return
    for openedFile in infoStatic.FS.opened_files:
        if openedFile.num_descriptor == fd:
            if openedFile.descriptor.length < openedFile.offset + size:
                print_error(
                    f'File length is {openedFile.descriptor.length}. We can\'t read from {openedFile.offset} to {openedFile.offset + size}')
                return
            num = openedFile.offset // infoStatic.BLOCK_SIZE
            answer = ""
            for i in range(openedFile.offset, openedFile.offset + size):
                if i == infoStatic.BLOCK_SIZE * num + infoStatic.BLOCK_SIZE:
                    num += 1
                answer += str(openedFile.descriptor.blocks[num][i - num * infoStatic.BLOCK_SIZE])
            print(answer)


def fs_symlink(string, pathname):
    if check_fs():
        return
    if infoStatic.FS.descriptors_num >= infoStatic.FS.descriptors_max_num:
        print_error('All descriptors were used')
        return
    oldPath = "/".join(pathname.split('/')[:-1])
    if len(pathname.split('/')) == 2 and oldPath == '':
        oldPath = '/'
    newSymName = pathname.split('/')[-1]
    if len(str(newSymName)) > infoStatic.MAX_FILE_NAME_LENGTH:
        print_error(f'File name is too large. should be less then {infoStatic.MAX_FILE_NAME_LENGTH}')
        return
    if newSymName == '':
        print_error('Name could\'t be empty')
        return
    workingDir = check_path_exist(oldPath)
    if workingDir is None:
        print_error(f"There is no directory with this path: {oldPath}")
        return
    for directory in workingDir.child_directories:
        if newSymName == directory.name:
            print_error('Directory with this name exist')
            return
    descriptor_num = None
    for i, value in enumerate(infoStatic.FS.descriptorsBitmap):
        if not value:
            infoStatic.FS.descriptorsBitmap[i] = 1
            descriptor_num = i
            break
    newSymlinkDescriptor = Desc(descriptor_num, 'symlink', 0, newSymName, string)
    register_descriptor(newSymlinkDescriptor)
    newSymlink = Sym(newSymName, newSymlinkDescriptor, workingDir, string)
    workingDir.child_directories.append(newSymlink)
    workingDir.child_descriptors.append(newSymlinkDescriptor)


def fs_rmdir(pathname):
    if check_fs():
        return
    if pathname == '/':
        print_error('You can\'t delete root directory')
        return
    if pathname == '' or pathname == '.':
        print_error('You can\'t delete current directory')
        return
    if pathname == '..':
        print_error('It\'s unlogical to try delete directory that upper then other. Really? ')
        return
    oldDir = check_path_exist(pathname)
    if oldDir is None:
        print_error(f"There is no directory with this path: {pathname}")
        return
    if len(oldDir.child_descriptors) != 2:
        print_error('You can\'t delete nonempty dir')
        return
    if infoStatic.CWD == oldDir:
        print_error('You can\'t delete directory you are in now ')
    oldDir.parent.child_descriptors.remove(oldDir.descriptor)
    oldDir.parent.child_directories.remove(oldDir)
    oldDir.child_descriptors.clear()
    oldDir.child_directories.clear()
    oldDir.parent.descriptor.links_num -= 1
    infoStatic.FS.descriptors.remove(oldDir.descriptor)
    infoStatic.FS.descriptorsBitmap[oldDir.descriptor.NUM] = 0
    infoStatic.FS.descriptors_num -= 1
    del oldDir.descriptor
    del oldDir
    print_ok('Directory is deleted')


def fs_cd(pathname):
    if check_fs():
        return
    if pathname == '/':
        infoStatic.CWD = infoStatic.FS.root
        return
    newDir = check_path_exist(pathname)
    if newDir is None:
        print_error(f"There is no directory with this path: {pathname}")
        return
    infoStatic.CWD = newDir
    print_ok('Directory is changed')


def fs_mkdir(pathname: str):
    if check_fs():
        return
    if infoStatic.FS.descriptors_num >= infoStatic.FS.descriptors_max_num:
        print_error('All descriptors were used')
        return
    oldPath = "/".join(pathname.split('/')[:-1])
    if len(pathname.split('/')) == 2 and oldPath == '':
        oldPath = '/'
    newDirName = pathname.split('/')[-1]
    if len(str(newDirName)) > infoStatic.MAX_FILE_NAME_LENGTH:
        print_error(f'File name is too large. should be less then {infoStatic.MAX_FILE_NAME_LENGTH}')
    workingDir = check_path_exist(oldPath)
    if workingDir is None:
        print_error(f"There is no directory with this path: {oldPath}")
        return
    for directory in workingDir.child_directories:
        if newDirName == directory.name:
            print_error('Directory with this name exist')
            return
    descriptor_num = None
    for i, value in enumerate(infoStatic.FS.descriptorsBitmap):
        if not value:
            infoStatic.FS.descriptorsBitmap[i] = 1
            descriptor_num = i
            break
    newDirDescriptor = Desc(descriptor_num, 'directory', 0, newDirName)
    register_descriptor(newDirDescriptor)
    newDir = Dir(newDirName, newDirDescriptor, workingDir)
    workingDir.child_descriptors.append(newDirDescriptor)
    workingDir.child_directories.append(newDir)
    print_ok('Directory is created')