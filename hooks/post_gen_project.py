import os
import io
import shutil
import zipfile
import tempfile
import urllib.request

from os.path import join as path_join

print("post-run hook!")
print(os.getcwd())
def enabled(arg):
    if len(arg) == 0: return False
    return arg.lower()[0] == 'y'

def rmdir(*path_parts):
    path = os.sep.join(str(i) for i in path_parts)
    if not os.path.exists(path):
        return
    print("Pruning unwanted %s%c" % (path, os.sep))
    shutil.rmtree(path)

def copyintotree(src, dst, symlinks=False, ignore=None):
    """Copy files in src into possibly existing directly dst"""
    if not os.path.exists(dst):
        os.makedirs(dst)
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            copyintotree(s, d, symlinks, ignore)
        else:
            if not os.path.exists(d) or os.stat(s).st_mtime - os.stat(d).st_mtime > 1:
                shutil.copy2(s, d)

def download_install(code_root, vendor_name, archive_url):
    print("Downloading %s from %s ..." % (vendor_name, archive_url))
    response = urllib.request.urlopen(archive_url)
    data = response.read()
    print("Completed")
    zip_bytes = io.BytesIO(data)

    tmp_dir = tempfile.TemporaryDirectory(suffix="cookiecutter_post_gen_project")

    zip = zipfile.ZipFile(zip_bytes)
    zip.extractall(tmp_dir.name)
    print("unzipped to " + tmp_dir.name)

    src_dir = tmp_dir.name    
    # if there is only one directory in the tempdir, then move the contents to vendor_name
    tmp_contents = os.listdir(tmp_dir.name)
    if len(tmp_contents) == 1:
        print("happenin'")
        src_dir = path_join(src_dir, tmp_contents[0])

    print("src_dir: " + src_dir)

    dst_dir = path_join(code_root, 'vendors', vendor_name)
    copyintotree(src_dir, dst_dir)

#
# begin main
#
if __name__ == '__main__':

    #
    # Prune
    #
    code_root = '{{ cookiecutter.directory_name }}'
    if not enabled('{{ cookiecutter.support_build }}'):
        rmdir(code_root, 'build')
        shutil.rmtree("build")
        
    if not enabled('{{ cookiecutter.support_shaders }}'):
        rmdir(code_root, 'src', 'shaders')
            
    if not enabled('{{ cookiecutter.support_config }}'):
        rmdir(code_root, 'src', 'config')

    if not enabled('{{ cookiecutter.support_public_include }}'):
        rmdir(code_root, 'include')

    if not enabled('{{ cookiecutter.support_vendors }}'):
        rmdir(code_root, "vendors")

    if not enabled('{{ cookiecutter.support_test }}'):
        rmdir(code_root, "test")

    if not enabled('{{ cookiecutter.support_docs }}'):
        rmdir(code_root, "docs")

    if not enabled('{{ cookiecutter.share }}'):
        print("Pruning LICENSE")
        os.remove(path_join(code_root, "LICENSE"))

    if not enabled('{{ cookiecutter.uselib_sdl2 }}'):
        rmdir(code_root, "vendors", "SDL2")

    # rename main project file based on extension
    if '{{ cookiecutter.main_language }}' == 'c++':
        path = path_join(code_root, 'src', '{{ cookiecutter.project_prefix }}')
        src_path = path + '.c'
        dst_path = path + '.cpp'
        os.rename(src_path, dst_path)
        
    #
    # Run premake
    #
    os.chdir(path_join(code_root, "build"))
    print(os.getcwd())
    print("---")
    os.system("premake5 dist")
    os.chdir("../..")

    #
    # Download vendors
    # 
    download_install(code_root, "SDL2", "{{ cookiecutter.sdl2_archive_url }}")
