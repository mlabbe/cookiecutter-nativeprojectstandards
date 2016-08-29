import os
import shutil

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
