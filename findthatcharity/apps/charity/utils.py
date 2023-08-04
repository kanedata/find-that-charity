import re


def regno_to_orgid(regno: str) -> str:
    regno = regno.strip().upper()
    if regno.startswith("GB-"):
        return regno
    if regno.startswith("SC"):
        return "GB-SC-{}".format(regno)
    if regno.startswith("N") or (regno.startswith("1") and len(regno) == 6):
        return "GB-NIC-{}".format(re.sub("[^0-9]", "", regno))
    return "GB-CHC-{}".format(regno)
