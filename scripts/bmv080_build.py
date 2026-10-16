Import('env')
from os.path import join
sdk = join(env['PROJECT_DIR'], 'private', 'bmv080')
env.Append(CPPPATH=[sdk], LIBPATH=[sdk], LIBS=['_bmv080', '_postProcessor'])
