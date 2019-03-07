"""
Contains classes for security types.
"""

class SecurityScheme(object):
    pass

class APIKey(SecurityScheme):
    def __init__(self, name, location="header"):
        self.name = name
        self.location = location if location in ("query", "header", "cookie") else "header"

    @property
    def type(self):
        return "apiKey"
        
    def spec(self):
        return {
            "type": "apiKey",
            "name": self.name,
            "in": self.location
        }

class HTTP(SecurityScheme):
    Schemes = ['basic', 'bearer', 'digest', 'hoba', 'mutual', 'negotiate', 'oauth', 'scram-sha-1', 
               'scram-sha-256', 'vapid']  #from http://www.iana.org/assignments/http-authschemes/http-authschemes.xhtml
    
    
    def __init__(self, scheme, bearerFormat=None):
        self.scheme = scheme
        if str(scheme).lower() == 'bearer':
            self.bearerFormat = bearerFormat

    @property
    def type(self):
        return "http"
    
    def spec(self):
        sp = {
            "type": "http",
            "scheme": self.scheme,
        }
        if self.bearerFormat:
            sp["bearerFormat"] =  self.bearerFormat
        return sp
    



