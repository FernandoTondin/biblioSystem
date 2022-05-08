
class database_acces:
    def __init__(self):
        self.host = ""
        self.port = ""
        self.user = ""
        self.password = ""
        self.database = ""
        self.localHost = "localhost"
        self.localUser = "root"
        self.localPassword = ""
        self.local = True
    
    def get_host(self):
        if self.local:
            return self.localHost
        return self.host


    def get_port(self):
        return self.port


    def get_user(self):
        if self.local:
            return self.localUser
        return self.user


    def get_password(self):
        if self.local:
            return self.localPassword
        return self.password


    def get_database(self):
        return self.database