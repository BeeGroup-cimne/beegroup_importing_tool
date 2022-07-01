import json

import requests

API_URL = "https://host.manttest.net/MTW_InfraestructuresCAT"


class GMAO:
    def __init__(self, username, password, project):
        self.session_id = self.authenticate(username, password, project)
        self.headers = {"Content-Type": "application/json",
                        "x-manttest-loginid": self.session_id}

    @staticmethod
    def authenticate(username, password, project):
        headers = {"Content-Type": "application/json"}
        body = json.dumps({"username": username, "password": password, "project": project})
        res = requests.post(url=f"{API_URL}/api/loginservice/loginuser", headers=headers, data=body)
        assert res.status_code == 200
        return res.json()

    def logout(self):
        body = json.dumps({})
        requests.post(url=f"{API_URL}/api/loginservice/logout", headers=self.headers, data=body)
        self.session_id = ""
        self.headers = {"Content-Type": "application/json"}

    def find_zones(self, page_size, page_index, modified_from_date, zone_path=""):
        body = {"pagesize": page_size,
                "pageindex": page_index,
                "modifiedfromdate": modified_from_date,
                }

        if zone_path != "":
            body.update({"zonepath": zone_path})

        body = json.dumps(body)
        res = requests.post(url=f"{API_URL}/api/zone/apifindzones", headers=self.headers, data=body)
        assert res.status_code == 200
        return res.json()

    def get_full_zone(self, _id, get_criticalities=True, get_managed_scopes=True, get_operations=True,
                      get_features=True,
                      services=None):

        if services is None:
            services = ['Maintenance', 'Cleaning', 'Gardening']

        body = json.dumps({
            "id": _id,
            "getcriticalities": get_criticalities,
            "getmanagedscopes": get_managed_scopes,
            "getoperations": get_operations,
            "getfeatures": get_features,
            "services": services,
        })

        res = requests.post(url=f"{API_URL}/api/zone/apigetfullzone", headers=self.headers, data=body)
        assert res.status_code == 200
        return res.json()
