import requests
from requests.auth import HTTPBasicAuth
import os
from dotenv import load_dotenv
from tools.get_slots_tool import get_creds
import json
from typing import Any, Callable, Dict
import xmltodict
from agno.tools import tool

load_dotenv()

def format_cookie(s):
    c = dict(i.strip().split('=', 1) for i in s.replace(',', ';').split(';') if '=' in i and 'path' not in i and 'HttpOnly' not in i)
    return f"SAP_SESSIONID_S4H_100={c['SAP_SESSIONID_S4H_100']}; sap-usercontext={c['sap-usercontext']}"

def get_doc_no(guid:str):
    r_d = requests.get(
            f"https://s4hana.scmchamps.com:8006/sap/opu/odata/sap/ZSCWM_DAS_CARRIER_ACCESS_SRV/AppointmentSet(guid'{guid}')",
            auth=HTTPBasicAuth(os.getenv('SAP_USER'), os.getenv('SAP_PASS')),
            verify=False
    )
    r_d_json = json.loads(json.dumps(xmltodict.parse(r_d.text),indent=4))
    doc_no = r_d_json["entry"]["content"]["m:properties"]["d:Docno"]
    print(f"Document number retrieved: {doc_no}")
    return doc_no

def logger_hook(function_name: str, function_call: Callable, arguments: Dict[str, Any]):
    """Hook function that wraps the tool execution"""
    print(f"About to call {function_name} with arguments: {arguments}")
    result = function_call(**arguments)
    print(f"Function call completed with result: {result}")
    return result

@tool(
    name="create_appointment",
    description="Create a dock appointment via SAP API.",
    show_result=False,
    stop_after_tool_call=False,
    tool_hooks=[logger_hook],
)
def create_appointment(loadpoint:str, carrier:str, req_start_time:str) -> str:
    """
    Creates a dock appointment via the SAP API.
    Args:9
        loadpoint (str): The load point identifier for the appointment.
        carrier (str): Business partner id .
        req_start_time (str): The requested start time for the appointment in ISO 8601 (%Y-%m-%dT%H:%M:%SZ) format.
    Returns:
        str: The appointment reference if the appointment is successfully created, otherwise None.
    """
    try:
        print(f"Creating appointment for Loadpoint: {loadpoint}, Carrier: {carrier}, Start Time: {req_start_time}")
        header = get_creds("23062025") # Fetch CSRF token by getting dock slots
        csrf = header[0] if header else None
        cookie = header[1] if header else None
        
        if not csrf:
            print("Failed to get CSRF token")
            return None
        
        cookies = format_cookie(cookie) if cookie else None
            
        r = requests.post(
            "https://s4hana.scmchamps.com:44303/sap/opu/odata/sap/ZSCWM_DAS_CARRIER_ACCESS_SRV/AppointmentSet",
            auth=HTTPBasicAuth(os.getenv('SAP_USER'), os.getenv('SAP_PASS')),
            headers={
                'x-csrf-token': csrf,
                'Cookie': cookies,
            },
            json={
                "Loadpoint": loadpoint,  # Use actual parameters
                "Carrier": carrier,
                "Mtr": 'TRCK',
                "ReqStartTime": req_start_time
            },
            verify=False
        )
        print(f"Request URL: {r.url}")
        r.raise_for_status()
        print(f"Response status code: {r.status_code}")
        r_json = json.loads(json.dumps(xmltodict.parse(r.text),indent=4))
        print(f"Response JSON: {r_json}")
        return get_doc_no(r_json["entry"]["content"]["m:properties"]["d:AppointmentKey"])
        
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        print(f"Response status: {r.status_code if 'r' in locals() else 'No response'}")
        print(f"Response text: {r.text if 'r' in locals() else 'No response'}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None
    
def get_doc_no(guid:str):
    r_d = requests.get(
            f"https://s4hana.scmchamps.com:8006/sap/opu/odata/sap/ZSCWM_DAS_CARRIER_ACCESS_SRV/AppointmentSet(guid'{guid}')",
            auth=HTTPBasicAuth(os.getenv('SAP_USER'), os.getenv('SAP_PASS')),
            verify=False
    )
    r_d_json = json.loads(json.dumps(xmltodict.parse(r_d.text),indent=4))
    doc_no = r_d_json["entry"]["content"]["m:properties"]["d:Docno"]
    print(f"Document number retrieved: {doc_no}")
    return doc_no