import requests

API_URL = ""


class GMAO:
    def __init__(self, username, password, project):
        self.session_id = self.authenticate(username, password, project)

    @staticmethod
    def authenticate(username, password, project):
        headers = {"Content-Type": "application/json"}
        body = {"username": username, "password": password, "project": project}
        res = requests.post(url=f"{API_URL}/api/loginservice/LoginUser", headers=headers, data=body)
        assert res.status_code == 200
        return res.json()
