import os
import subprocess
import tarfile
from distutils.spawn import find_executable

from .exceptions import GitExecutionError
from .logging import LOGGER


PKG_PATH = os.path.dirname(os.path.realpath(__file__))
VENDOR_PATH = os.path.realpath('{}/vendor'.format(PKG_PATH))
GIT_VERSION = '2.4.3'
GIT_TAR_FILE = '{}/git-{}.tar'.format(VENDOR_PATH, GIT_VERSION)
TMP_PATH = '/tmp'
BIN_PATH = os.path.join(TMP_PATH, 'usr/bin')
GIT_TEMPLATE_DIR = os.path.join(TMP_PATH, 'usr/share/git-core/templates')
GIT_EXEC_PATH = os.path.join(TMP_PATH, 'usr/libexec/git-core')
LD_LIBRARY_PATH = os.path.join(TMP_PATH, 'usr/lib64')
GIT_BINARY = '{}/usr/bin/git'.format(TMP_PATH)


if not find_executable('git'):
    LOGGER.info('git not found installing using local copy')
    if not os.path.isfile(GIT_BINARY):
        LOGGER.info('extracting git tarball')
        tar = tarfile.open(GIT_TAR_FILE)
        tar.extractall(path=TMP_PATH)
        tar.close()

    LOGGER.info('setting up environment variables')
    os.environ['PATH'] += ':{}'.format(BIN_PATH)
    os.environ['GIT_TEMPLATE_DIR'] = GIT_TEMPLATE_DIR
    os.environ['GIT_EXEC_PATH'] = GIT_EXEC_PATH
    os.environ['LD_LIBRARY_PATH'] = LD_LIBRARY_PATH


# def exec_command(*args, **kwargs):
#     ''' For standard commands without any command line input '''
#     options = dict({'cwd': '/tmp', 'env': os.environ}, **kwargs)
#     command = ['git'] + list(args)
#     LOGGER.info('executing git command: "{}"'.format(' '.join(command)))
#     p = subprocess.Popen(command, stdout=subprocess.PIPE,
#                          stderr=subprocess.PIPE, cwd=options['cwd'],
#                          env=options['env'])
#     stdout, stderr = p.communicate()
#     if p.returncode != 0:
#         LOGGER.error('git failed with {} returncode'.format(p.returncode))
#         raise GitExecutionError(
#             'command={} returncode={} stdout="{}" '
#             'stderr="{}"'.format(command, p.returncode, stdout, stderr)
#         )
#     return stdout, stderr

def exec_command(*args, **kwargs):
    ''' 
    For commands when command line input is needed add a keyworded arg named 'clinput'
    which is a list of the things you need to input in order of how they are asked. 
    For example, if your repository is private, and requires a username/password.

    Example 1:
        You want to clone a private repo. You can clone via 
            git clone [user]:[password]@host.xz/path/to/repo.git
        However this will leave the password in your git/bash history, and also 
        is not allowed if you use an access token as your password (via github standards).
        So instead you can 
            git clone host.xz/path/to/repo.git
        Then your keywords arg should include
            git.exec_command('clone', 'pathtorepo', ..., clinput=['username', 'password'])
        
        Or you could
            git clone [user@]host.xz/path/to/repo.git
        In which your keywords arg should inlude
            git.exec_command('clone', 'pathtorepo', ..., clinput=['password'])
    Example 2:
        Clone using an access token. 
            git clone [user]@host.xz:path/to/repo.git
        In which it will prompt for a password which is passed in.
            git.exec_command('clone', 'pathtorepo', ..., clinput=['accesstoken'])
    '''
    options = dict({'cwd': '/tmp', 'env': os.environ}, **kwargs)
    command = ['git'] + list(args)
    LOGGER.info('executing git command: "{}"'.format(' '.join(command)))
    LOGGER.info('Test')
    p, stdout, stderr = None, None, None

    if 'clinput' in options:
        LOGGER.info('Inputting command line arguments')
        p = subprocess.Popen(command, 
                             stdin  = subprocess.PIPE, 
                             stdout = subprocess.PIPE,
                             stderr = subprocess.PIPE,
                             cwd=options['cwd'],
                             env=options['env'], 
                             universal_newlines=True)
        newline = os.linesep
        stdout, stderr = p.communicate( newline.join(options['clinput']) )
    else:
        p = subprocess.Popen(command, 
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, 
                             cwd=options['cwd'],
                             env=options['env'])
        stdout, stderr = p.communicate()
    
    if p.returncode != 0:
        LOGGER.error('git failed with {} returncode'.format(p.returncode))
        raise GitExecutionError(
            'command={} returncode={} stdout="{}" '
            'stderr="{}"'.format(command, p.returncode, stdout, stderr)
        )
    return stdout, stderr
        
