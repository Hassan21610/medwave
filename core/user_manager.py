class UserManager:
    def __init__(self):
        self.users = ["Dr. A", "Dr. B", "Dr. C"]
        self.idx = -1

    def login_next(self):
        self.idx = (self.idx + 1) % len(self.users)
        return self.users[self.idx]
