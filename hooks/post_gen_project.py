import os
import io
import sys
import stat
import shutil
import zipfile
import tarfile
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

def _download_file(vendor_name, archive_url):
    """Download a file, returning its bytes"""
    print("Downloading %s from %s ..." % (vendor_name, archive_url))
    response = urllib.request.urlopen(archive_url)
    data = response.read()
    print("Completed")
    return io.BytesIO(data)

def _make_all_files_readable_writable(root_dir):
    """recurse root_dir, making sure all files have +w"""
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            path = path_join(root, file)
            os.chmod(path, stat.S_IWRITE|stat.S_IREAD)
                
def download_unzip_install(code_root, vendor_name, archive_url):
    if len(archive_url) == 0:
        return

    zip_bytes = _download_file(vendor_name, archive_url)
    
    tmp_dir = tempfile.TemporaryDirectory(suffix="cookiecutter_post_gen_project")

    zip = zipfile.ZipFile(zip_bytes)
    zip.extractall(tmp_dir.name)
    print("unzipped to " + tmp_dir.name)

    src_dir = tmp_dir.name    
    # if there is only one directory in the tempdir, then move the contents to vendor_name
    tmp_contents = os.listdir(tmp_dir.name)
    if len(tmp_contents) == 1:
        print("unzipping the contents of zip's %s into %s" % (tmp_contents[0], vendor_name))
        src_dir = path_join(src_dir, tmp_contents[0])

    dst_dir = path_join(code_root, 'vendors', vendor_name)
    if not os.path.isdir(dst_dir):
        os.mkdir(dst_dir)
    copyintotree(src_dir, dst_dir)

def download_untar_install(code_root, vendor_name, archive_url):
    if len(archive_url) == 0:
        return

    tar_bytes = _download_file(vendor_name, archive_url)
    tar = tarfile.open(mode='r', fileobj=tar_bytes)

    tmp_dir = tempfile.TemporaryDirectory(suffix="cookiecutter_post_gen_project")

    tar.extractall(tmp_dir.name)
    print("untarred to " + tmp_dir.name)

    src_dir = tmp_dir.name
    # if there is only one directory in the tempdir, then move the contents to vendor_name
    tmp_contents = os.listdir(tmp_dir.name)
    if len(tmp_contents) == 1:
        print("unzipping the contents of zip's %s into %s" % (tmp_contents[0], vendor_name))
        src_dir = path_join(src_dir, tmp_contents[0])
    
    dst_dir = path_join(code_root, 'vendors', vendor_name)
    if not os.path.isdir(dst_dir):
        os.mkdir(dst_dir)

    # workaround for some files in tar being read-only
    _make_all_files_readable_writable(tmp_dir.name)

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

    if not enabled('{{ cookiecutter.has_dist_dir }}'):
        dist_root = '{{ cookiecutter.directory_name }}_dist'
        rmdir(dist_root)

    # can't get rid of tools if vendors is being supported:
    # tools/pylib contains vendorcompile.py
    if not enabled('{{ cookiecutter.support_tools }}') and \
       not enabled('{{ cookiecutter.support_vendors }}'):
        rmdir(code_root, "tools")

    if not enabled('{{ cookiecutter.support_vendors }}'):
        rmdir(code_root, "tools", "pylib")

    if '{{ cookiecutter.open_source_license }}' == 'Not open source':
        print("Pruning LICENSE")
        os.remove(path_join(code_root, "LICENSE"))

    if not enabled('{{ cookiecutter.support_config_buildinfo }}'):
        buildinfo_path = path_join(code_root, "src", "config", \
                                   '{{ cookiecutter.project_prefix }}buildinfo.h')
        if os.path.exists(buildinfo_path):
            os.remove(buildinfo_path)

    if not enabled('{{ cookiecutter.uselib_sdl2 }}'):
        rmdir(code_root, "vendors", "SDL2")

    if not enabled('{{ cookiecutter.uselib_bgfx }}'):
        rmdir(code_root, "vendors", "bgfx")

    if not enabled('{{ cookiecutter.uselib_glew }}'):
        rmdir(code_root, "vendors", "glew")

    if not enabled('{{ cookiecutter.uselib_lua53 }}'):
        rmdir(code_root, "vendors", "lua53")


    # rename main project file based on extension
    if '{{ cookiecutter.main_language }}' == 'c++':
        path = path_join(code_root, 'src', '{{ cookiecutter.directory_name }}')
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
    if '{{ cookiecutter.support_vendors }}' == 'y':
        if enabled('{{ cookiecutter.uselib_sdl2 }}'):
            download_unzip_install(code_root, "SDL2", "{{ cookiecutter.sdl2_archive_url }}")
        if enabled('{{ cookiecutter.uselib_bgfx }}'):
            download_unzip_install(code_root, "bgfx", "{{ cookiecutter.bgfx_archive_url }}")
            download_unzip_install(code_root, "bx", "{{ cookiecutter.bx_archive_url }}")
            download_unzip_install(code_root, "bimg", "{{ cookiecutter.bimg_archive_url }}")
        if enabled('{{ cookiecutter.uselib_glew }}'):
            download_unzip_install(code_root, 'glew', "{{ cookiecutter.glew_archive_url }}")
        if enabled('{{ cookiecutter.uselib_lua53 }}'):
            download_untar_install(code_root, 'lua53', '{{ cookiecutter.lua53_archive_url }}')
                                                     

    #
    # Prune temp files
    #
    print("Pruning temp files")
    for dirpath, dirnames, filenames in os.walk(code_root):
        for filename in filenames:
            filepath = path_join(dirpath, filename)
            if filepath[-1] == '~':
                os.remove(filepath)
            
    # 
    # success message
    #
    print("\nSuccessfully generated project")
    print("Next steps: ")
    print("\tadd {{ cookiecutter.directory_name }} into source control")
    if '{{ cookiecutter.has_dist_dir }}' == 'y':
        print("\tadd {{ cookiecutter.directory_name }}_dist into source control")

    if '{{ cookiecutter.support_vendors }}' == 'y':
        print("\tgo into {{ cookiecutter.directory_name }}/vendors and run compile_all_vendors.py")
    print("\tgo into {{ cookiecutter.directory_name }}/build and build the desired project")

    if '{{ cookiecutter.support_vendors }}' == 'y' and '{{ cookiecutter.project_kind }}' == 'StaticLib':
        print("WARNING: You have chosen to support vendors on a static library project.  Static linking " +
              "static libraries is not supported on premake's gmake option.  The better approach " +
              "is to include all static libraries as vendors in the final binary.")
