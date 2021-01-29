# -*- mode: python ; coding: utf-8 -*-
from kivy_deps import sdl2, glew
from kivymd import hooks_path as kivymd_hooks_path
from kivy.tools.packaging.pyinstaller_hooks import get_deps_minimal, get_deps_all, hookspath, runtime_hooks

block_cipher = None

added_files = [
    ('DATA', 'DATA'), 
    ('C:/Users/dimit/AppData/Local/Programs/Python/Python38/Lib/site-packages/pykakasi/data', 'pykakasi/data'),
    ('C:\\Users\\dimit\\Desktop\\Cloned_Repos\\IAs\\CS_IA_Manga_Downloader_Kivy\\settings.json','.')
]


a = Analysis(['C:\\Users\\dimit\\Desktop\\Cloned_Repos\\IAs\\CS_IA_Manga_Downloader_Kivy\\main.py'],
             pathex=[
                'C:\\Users\\dimit\\Desktop\\Cloned_Repos\\IAs\\CS_IA_Manga_Downloader_Kivy',
                'C:\\Users\\dimit\\AppData\\Local\\Programs\\Python\\Python38\\Lib\\site-packages\\pykakasi'
            ],
             binaries=[],
             datas=added_files,
             hiddenimports=['win32file','win32timezone','pkg_resources.py2_warn', 'pkg_resources'],
             hookspath=[kivymd_hooks_path],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

#a.datas += Tree('C:\\Users\\dimit\\AppData\\Local\\Programs\\Python\\Python38\\Lib\\site-packages\\pykakasi')


pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          Tree('C:\\Users\\dimit\\Desktop\\Cloned_Repos\\IAs\\CS_IA_Manga_Downloader_Kivy'),
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],
          name='Manga Downloader',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False,
          icon='Icons\\Manga Downloader Icon.ico')
