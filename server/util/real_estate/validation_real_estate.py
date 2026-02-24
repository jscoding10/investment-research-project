import os
import requests
from util.logger import get_logger
from models.real_estate.state_real_estate import RealEstateResearchState

logger = get_logger(__name__)

def validate_address(address: str, state: RealEstateResearchState) -> dict:
    if not address or len(address.strip()) < 10:
        logger.warning(f"Invalid format: {address}")
        return {"is_address_valid": False}

    try:
        headers = {
            'x-rapidapi-key': os.getenv("RAPIDAPI_KEY"),
            'x-rapidapi-host': "private-zillow.p.rapidapi.com"
        }
        encoded = requests.utils.quote(address.strip())
        url = f"https://private-zillow.p.rapidapi.com/pro/byaddress?propertyaddress={encoded}"
        response = requests.get(url, headers=headers, timeout=10)

        if not response.ok:
            logger.warning(f"Zillow API error {response.status_code} for {address}")
            return {"is_address_valid": False}

        data = response.json()
        
        # Core validation: must have valid zpid and basic property details
        prop = data.get("propertyDetails", {})
        if not prop.get("zpid") or not prop.get("homeType") or not prop.get("livingAreaValue"):
            logger.warning(f"No valid property data for {address}")
            return {"is_address_valid": False}

        # Store full raw response for reuse by other agents
        state.zillow_raw = data
        state.zpid = prop["zpid"]
        state.is_address_valid = True

        logger.info(f"Address validated: {address} → ZPID {state.zpid}")
        return {"is_address_valid": True}

    except Exception as e:
        logger.error(f"Validation failed for {address}: {e}", exc_info=True)
        return {"is_address_valid": False}