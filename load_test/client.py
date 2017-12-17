class Client :
    def __init__(self,addr):
        self.addr=addr
        self.user_no = None
        
    def get_addr(self):
        return self.addr

    def process_cmd(self, cmd,cmd_info):
        print(cmd)
