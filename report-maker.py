# import the json library so that we can handle json
import json

# show datetime
from datetime import datetime

# read json from products.json to the variable products
data = json.load(open("network_devices.json","r",encoding = "utf-8"))

# create a variable that holds our whole text report
report = ""

# helper function for consistent table rows

def format_row(hostname, vendor, value):
    return (
        " "
        + hostname.ljust(19)
        + vendor.ljust(19)
        + str(value).rjust(10)
        + "\n"
    )

# get company name and last update from JSON

company = data.get("company", "Unknown Company")

last_updated = data.get("last_updated", "Unknown")

#create a list for problematic devices

offline = []
warning = []
low_uptime = []

# initialize counters for device types and offline devices

device_type_counts = {}
offline_type_counts = {}

# loop through the location list
for location in data["locations"]:
    # add the site/'name' of the location to the report
    report += "\n" + location["site"] + "\n"
    # add a list of the host names of the devices 
    # on the location to the report
    for device in location["devices"]:
        report += format_row(device["hostname"], device["vendor"], f"{device['uptime_days']} days")

        # collect problematic devices while looping
        
        if device["status"].lower() == "offline":
            offline.append(device)
            offline_type_counts[device["type"]] = offline_type_counts.get(device["type"], 0) + 1
        
        elif device["status"].lower() == "warning":
            warning.append(device)
        if device["uptime_days"] < 30:
            low_uptime.append(device)

        dtype = device.get("type", "Unknown")

        device_type_counts[dtype] = device_type_counts.get(dtype, 0) + 1

# create an empty summary
summary = ""

# company name, timestamp and summary

summary += "="*35 + "\n"
summary +=  f"NETWORK REPORT - {company}\n"
summary += "="*38 + "\n"

summary += f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"

summary += f"Data last updated: {last_updated}\n\n\n"

summary += "="*41 + "\n"
summary += f"EXECUTIVE SUMMARY\n"
summary += "="*44 + "\n"
summary += f"⚠ Offline devices: {len(offline)}\n"

summary += f"⚠ Warning devices: {len(warning)}\n"

summary += f"⚠ Low uptime (<30 days): {len(low_uptime)}\n\n"

# detailed sections for problematic devices

if offline:
    summary += "="*47 + "\n"
    summary += "OFFLINE DEVICES\n"
    summary += "="*50 + "\n"
    for d in offline:
        summary += format_row(d["hostname"], d["vendor"], "OFFLINE")
    summary += "\n\n"

if warning:
    summary += "="*50 + "\n"
    summary += "WARNING DEVICES\n"
    summary += "="*50 + "\n"
    for d in warning:
        summary += format_row(d["hostname"], d["vendor"], "WARNING")
    summary += "\n\n"

if low_uptime:
    summary += "="*50 + "\n"
    summary += "LOW UPTIME DEVICES (<30 days)\n"
    summary += "="*50 + "\n"
    for d in low_uptime:
        summary += format_row(d["hostname"], d["vendor"], f"{d['uptime_days']} days")
    summary += "\n\n"

# statistics per device type

summary += "="*50 + "\n"
summary += "STATISTICS PER DEVICE TYPE\n"
summary += "="*50 + "\n"

summary += f"{'Device type':19} {'Total':>6} {'Offline':>10}\n"
summary += "="*50 + "\n"

total_devices = sum(device_type_counts.values())
total_offline = sum(offline_type_counts.values())

for dtype, count in device_type_counts.items():
    offline_count = offline_type_counts.get(dtype, 0)
    summary += f"{dtype:17} {count:6} {offline_count:8}\n"

summary += "-"*50 + "\n"
summary += f"{'TOTAL':17} {total_devices:6} {total_offline:8}   ({total_offline/total_devices*100:.1f}% offline) \n\n"
summary += "\n"

# total port usage for switches

summary += "="*40 + "\n"
summary += f"TOTAL PORT USAGE (Switches)\n"
summary += "="*40 + "\n"

total_ports = sum(
    d.get("ports", {}).get("total", 0)
    for loc in data["locations"]
    for d in loc["devices"]
    if d["type"].lower() == "switch"
)

used_ports =sum(
    d.get("ports", {}).get("used", 0)
    for loc in data["locations"]
    for d in loc["devices"]
    if d["type"].lower() == "switch"
)

if total_ports == 0:
    summary += "No port data available in JSON\n\n"
else:
    percent_used = (used_ports / total_ports * 100)
    summary += f"Used: {used_ports} / {total_ports} ports ({percent_used:.1f}%)\n\n\n"

# detailed port usage per switch

summary += f"{'Hostname' :19} {'Total':>6} {'Used':>6} {'Free':>6}\n"

for loc in data["locations"]:
    for d in loc["devices"]:
        if d["type"].lower() == "switch":
            ports = d.get("ports", {})
            total = ports.get("total", 0)
            used = ports.get("used", 0)
            free = ports.get("free", 0)
            summary += f"{d['hostname']:19} {total:6} {used:6} {free:6}\n"

summary += "\n"

# VLAN overview

summary += "="*40 + "\n"
summary += "VLAN OVERVIEW\n"
summary += "="*40 + "\n"
vlans = set()
for loc in data["locations"]:
    for d in loc["devices"]:
        if "vlans" in d:
            vlans.update(d["vlans"])

if vlans:
    summary += "VLANs in use:\n"
    vlans_sorted = sorted(vlans)
    cols = 5

    for i, v in  enumerate(vlans_sorted, 1):
        summary += f"{v:<6}"

        if i % cols == 0:

            summary += "\n"
    summary += "\n\n"

# location overview

summary += "="*50 + "\n"
summary += "LOCATION OVERVIEW\n"
summary += "="*50 + "\n"

summary += f"{'Location':23} {'Total':>6} {'Online':>9} {'Offline':>9}\n"
summary += "-"*50 + "\n"

for loc in data["locations"]:
    devices = loc["devices"]
    total = len(devices)
    offline_count = sum(1 for d in devices if d["status"].lower() == "offline")
    online_count = total - offline_count
    summary += f"{loc['site']:22} {total:6}{online_count:8} {offline_count:8}\n"
summary +=  "\n\n"

# somewhere later in our report add something to summary
summary += "="*50 + "\n"
summary += "This is our basic report:\n"
summary += "="*50 + "\n"

# summary before main report

report = summary + report

# write the report to text file
with open('network_report.txt', 'w', encoding='utf-8') as f:
    f.write(report)