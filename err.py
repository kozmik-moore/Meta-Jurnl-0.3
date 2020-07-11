class ErrorManager:
    __message = ''

    @property
    def message(self):
        return self.__message

    @message.setter
    def message(self, m):
        try:
            self.__message = m
            print(m)
        except TypeError:
            print('Message is not of type str')

    def clear_message(self):
        self.message = ''