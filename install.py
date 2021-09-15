import os, shutil


root = r'c:\\'
for fn in os.listdir(root):
    if fn[:6].lower() == 'python':
        shutil.copytree(os.path.join('src', 'micro'), os.path.join(root, fn, 'Lib', 'site-packages', 'micro'))
