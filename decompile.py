import os
import fnmatch
import shutil
import errno
import uncompyle6
import logging

logging.basicConfig(filename='decompile.log', filemode='w',
                    format='%(name)s - %(levelname)s - %(message)s')


def copyFile(src, dest):
    try:
        os.makedirs(os.path.dirname(dest))
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
    shutil.copyfile(src, dest)


def openAndMakeDirs(file, mode):
    try:
        os.makedirs(os.path.dirname(file))
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
    return open(file, mode)


def find_files(directory, pattern):
    for root, dirs, files in os.walk(directory):
        for basename in files:
            if fnmatch.fnmatch(basename, pattern):
                filename = os.path.join(root, basename)
                yield filename


logging.info("Decompiling files")

errors = 0

for filename in (filename for filename in find_files('scripts', "*") if filename.endswith(".pyc")):
    basename = os.path.splitext(os.path.basename(filename))[0]
    dirname = os.path.dirname(filename)
    with openAndMakeDirs("decompiled\\%s\\%s.py" % (dirname, basename), "w") as fileobj:
        try:
            uncompyle6.uncompyle_file(filename, fileobj)
        except:
            logging.error("Error occurred decompiling file: %s" % filename)
            errors += 1

if errors > 0:
    logging.warning(
        "Decompiling some files failed! Check decompile.log for details")
else:
    logging.info("All files decompiled successfully!")

logging.info("Moving other files")

List = []

for filename in (filename for filename in find_files('scripts', "*") if not filename.endswith(".pyc")):
    List.append(filename)

for item in List:
    copyFile(item, "decompiled\\%s\\%s" %
             (os.path.dirname(item), os.path.basename(item)))
