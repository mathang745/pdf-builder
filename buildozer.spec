[app]
title = Booklet Studio Pro
package.name = bookletstudio
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3,kivy==2.2.1,pypdf
python_version = 3.10
orientation = portrait
fullscreen = 0
android.archs = arm64-v8a
android.accept_sdk_license = True
android.api = 33
android.minapi = 21
android.ndk_api = 21

[buildozer]
log_level = 2
warn_on_root = 1
