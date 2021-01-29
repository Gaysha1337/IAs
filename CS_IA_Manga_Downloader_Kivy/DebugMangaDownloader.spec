# -*- mode: python ; coding: utf-8 -*-
from kivy_deps import sdl2, glew
from kivymd import hooks_path as kivymd_hooks_path

block_cipher = None


a = Analysis(['C:/Users/dimit/Desktop/Cloned_Repos/IAs/CS_IA_Manga_Downloader_Kivy/main.py'],
             pathex=['C:\\Users\\dimit\\Desktop\\Cloned_Repos\\IAs\\CS_IA_Manga_Downloader_Kivy'],
             binaries=[],
             datas=[('C:/Users/dimit/Desktop/Cloned_Repos/IAs/CS_IA_Manga_Downloader_Kivy/DATA', 'DATA/'), ('C:/Users/dimit/AppData/Local/Programs/Python/Python38/Lib/site-packages/pykakasi/data', 'pykakasi/data')],
             hiddenimports=['win32file', 'win32timezone', 'pkg_resources.py2_warn', 'pkg_resources'],
             hookspath=[kivymd_hooks_path],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='Manga Downloader',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False , icon='C:\\Users\\dimit\\Desktop\\Cloned_Repos\\IAs\\CS_IA_Manga_Downloader_Kivy\\Icons\\Manga Downloader Icon.ico')
coll = COLLECT(exe,
               Tree('C:\\Users\\dimit\\Desktop\\Cloned_Repos\\IAs\\CS_IA_Manga_Downloader_Kivy'),
               a.binaries,
               a.zipfiles,
               a.datas,
               *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],
               strip=False,
               upx=True,
               upx_exclude=[],
               name='Manga Downloader')
