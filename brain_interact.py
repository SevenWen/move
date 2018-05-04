#! /usr/bin/env python

"""Interacts with a PyPy subprocess translated with --sandbox.

Usage:
    pypy_interact.py [options] <executable> <args...>

Options:
    --tmp=DIR     the real directory that corresponds to the virtual /tmp,
                  which is the virtual current dir (always read-only for now)
    --heapsize=N  limit memory usage to N bytes, or kilo- mega- giga-bytes
                  with the 'k', 'm' or 'g' suffix respectively.
    --timeout=N   limit execution time to N (real-time) seconds.
    --log=FILE    log all user input into the FILE.
    --verbose     log all proxied system calls.

Note that you can get readline-like behavior with a tool like 'ledit',
provided you use enough -u options:

    ledit python -u pypy_interact.py pypy3-c-sandbox -u
"""

import sys, os, asyncio, asyncio_interface, playground
#from rpython.translator.sandbox.sandlib import SimpleIOSandboxedProc
from sandlib import VirtualizedNetworkProc
from rpython.translator.sandbox.vfs import Dir, RealDir, RealFile
import pypy
LIB_ROOT = os.path.dirname(os.path.dirname(pypy.__file__))

EXIT_HANDLERS = []
def runSafe(f):
    try:
        f()
    except: pass
    
def AddExitHandler(f):
    EXIT_HANDLERS.append(lambda: runSafe(f))
    
def RunExitHandlers():
    for f in EXIT_HANDLERS: f()

class PyPySandboxedProc(VirtualizedNetworkProc):#, SimpleIOSandboxedProc):
    argv0 = '/bin/pypy3-c'
    virtual_cwd = '/tmp'
    virtual_env = {"userbase":"/tmp"}
    virtual_console_isatty = True

    pypy_stdlib_path = "/bin/"

    def __init__(self, executable, arguments, tmpdir=None, debug=True):
        self.executable = executable = os.path.abspath(executable)
        self.tmpdir = tmpdir
        self.debug = debug
        super(PyPySandboxedProc, self).__init__([self.argv0] + arguments,
                                                executable=executable)

    def build_virtual_root(self):
        # build a virtual file system:
        # * can access its own executable
        # * can access the pure Python libraries
        # * can access the temporary usession directory as /tmp
        exclude = ['.pyc', '.pyo']
        if self.tmpdir is None:
            tmpdirnode = Dir({})
        else:
            tmpdirnode = RealDir(self.tmpdir, exclude=exclude)
        libroot = str(LIB_ROOT)

        return Dir({
            'bin': Dir({
                'pypy3-c': RealFile(self.executable),#, mode=0111),
                'lib-python': RealDir(os.path.join(libroot, 'lib-python'),
                                      exclude=exclude), 
                'lib_pypy': RealDir(os.path.join(libroot, 'lib_pypy'),
                                      exclude=exclude),
                }),
             'tmp': tmpdirnode,
             'dev': Dir({
                'urandom': RealFile("/dev/urandom")})
             })

def main():
    from getopt import getopt      # and not gnu_getopt!
    options, arguments = getopt(sys.argv[1:], 't:hv', 
                                ['tmp=', 'heapsize=', 'timeout=', 'log=', 'gameobj=',
                                 'verbose', 'help'])
    tmpdir = None
    timeout = None
    logfile = None
    debug = False
    extraoptions = []

    def help():
        print >> sys.stderr, __doc__
        sys.exit(2)

    for option, value in options:
        if option in ['-t', '--tmp']:
            value = os.path.abspath(value)
            if not os.path.isdir(value):
                raise OSError("%r is not a directory" % (value,))
            tmpdir = value
        elif option == '--heapsize':
            value = value.lower()
            if value.endswith('k'):
                hbytes = int(value[:-1]) * 1024
            elif value.endswith('m'):
                hbytes = int(value[:-1]) * 1024 * 1024
            elif value.endswith('g'):
                hbytes = int(value[:-1]) * 1024 * 1024 * 1024
            else:
                hbytes = int(value)
            if hbytes <= 0:
                raise ValueError
            if hbytes > sys.maxsize:
                raise OverflowError("--heapsize maximum is %d" % sys.maxsize)
            extraoptions[:0] = ['--heapsize', str(hbytes)]
        elif option == '--timeout':
            timeout = int(value)
        elif option == '--log':
            logfile = value
        elif option in ['-v', '--verbose']:
            debug = True
        elif option in ['-h', '--help']:
            help()
        elif option == "--gameobj":
            asyncio_interface.gOBJECT_IDENTIFIER = int(value)
        else:
            raise ValueError(option)

    if len(arguments) < 1:
        help()

    if tmpdir is None:
        raise Exception("A tmp directory is required for a brain.")
    
    # lock in this path.
    asyncio_interface.PLAYGROUND_CFG_PATH = os.path.join(tmpdir, ".playground")
    playground.Configure.AddCustomPath("brain",asyncio_interface.PLAYGROUND_CFG_PATH)
    playground.reloadConnectors() # Resets the connectors for the new Configure path
    
    sandproc = PyPySandboxedProc(arguments[0], extraoptions + arguments[1:],
                                 tmpdir=tmpdir, debug=debug)
    if timeout is not None:
        sandproc.settimeout(timeout, interrupt_main=True)
    if logfile is not None:
        sandproc.setlogfile(logfile)
    
    AddExitHandler(sandproc.kill)
    asyncio.get_event_loop().run_in_executor(None, sandboxThread, sandproc, asyncio.get_event_loop())
        
def sandboxThread(sandproc, loop):
    try:
        sandproc.interact()
    finally:
        sandproc.kill()
    loop.call_soon_threadsafe(stop)
    
def stop():
    asyncio.get_event_loop().stop()

if __name__ == '__main__':
    # Global variable gLOOP is not optimal. What's a better way?
    asyncio_interface.gLOOP = asyncio.get_event_loop()
    asyncio.get_event_loop().set_debug(True)
    main()
    try:
        asyncio.get_event_loop().run_forever()
    finally:
        RunExitHandlers()