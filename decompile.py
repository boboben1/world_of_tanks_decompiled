import os
import fnmatch
import shutil
import errno
import uncompyle6
import logging
import sys
import threading

logging.basicConfig(filename='decompile.log', filemode='w',
                    format='%(name)s - %(levelname)s - %(message)s', level="INFO")


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


def main():

    logging.info("Decompiling files")

    errors = 0

    PYC = []

    for filename in (filename for filename in find_files('scripts', "*") if filename.endswith(".pyc")):
        PYC.append(filename)

    with open("allpyc.txt", "w") as f:
        for item in PYC:
            f.write("%s\n" % item)
    try:
        for filename in PYC:
            basename = os.path.splitext(os.path.basename(filename))[0]
            dirname = os.path.dirname(filename)
            try:
                fileobj = openAndMakeDirs("decompiled\\%s\\%s.py" %
                                          (dirname, basename), "w")
                uncompyle6.uncompyle_file(filename, fileobj)
                #print("Decompiled file %s" % (filename))
                fileobj.close()
            except (uncompyle6.semantics.pysource.SourceWalkerError, uncompyle6.parser.ParserError):
                logging.error("Error occurred decompiling file: %s" % filename)
                errors += 1
    except Exception as e:
        print(e.__class__.__name__)
        logging.error(str(e))

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


# Took forever to figure this out
if __name__ == '__main__':
    sys.setrecursionlimit(100000)
    threading.stack_size(200000000)
    thread = threading.Thread(target=main)
    thread.start()
