import argparse

from dexma.device import Device


def gather_devices():
    d = Device()
    res = d.get_devices({"start": 0})

    assert res.status_code == 200
    has_next = True

    while has_next:
        pass

    for dev in res.json():
        print(dev)


def gather(arguments, settings, config):
    ap = argparse.ArgumentParser()
    ap.add_argument("--user", "-u", help="The user importing the data", required=True)
    ap.add_argument("--namespace", "-n", help="The subjects namespace uri", required=True)
    ap.add_argument("-st", "--store", required=True, help="Where to store the data", choices=["kafka", "hbase"])

    ap.add_argument("-k", "--kind_of_data", required=True, help="Where to store the data",
                    choices=["devices", "location", "parameter", "supplies", "reading", "all"])
    args = ap.parse_args(arguments)

    if args.kind_of_data == "devices" or args.kind_of_data == "all":
        gather_devices(arguments, settings, config)
