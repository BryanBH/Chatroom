import PyQt5.QtWidgets


class QConsole(PyQt5.QtWidgets.QTextBrowser):
    def print_message(self, message):
        self.insertHtml('{}<br>'.format(message))
        self.update()  # This isn't ideal but it works

    def print_user_message(self, message, user):
        self.insertHtml('<b>{}:</b> {}<br>'.format(user, message))
        self.update()
