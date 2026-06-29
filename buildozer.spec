[app]
title = Equipment Lending Mobile
package.name = equipmentlending
package.domain = hk.serena
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,md
version = 0.1

requirements = python3==3.11.7,kivy==2.3.0,kivymd==1.1.1

orientation = portrait
fullscreen = 0

android.permissions = INTERNET,NFC
android.api = 33
android.minapi = 24
android.archs = arm64-v8a,armeabi-v7a
android.accept_sdk_license = True

p4a.bootstrap = sdl2

[buildozer]
log_level = 2
warn_on_root = 1
