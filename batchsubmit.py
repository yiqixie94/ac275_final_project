import os, sys, shutil
import time, io



def run_recursive(search_depth=0, root=os.getcwd(), filename='batch.sh', cmdfmt='sbatch {path}'):
    counter = 0
    filepath = os.path.join(root, filename)
    if os.path.exists(filepath):
        os.chdir(root)
        os.system(cmdfmt.format(path=filepath))
        print(filepath)
        counter += 1
    if search_depth > 0:
        for subname in os.listdir(root):
            subpath = os.path.join(root, subname)
            if os.path.isdir(subpath):
                counter += run_recursive(search_depth-1, subpath, filename, cmdfmt)
    return counter


if __name__ == '__main__':
    run_recursive(1)


