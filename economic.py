class CookiesCount:

    def __init__(self, user, cookies):
        self.user = user
        self.cookies = cookies

    def __repr__(self):
        return f'<@{self.user}> с кол-вом {self.cookies} фисташек!'