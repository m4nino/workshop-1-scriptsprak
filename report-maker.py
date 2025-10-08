# import the json library so that we can handle json
import json

# show datetime
from datetime import datetime

# read json from products.json to the variable products
data = json.load(open("network_devices.json","r",encoding = "utf-8"))

# create a variable that holds our whole text report
report = ""

# get company name and last update from JSON

company = data.get("company", "Unknown Company")

last_updated = data.get("last_updated", "Unknown")

#create a list for problematic devices

offline = []

warning = []

low_uptime = []

# loop through the location list
for location in data["locations"]:
    # add the site/'name' of the location to the report
    report += "\n" + location["site"] + "\n"
    # add a list of the host names of the devices 
    # on the location to the report
    for device in location["devices"]:
        report += (" " 
                 + device["hostname"].ljust(19,' ') + ' '
                 + device["vendor"].ljust(19) + ' '
                 + str(device["uptime_days"]).rjust(4)
                 + "\n"
                 )
        # collect problematic devices while looping
        
        if device["status"].lower() == "offline":
         
            offline.append(device)
        elif device["status"].lower() == "warning":
         
            warning.append(device)
        if device["uptime_days"] < 30:

            low_uptime.append(device)

# create an empty summary
summary = ""

# add company name, timestamp and summary

summary += "="*80 + "\n"

summary +=  f"NETWORK REPORT - {company}\n"

summary += "="*80 + "\n"

summary += f"Report generated: {datetime.now().strftime('%y-%m-%d %H:%M')}\n"

summary += f"Data last updated: {last_updated}\n\n"

summary +="EXECUTIVE SUMMARY\n"
summary +="-----------------\n"
summary += f"⚠ Offline devices: {len(offline)}\n"

summary += f"⚠ Warning devices: {len(warning)}\n"

summary += f"⚠ Low uptime (<30 days): {len(low_uptime)}\n\n"

# somewhere later in our report add something to summary
summary += "summary:\n"
summary += "This is our basic report:\n"

# add summary before main report
report = summary + report

# write the report to text file
with open('network_report.txt', 'w', encoding='utf-8') as f:
    f.write(report)