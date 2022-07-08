import json
from time import sleep
from typing import List

import requests
from requests import HTTPError

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
    def authenticate(username: str, password: str, project: str):
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

    def find_zones(self, modified_from_date: str = None, zone_path: str = None, page_size: int = 100,
                   page_index: int = 0):
        body = json.dumps({"pagesize": page_size,
                           "pageindex": page_index,
                           "modifiedfromdate": modified_from_date,
                           "zonepath": zone_path
                           })

        return self.check_response(requests.post,
                                   {"url": f"{API_URL}/api/zone/apifindzones", "headers": self.headers, "data": body})

    def get_full_zone(self, id: str, get_criticalities: bool = True, get_managed_scopes: bool = True,
                      get_operations: bool = True,
                      get_features: bool = True,
                      services: List[str] = None):

        if services is None:
            services = ['Maintenance', 'Cleaning', 'Gardening']

        body = json.dumps({
            "id": id,
            "getcriticalities": get_criticalities,
            "getmanagedscopes": get_managed_scopes,
            "getoperations": get_operations,
            "getfeatures": get_features,
            "services": services,
        })

        return self.check_response(requests.post,
                                   {"url": f"{API_URL}/api/zone/apigetfullzone", "headers": self.headers, "data": body})

    def find_assets(self, modified_from_date: str = None, zone_path: str = None, page_size: int = 100,
                    page_index: int = 0):
        body = {"pagesize": page_size,
                "pageindex": page_index,
                "modifiedfromdate": modified_from_date,
                "zonepath": zone_path
                }

        body = json.dumps(body)
        return self.check_response(requests.post,
                                   {"url": f"{API_URL}/api/inventory/apifindassets", "headers": self.headers,
                                    "data": body})

    def get_full_asset(self, id: int, get_feature: str = True):
        body = json.dumps({"id": id, "getfeatures": get_feature})

        return self.check_response(requests.post,
                                   {"url": f"{API_URL}/api/inventory/apigetfullasset", "headers": self.headers,
                                    "data": body})

    def find_indicator_values(self, service: List[str] = None, searchtext: str = None, fromdate: str = None,
                              todate: str = None,
                              indicatorid=None,
                              managedscopeid=None, zoneid=None, zonepath=None, page_size: int = 100,
                              page_index: int = 0):

        if service is None:
            service = ['Maintenance']

        body = json.dumps(
            {
                "service": service,
                "searchtext": searchtext,
                "pagesize": page_size,
                "pageindex": page_index,
                "fromdate": fromdate,
                "todate": todate,
                "indicatorid": indicatorid,
                "managedscopedid": managedscopeid,
                "zoneid": zoneid,
                "zonepath": zonepath
            })

        body = json.dumps(body)
        return self.check_response(requests.post,
                                   {"url": f"{API_URL}/api/workorder/apifindindicatorvalues", "headers": self.headers,
                                    "data": body})

    def find_work_orders(self, service: str = None, modifiedfromdate: str = None, fromorderdate: str = None,
                         searchtext: str = None, toorderdate: str = None,
                         zoneid: str = None, zonepath: str = None, page_size: int = 100, page_index: int = 0,
                         statusids: List[str] = None, worktypes: List[str] = None):
        if service is None:
            service = 'Maintenance'

        body = json.dumps({
            "service": service,
            "searchtext": searchtext,
            "pagesize": page_size,
            "pageindex": page_index,
            "modifiedfromdate": modifiedfromdate,
            "fromorderdate": fromorderdate,
            "toorderdate": toorderdate,
            "zoneid": zoneid,
            "zonepath": zonepath,
            "statusids": statusids,
            "worktypes": worktypes
        })

        return self.check_response(requests.post,
                                   {"url": f"{API_URL}/api/workorder/apifindworkorders", "headers": self.headers,
                                    "data": body})

    def get_full_work_order(self, id: str, getelementlist: bool = True, gettrasklist: bool = True,
                            gettimelist: bool = True, getfeatures: bool = True):
        body = json.dumps(
            {"id": id, "getfeatures": getfeatures, "getelementlist": getelementlist, "gettrasklist": gettrasklist,
             "gettimelist": gettimelist})

        return self.check_response(requests.post,
                                   {"url": f"{API_URL}/api/workorder/apigetfullworkorder", "headers": self.headers,
                                    "data": body})

    def get_total_pages(self, fn_name: str) -> int:
        fn = getattr(self, fn_name)
        return fn(page_size=1, page_index=0)['totalpages']

    def check_response(self, fn, args=None):
        if args is None:
            args = {}

        try:
            res = fn(**args)

            if res.status_code != 200:
                self.login()
                sleep(3)
                res = fn(**args)

            return res.json()
        except HTTPError as ex:
            print(ex)
