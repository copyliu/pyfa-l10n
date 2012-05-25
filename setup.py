# coding=big5
# +----------------------------------------+
# |Author: Lau Gin San (CopyLiu)           |
# |Email:copyliu@gmail.com                 |
# |Verson : 0.0.2                          |
# |                                        |
# |License:GPLv2.0                         |
# +----------------------------------------+
from distutils.core import setup
import py2exe

includes = ["encodings", "encodings.*"]
options = {"py2exe":
            {   "compressed": 1,
                "optimize": 2,
                "includes": includes,
                "bundle_files": 3,
                "dll_excludes": ["MSVCP90.dll"]

            }
          }
setup(   

    version = "0.1",
    description = u"pyfa",
    name = u"pyfa",
	author =u"pyfa",
    options = options,
    zipfile=None,
    windows=[{"script": "pyfa.py",#"icon_resources":[(1,"wx.ico")],
              #'uac_info': "requireAdministrator",

	#"resources":[(1,"wx.ico")]
    }],
)
