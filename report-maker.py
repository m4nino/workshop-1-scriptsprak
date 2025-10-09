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

# counter 

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

summary += "="*80 + "\n"
summary +=  f"NETWORK REPORT - {company}\n"
summary += "="*80 + "\n"

summary += f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"

summary += f"Data last updated: {last_updated}\n\n"

summary +="EXECUTIVE SUMMARY\n"
summary +="==================\n"
summary += f"⚠ Offline devices: {len(offline)}\n"

summary += f"⚠ Warning devices: {len(warning)}\n"

summary += f"⚠ Low uptime (<30 days): {len(low_uptime)}\n\n"

# detailed sections for problematic devices

if offline:
    summary += "="*80 + "\n"
    summary += "OFFLINE DEVICES\n"
    summary += "="*80 + "\n"
    for d in offline:
        summary += format_row(d["hostname"], d["vendor"], "OFFLINE")
    summary += "\n"

if warning:
    summary += "="*80 + "\n"
    summary += "WARNING DEVICES\n"
    summary += "="*80 + "\n"
    for d in warning:
        summary += format_row(d["hostname"], d["vendor"], "WARNING")
    summary += "\n"

if low_uptime:
    summary += "="*80 + "\n"
    summary += "LOW UPTIME DEVICES (<30 days)\n"
    summary += "="*80 + "\n"
    for d in low_uptime:
        summary += format_row(d["hostname"], d["vendor"], f"{d['uptime_days']} days")
    summary += "\n"

# statistics per device type

summary += "="*80 + "\n"
summary += "STATISTICS PER DEVICE TYPE\n"
summary += "="*80 + "\n"
total_devices = sum(device_type_counts.values())
total_offline = sum(offline_type_counts.values())

for dtype, count in device_type_counts.items():
    offline_count = offline_type_counts.get(dtype, 0)

    summary += f"{dtype.capitalize():15} {count:3} st {offline_count} (offline)\n"

summary += "-"*40 + "\n"
summary += f"TOTAL: {total_devices} devices ({total_offline} offline = {total_offline/total_devices*100:.1f}% offline)\n\n"

# somewhere later in our report add something to summary
summary += "\n"
summary += "This is our basic report:\n"

# summary before main report

report = summary + report

# write the report to text file
with open('network_report.txt', 'w', encoding='utf-8') as f:
    f.write(report)