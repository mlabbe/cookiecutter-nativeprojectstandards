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
    print("Pruning unwanted %s%c" % (path, os.sep))
    shutil.rmtree(path)

#
# begin main
#
if __name__ == '__main__':

    #
    # Prune
    #
    if not enabled('{{ cookiecutter.support_build }}'):
        rmdir('build')
        shutil.rmtree("build")
        
    if not enabled('{{ cookiecutter.support_shaders }}'):
        rmdir('src', 'shaders')
            
    if not enabled('{{ cookiecutter.support_config }}'):
        rmdir('src', 'config')

    if not enabled('{{ cookiecutter.support_public_include }}'):
        rmdir('include')

    if not enabled('{{ cookiecutter.support_vendors }}'):
        rmdir("vendors")

    if not enabled('{{ cookiecutter.support_test }}'):
        rmdir("test")

    if not enabled('{{ cookiecutter.share }}'):
        print("Pruning LICENSE")
        os.remove("LICENSE")

    # rename main project file based on extension
    if '{{ cookiecutter.main_language }}' == 'c++':
        path = path_join('src', '{{ cookiecutter.project_prefix }}')
        src_path = path + '.c'
        dst_path = path + '.cpp'
        os.rename(src_path, dst_path)
        
    #
    # Run premake
    #
    os.chdir("build")
    os.system("premake5 dist")
    os.chdir("..")
