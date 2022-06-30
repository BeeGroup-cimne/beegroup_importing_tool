import requests

API_URL = ""


class GMAO:
    def __init__(self, username, password, project):
        self.session_id = self.authenticate(username, password, project)
        self.headers = {"Content-Type": "application/json",
                        "X-ManTest-LoginId": self.session_id}

    @staticmethod
    def authenticate(username, password, project):
        headers = {"Content-Type": "application/json"}
        body = {"username": username, "password": password, "project": project}
        res = requests.post(url=f"{API_URL}/api/loginservice/LoginUser", headers=headers, data=body)
        assert res.status_code == 200
        return res.json()

    def logout(self):
        body = {}
        requests.post(url=f"{API_URL}/api/loginservice/Logout", headers=self.headers, data=body)
        self.session_id = ""

    def find_zones(self, page_size, page_index, modified_from_date, zone_path):
        body = {"pagesize": page_size,
                "pageindex": page_index,
                "modifiedfromdate": modified_from_date,
                "zonepath": zone_path
                }
        res = requests.post(url=f"{API_URL}/api/zone/APIFindZones", headers=self.headers, data=body)
        assert res.status_code == 200
        return res.json()
