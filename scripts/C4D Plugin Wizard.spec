# -*- mode: python -*-
import os, sys, shutil, logging
logging.basicConfig(filename=(os.path.join(os.curdir, 'build.log')),level=logging.DEBUG)
home = os.environ['HOME']

# USER CONFIG
# adjust these paths to match your system
if sys.platform == "win32":
    base = home + r"\Documents\Eclipse\Projects\Python\C4D Plugin Wizard"
    pyinst2_root = home + '/source/python/pyinstaller-2.0'
elif sys.platform == "darwin":
    base = home + "/Documents/Eclipse/Workspaces/Python/C4D Plugin Wizard"
    pyinst2_root = home + '/source/pyinstaller-2.0'
# END USER CONFIG

def to_unix_path(p):
    return p.replace(r'\\', '/')

base = to_unix_path(base)
pyinst2_root = to_unix_path(pyinst2_root)

a = Analysis(
    [base + '/source/gui.py'],
    pathex=[
        base + '/source/gui.py', 
        base + '/source/c4dplugwiz.py', 
        pyinst2_root
    ],
    hiddenimports=[],
    hookspath=[base + '/support/pyinstaller/hooks'],
)
pyz = PYZ(a.pure)

if sys.platform == "win32":
    outdir = os.path.join(base, 'dist', 'win')
    
    exe = EXE(pyz,
              a.scripts,
              a.binaries,
              a.zipfiles,
              a.datas,
              name=os.path.join(outdir, 'CINEMA 4D Plugin Wizard.exe'),
              debug=False,
              strip=None,
              upx=True,
              console=False, 
              icon=(base + '/source/res/c4dapp.ico'))
    
elif sys.platform == "darwin":
    outdir = os.path.join(base, 'dist', 'osx')
    
    exe = EXE(pyz,
          a.scripts,
          # possible fix for http://github.com/andreberg/C4D-Plugin-Wizard/issues/1
          # see also: http://www.pyinstaller.org/ticket/595
          a.binaries + [('libQtCLucene.4.dylib',
                         '/usr/lib/libQtCLucene.4.dylib',
                         'BINARY')],
          a.zipfiles,
          a.datas,
          name=os.path.join(outdir, 'CINEMA 4D Plugin Wizard'),
          debug=False,
          strip=None,
          upx=True,
          console=True, 
          icon=(base + '/source/res/c4dapp.icns'))
    
    app = BUNDLE(exe, name=os.path.join(outdir, 'CINEMA 4D Plugin Wizard.app'))
    
try:
    shutil.rmtree(os.path.join(outdir, 'c4dplugwiz_data'))
    shutil.rmtree(os.path.join(outdir, 'images'))
except Exception as e:
    logging.warning('Exception: %s' % str(e))

try:
    shutil.copytree(base + '/source/c4dplugwiz_data', os.path.join(outdir, 'c4dplugwiz_data'))
    shutil.copytree(base + '/source/images', os.path.join(outdir, 'images'))
except Exception as e:
    logging.warning('Exception: %s' % str(e))
