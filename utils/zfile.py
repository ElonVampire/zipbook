#   Programmer: limodou
#   E-mail:     limodou@gmail.com
#
#   Copyleft 2005 limodou
#
#   Distributed under the terms of the GPL (GNU Public License)
#
#   ZFile is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#   $Id$

import zipfile
import os
import os.path
import sys
import getopt

__appname__ = 'zfile'
__author__ = 'limodou'
__version__ = '0.1'

class ZFile(object):
    def __init__(self, filename, mode='r', basedir='', visitor=None):
        self.filename = filename
        self.mode = mode
        if self.mode in ('w', 'a'):
            self.zfile = zipfile.ZipFile(filename, self.mode, compression=zipfile.ZIP_DEFLATED)
        else:
            self.zfile = zipfile.ZipFile(filename, self.mode)
        self.basedir = basedir
        if not self.basedir:
            self.basedir = os.path.dirname(filename)
        self.basedir = os.path.normpath(os.path.abspath(self.basedir)).replace('\\', '/')
        self.visitor = visitor
        
    def addfile(self, path, arcname=None):
        path = os.path.normpath(path).replace('\\', '/')
        if not arcname:
            if path.startswith(self.basedir + '/'):
                arcname = path[len(self.basedir) + 1:]
            else:
                arcname = ''
        if self.visitor:
            self.visitor(path, arcname)
        self.zfile.write(path, arcname)
        
    def addstring(self, arcname, string):
        self.zfile.writestr(arcname, string)
            
    def addfiles(self, paths):
        for path in paths:
            if isinstance(path, tuple):
                p, arcname = path
                p = os.path.abspath(p)
                if os.path.isdir(p):
                    self.addpath(p)
                else:
                    self.addfile(p, arcname)
            else:
                path = os.path.abspath(path)
                if os.path.isdir(path):
                    self.addpath(path)
                else:
                    self.addfile(path)
                
    def addpath(self, path):
        files = self._getallfiles(path)
        self.addfiles(files)
            
    def close(self):
        self.zfile.close()
        
    def extract_to(self, path):
        for p in self.zfile.namelist():
            self.extract(p, path)
            
    def extract(self, filename, path):
        if not filename.endswith('/'):
            f = os.path.join(path, filename)
            dir = os.path.dirname(f)
            if not os.path.exists(dir):
                os.makedirs(dir)
            file(f, 'wb').write(self.zfile.read(filename))

    def _getallfiles(self, path):
        fset = []
        for root, dirs, files in os.walk(path):
            for f in files:
                fset.append(os.path.join(root, f))
        return fset
            
        
def create(zfile, files, basedir='', visitor=None):
    z = ZFile(zfile, 'w', basedir, visitor=visitor)
    z.addfiles(files)
    z.close()
    
def extract(zfile, path):
    z = ZFile(zfile)
    z.extract_to(path)
    z.close()
   
def main():
    #process command line

    cmdstring = "Vhl:i:b:"

    try:
        opts, args = getopt.getopt(sys.argv[1:], cmdstring, [])
    except getopt.GetoptError:
        Usage()
        sys.exit(1)

    filelist = ''
    inputfiles = ''
    basedir = ''
    for o, a in opts:
        if o == '-V':       #version
            Version()
            sys.exit()
        elif o == '-h':       
            Usage()
            sys.exit()
        elif o == '-l':
            filelist = a
        elif o == '-i':
            inputfiles = a
        elif o == '-b':
            basedir = a

    if not basedir:
        basedir = os.getcwd()
        
    if inputfiles and filelist or len(args) < 1:
        Usage()
        sys.exit()
        
    zipfile = args[0]
    if not inputfiles and len(args) > 1:
        fout = None
        if filelist:
            fout = file(filelist, 'w')
            
        def visitor(path, arcname, f=fout):
            if f:
                f.write(arcname + '\n')

        if len(args) == 2 and os.path.isdir(args[1]):
            create(zipfile, args[1:], basedir, visitor)
        else:
            create(zipfile, args[1:], basedir, visitor=visitor)
        if fout:
            fout.close()
    elif inputfiles and len(args) == 1:
        lines = file(inputfiles).readlines()
        files = [f.strip() for f in lines]
        create(zipfile, files, basedir)
    
    else:
        Usage()
        sys.exit()
    
            
def Usage():
    print """Usage %s [options] zipfilename directories|filenames
      %s -i listfile zipfilename

-V      Show version
-h      Show usage
-l      Create a listinfo file
-i      Input file list
-b      Specify base directory
""" % (sys.argv[0], sys.argv[0])

def Version():
    print """%s Copyleft GPL
Author: %s
Version: %s""" % (__appname__, __author__, __version__)

if __name__ == '__main__':
#    a = ZFile('d:/aaaa.zip', 'w')
#    a.addfile('d:/a.csv')
#    a.addfile('d:/test/a.JPG')
#    a.addfile('d:/test/mixin/main.py', 'main.py')
#    files = ['d:/a.csv', 'd:/test/a.JPG', ('d:/test/mixin/main.py', 'main.py')]
##    a.addfiles(files)
##    a.close()        
#    create('d:/aaaa.zip', files)
#    a = ZFile('d:/aaaa.zip')
#    a.extract_to('d:/test/aaaa')
#    extract('d:/aaaa.zip', 'd:/test/aaaa/aaaa')
    main()
