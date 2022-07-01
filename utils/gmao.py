import json

import requests

API_URL = "https://host.manttest.net/MTW_InfraestructuresCAT"


class GMAO:
    def __init__(self, username, password, project):
        self.username = username
        self.password = password
        self.project = project
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

    def login(self):
        self.session_id = self.authenticate(self.username, self.password, self.project)
        self.headers = {"Content-Type": "application/json",
                        "x-manttest-loginid": self.session_id}

    def logout(self):
        body = json.dumps({})
        requests.post(url=f"{API_URL}/api/loginservice/logout", headers=self.headers, data=body)
        self.session_id = ""
        self.headers = {"Content-Type": "application/json"}

    def find_zones(self, modified_from_date, page_size=100, page_index=0, zone_path=None):
        body = {"pagesize": page_size,
                "pageindex": page_index,
                "modifiedfromdate": modified_from_date,
                }

        if zone_path is not None:
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

    def find_assets(self, modified_from_date, page_size=100, page_index=0, zone_path=""):
        body = {"pagesize": page_size,
                "pageindex": page_index,
                "modifiedfromdate": modified_from_date,
                }

        if zone_path != "":
            body.update({"zonepath": zone_path})

        body = json.dumps(body)
        res = requests.post(url=f"{API_URL}/api/inventory/apifindassets", headers=self.headers, data=body)
        assert res.status_code == 200
        return res.json()

    def get_full_asset(self, _id, get_feature=True):
        body = json.dumps({"id": _id, "getfeatures": get_feature})

        res = requests.post(url=f"{API_URL}/api/inventory/apigetfullasset", headers=self.headers, data=body)
        assert res.status_code == 200
        return res.json()

    def find_indicator_values(self, service, fromdate, searchtext=None, todate=None, indicatorid=None,
                              managedscopeid=None, zoneid=None, zonepath=None, pagesize=100, pageindex=0):
        body = {}
        if service is None:
            service = ['Maintenance', 'Cleaning', 'Gardening']

        if searchtext is not None:
            body.update({"searchtext": searchtext})

        if todate is not None:
            body.update({"todate": todate})

        if fromdate is not None:
            body.update({"fromdate": fromdate})

        if indicatorid is not None:
            body.update({"indicatorid": indicatorid})

        if managedscopeid is not None:
            body.update({"managedscopeid": managedscopeid})

        if zoneid is not None:
            body.update({"zoneid": zoneid})

        if zonepath is not None:
            body.update({"zonepath": zonepath})

        if zonepath is not None:
            body.update({"zonepath": zonepath})

        body.update(
            {
                "service": service,
                "pagesize": pagesize,
                "pageindex": pageindex,
            })

        body = json.dumps(body)
        res = requests.post(url=f"{API_URL}/api/workorder/apifindindicatorvalues", headers=self.headers, data=body)
        assert res.status_code == 200
        return res.json()

    def find_work_orders(self, service, modifiedfromdate=None, fromorderdate=None, searchtext=None, toorderdate=None,
                         indicatorid=None,
                         zoneid=None, zonepath=None, pagesize=100, pageindex=0,
                         statusids=None, worktypes=None):
        body = {}

        if modifiedfromdate is not None:
            body.update({"modifiedfromdate": modifiedfromdate})

        if fromorderdate is not None:
            body.update({"fromorderdate": fromorderdate})

        if searchtext is not None:
            body.update({"searchtext": searchtext})

        if toorderdate is not None:
            body.update({"toorderdate": toorderdate})

        if indicatorid is not None:
            body.update({"indicatorid": indicatorid})

        if zoneid is not None:
            body.update({"zoneid": zoneid})

        if zonepath is not None:
            body.update({"zonepath": zonepath})

        if statusids is not None:
            body.update({"statusids": statusids})

        if worktypes is not None:
            body.update({"worktypes": worktypes})

        body.update({"pagesize": pagesize, "pageindex": pageindex, "service": service})

        body = json.dumps(body)

        res = requests.post(url=f"{API_URL}/api/workorder/apifindworkorders", headers=self.headers, data=body)
        assert res.status_code == 200
        return res.json()

    def get_full_work_order(self, _id, getelementlist=True, gettrasklist=True, gettimelist=True, getfeatures=True):
        body = json.dumps(
            {"id": _id, "getfeatures": getfeatures, "getelementlist": getelementlist, "gettrasklist": gettrasklist,
             "gettimelist": gettimelist})

        res = requests.post(url=f"{API_URL}/api/workorder/apigetfullworkorder", headers=self.headers, data=body)
        assert res.status_code == 200
        return res.json()
