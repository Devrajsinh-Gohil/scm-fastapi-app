import os
import requests
from agno.tools import tool
from dotenv import load_dotenv
from typing import Any, Callable, Dict
from requests.auth import HTTPBasicAuth

# Load environment variables from .env file
load_dotenv()

def logger_hook(function_name: str, function_call: Callable, arguments: Dict[str, Any]):
    """Hook function that wraps the tool execution"""
    print(f"About to call {function_name} with arguments: {arguments}")
    result = function_call(**arguments)
    print(f"Function call completed with result: {result}")
    return result


@tool(
    name="get_dock_slots",
    description="Get dock appointment slots from SAP system for a user requested date date.",
    tool_hooks=[logger_hook],
    show_result=False,
    stop_after_tool_call=False,
)
def get_dock_slots(date_ddmmyyyy:str):
    """
    Get dock appointment slots from SAP system for a user requested date date.
    
    Args:
        date_ddmmyyyy (str): Date in DDMMYYYY format (e.g., "23062025")
        flag (bool): If True, returns slot data; if False, returns auth tokens. Defaults to True.
    
    Returns:
        list or tuple or None: Dock slots data, auth tokens, or None if failed
    """
    if len(date_ddmmyyyy) != 8 or not date_ddmmyyyy.isdigit():
        return None
    
    try:
        r = requests.get(
            f"https://s4hana.scmchamps.com:8006/sap/opu/odata/sap/ZDOCK_APPOINTMENT_SLOT_TIME_SRV/ZDOCK_SLOT_TIMESet?$filter=CurrDate%20eq%20%27{date_ddmmyyyy}%27&$format=json",
            auth=HTTPBasicAuth(os.getenv('SAP_USER'), os.getenv('SAP_PASS')),
            verify=False
        )
        r.raise_for_status()
        

        
        return [{
            'StartTime': s.get('StartTime', '').strip()[8:-4],
            'EndTime': s.get('FinishTime', '').strip()[8:-4],
            'Capacity': s.get('Capacity', 0),
            'Loadpoint': s.get('Loadpoint', '')
        } for s in r.json()['d']['results']]
            
        
        
    except:
        return None
    
    
def get_creds(date_ddmmyyyy:str):
    """
    Get dock appointment slots from SAP system for a user requested date date.
    
    Args:
        date_ddmmyyyy (str): Date in DDMMYYYY format (e.g., "23062025")
        flag (bool): If True, returns slot data; if False, returns auth tokens. Defaults to True.
    
    Returns:
        list or tuple or None: Dock slots data, auth tokens, or None if failed
    """
    if len(date_ddmmyyyy) != 8 or not date_ddmmyyyy.isdigit():
        return None
    
    try:
        r = requests.get(
            f"https://s4hana.scmchamps.com:8006/sap/opu/odata/sap/ZDOCK_APPOINTMENT_SLOT_TIME_SRV/ZDOCK_SLOT_TIMESet?$filter=CurrDate%20eq%20%27{date_ddmmyyyy}%27&$format=json",
            auth=HTTPBasicAuth(os.getenv('SAP_USER'), os.getenv('SAP_PASS')),
            headers={
                'x-csrf-token': 'fetch',
            },
            verify=False
        )
        r.raise_for_status()
    
        return (r.headers.get('x-csrf-token', None),r.headers.get('set-cookie', None))
        
    except:
        return None