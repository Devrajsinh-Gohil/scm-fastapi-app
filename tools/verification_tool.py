import requests
from requests.auth import HTTPBasicAuth
from agno.tools import tool
from dotenv import load_dotenv
from agno.tools import tool
from typing import Any, Callable, Dict
import os

# Load environment variables from .env file
load_dotenv()

def get_carrier_list():
    """Fetch carrier list from SAP API"""
    try:
        r = requests.get(
            "https://s4hana.scmchamps.com:8006/sap/opu/odata/sap/ZDOCK_APPOINTMENT_CARRIER_LIST_SRV/ZDOCK_SLOT_CARRIERSet?$format=json",
            auth=HTTPBasicAuth(
                os.getenv('SAP_USER'), 
                os.getenv('SAP_PASS')
            ),
            verify=False
        )
        r.raise_for_status()
        
        return [{
            'PartnerID': s.get('Businesspartner', '').strip(),
        } for s in r.json()['d']['results']]
        
    except:
        return None
    
def logger_hook(function_name: str, function_call: Callable, arguments: Dict[str, Any]):
    """Hook function that wraps the tool execution"""
    print(f"About to call {function_name} with arguments: {arguments}")
    result = function_call(**arguments)
    print(f"Function call completed with result: {result}")
    return result
    
@tool(
    name="verify_id_tool",
    description="Verify if a carrier exists in the list by PartnerID.",
    show_result=False,
    stop_after_tool_call=False,
    tool_hooks=[logger_hook],
)
def verify(partner_id:str) -> bool:
    """
    Checks if the given partner_id exists in the carrier list.
    Args:
        partner_id (str): The unique identifier of the partner to verify.
    Returns:
        bool: True if the partner_id exists in the carrier list, False otherwise.
    """
    carrier_list = get_carrier_list()
    if not carrier_list:
        return False
    
    for carrier in carrier_list:
        if carrier['PartnerID'] == partner_id:
            return True
    return False