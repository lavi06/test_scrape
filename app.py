
import requests
import json, os
import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup

################################################################################



st.set_page_config(page_title="Process File", page_icon=":bar_chart:")
# st.image("Logo.png", caption=None, width=250, use_column_width=None, clamp=False, channels="RGB", output_format="auto")


_map = {
    "A05" : "Active",
    "A09" : "Cancelled",
    "A13" : "Withdrawn",
    "A54" : "Forced",
    "A53" : "Planned",
    "PU"  : "Production unit",
    "GU"  : "Generation unit"
    }

headers = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'en-GB,en;q=0.9',
    'Connection': 'keep-alive',
    'Content-Type': 'application/json;charset=UTF-8',
    'Origin': 'https://transparency.entsoe.eu',
    'Referer': 'https://transparency.entsoe.eu/outage-domain/r2/unavailabilityOfProductionAndGenerationUnits/show?name=&defaultValue=false&viewType=TABLE&areaType=CTA&atch=false&dateTime.dateTime=01.02.2020+00:00%7CUTC%7CDAY&dateTime.endDateTime=27.05.2024+00:00%7CUTC%7CDAY&area.values=CTY%7C10YHU-MAVIR----U!CTA%7C10YHU-MAVIR----U&assetType.values=PU&assetType.values=GU&outageType.values=A54&outageType.values=A53&outageStatus.values=A05&masterDataFilterName=&masterDataFilterCode=&dv-datatable_length=10',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
    'sec-ch-ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
}


def update_json(results):
    try:
        with open("Results.json", "r") as f:
            data = json.load(f)
    except:
        data = []

    data += results

    with open("Results.json", "w") as f:
        json.dump(data, f, indent = 3)


    val = f"Updated Results : {len(data)}"
    print(val)
    st.session_state.terminal += "\n" + val

def parse():
    filename = "Results.json"
    results = []
    with open("Results.json", "r") as f:
        data = json.load(f)

    for each in data:

        Status = _map.get(each[0], each[0])
        Nature = _map.get(each[1], each[1])

        Type = each[2]
        Unavailability_period = each[3]
        Area = each[4]
        Unit      = each[5]
        Installed = each[6]
        Available = each[7]

        try:
            Installed = BeautifulSoup(Installed, "html.parser").text
        except:
            pass
        try:
            Available = BeautifulSoup(Available, "html.parser").text
        except:
            pass

        results.append([Status,Nature,Type,Unavailability_period,Area,Unit,Installed,Available])


    if len(results) == 0:
        print("")
        print("No Records to Save..")
        print("Please try again later..")
        print("")
    else:
        file_path = filename.replace(".json",".xlsx")
        df = pd.DataFrame(results, columns = ["Status","Nature","Type","Unavailability_period","Area","Unit","Installed","Available"])

        df.to_excel(file_path, index = False)
        print("")
        print(f"File Saved to -> {file_path}")

    try:
        print("Removing Cache")
        os.remove(filename)
    except:
        print("Error Removing Cache")


def scrape_website():

    url = st.session_state.url

    # url = "https://transparency.entsoe.eu/outage-domain/r2/unavailabilityOfProductionAndGenerationUnits/show?name=&defaultValue=true&viewType=TABLE&areaType=CTA&atch=false&dateTime.dateTime=30.05.2024+00:00%7CUTC%7CDAY&dateTime.endDateTime=01.06.2024+00:00%7CUTC%7CDAY&CTY%7C10YHU-MAVIR----U%7CMULTI=CTY%7C10YHU-MAVIR----U%7CMULTI&area.values=CTY%7C10YHU-MAVIR----U!CTA%7C10YHU-MAVIR----U&assetType.values=PU&assetType.values=GU&outageType.values=A54&outageType.values=A53&outageStatus.values=A05&masterDataFilterName=&masterDataFilterCode=&dv-datatable_length=10"
    url = url.replace("/show","/getDataTableData")

    # st.session_state.terminal += "\n" + url

    offset = 0
    limit = 100

    while offset >= 0 and offset < 5000:

        val = f"Page : {offset/100 + 1}"
        print(val)
        st.session_state.terminal += "\n" + val

        json_data = {
            'sEcho': 1,
            'iColumns': 9,
            'sColumns': 'status,outageType,assetType,startDate,area,assetName,installedCapacity,availableCapacity,',
            'iDisplayStart': offset,
            'iDisplayLength': limit,
            'amDataProp': [0,1,2,3,4,5,6,7,8,],
        }
        response = requests.post(
            url,
            headers=headers,
            json = json_data,
        )

        data = response.json()

        results = data["aaData"]
        update_json(results)

        offset += limit

        if data["iTotalRecords"] > offset:
            pass
        else:
            offset = -1

    if offset >= 500:
        val = f"------ Limited to 500 Results ------"
        st.session_state.terminal += "\n\n" + val + "\n"


    val = f"------ Scrape Completed ------"
    st.session_state.terminal += "\n\n" + val + "\n"

    parse()

    val = f"------ File Ready to Download ------"
    st.session_state.terminal += "\n\n" + val + "\n"

    st.session_state.check = False


if "terminal" not in st.session_state:
    st.session_state.terminal = ""

if "check" not in st.session_state:
    st.session_state.check = True


url = st.text_input("URL", key = "url")
process = st.button("Scrape Results", on_click = scrape_website)


st.text_area("Terminal - Output", value = st.session_state.terminal, height = 400)

try:
    with open('Results.xlsx', 'rb') as f:
        data = f.read()
except:
    data = None

st.download_button(label='Download File', data = data, file_name='Results.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', disabled = st.session_state.check)





