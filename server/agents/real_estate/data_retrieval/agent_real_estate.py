import os
from typing import Optional, Dict, Any, List

import requests
from fastapi import HTTPException

from util.logger import get_logger
from models.real_estate.state_real_estate import RealEstateResearchState

logger = get_logger(__name__)

REQUEST_TIMEOUT_SEC = 12
ERROR_SNIPPET_MAX_LEN = 400

def data_retrieval_agent(state: RealEstateResearchState) -> Dict[str, Any]:
    """
    Fetch + validate + extract property data from Zillow (RapidAPI), RentCast, and Crime Data by Zip (RapidAPI).
    Raises HTTP 400 on missing/invalid data, 500 on configuration errors.
    """
    address = (state.address or "").strip()
    if not address:
        raise HTTPException(400, detail="Address is required")

    api_key = os.getenv("RAPID_API_KEY")
    if not api_key:
        msg = "Missing required environment variable: RAPID_API_KEY"
        logger.error(msg)
        raise HTTPException(500, detail="Server configuration error: Missing RapidAPI key")

    logger.info(f"Starting property data retrieval for: {address}")

    errors: List[str] = []

    # ── Zillow Property ────────────────────────────────────────────────────────────────
    zillow_raw: Optional[Dict] = None
    zpid: Optional[int] = None

    try:
        headers = {
            "x-rapidapi-key": api_key,
            "x-rapidapi-host": "private-zillow.p.rapidapi.com"
        }
        encoded = requests.utils.quote(address)
        url = f"https://private-zillow.p.rapidapi.com/pro/byaddress?propertyaddress={encoded}"

        resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT_SEC)

        if not resp.ok:
            err = f"Zillow HTTP {resp.status_code} - {resp.text[:ERROR_SNIPPET_MAX_LEN]}"
            errors.append(err)
            logger.warning(err)
        else:
            try:
                data = resp.json()
                if "propertyDetails" not in data or not data["propertyDetails"].get("zpid"):
                    errors.append("Zillow response missing valid propertyDetails/zpid")
                    logger.warning("Zillow response missing valid propertyDetails/zpid")
                else:
                    zillow_raw = data
                    zpid = int(data["propertyDetails"]["zpid"])
                    logger.info(f"Zillow success → ZPID {zpid}")

                    # ── Extract ZIP, city, state from address object ───────────────────────
                    addr = zillow_raw.get("propertyDetails", {}).get("address", {})
                    if addr:
                        state.zip_code = addr.get("zipcode") or addr.get("zip")
                        state.city     = addr.get("city")
                        state.state    = addr.get("state") or addr.get("stateOrProvince")

                        if state.zip_code:
                            logger.info(f"Extracted ZIP code: {state.zip_code}")
                        elif state.city and state.state:
                            logger.info(f"Extracted city/state fallback: {state.city}, {state.state}")
                        else:
                            logger.warning("Could not extract ZIP or city/state from Zillow address")
                    else:
                        logger.warning("No 'address' object found in Zillow property response")

            except ValueError as e:
                errors.append(f"Zillow JSON decode failed: {str(e)}")
                logger.warning(f"Zillow JSON decode failed: {str(e)}")

    except requests.Timeout:
        errors.append("Zillow request timed out")
        logger.warning("Zillow request timed out")
    except requests.RequestException as e:
        errors.append(f"Zillow network error: {str(e)}")
        logger.warning(f"Zillow network error: {str(e)}")
    except Exception as e:
        errors.append(f"Zillow unexpected error: {str(e)}")
        logger.exception("Zillow unexpected error")

    # ── RentCast ──────────────────────────────────────────────────────────────
    rentcast_raw: Optional[Dict] = None

    try:
        rc_encoded = requests.utils.quote(address)
        rc_url = (
            f"https://us-central1-rentcast-4da28.cloudfunctions.net/getRentData?"
            f"address={rc_encoded}&params=%7B%22avm%22:%7B%7D%7D&report=%7B%22compCount%22:10,%22marketData%22:true%7D&getPropertyData=true"
        )

        resp = requests.get(rc_url, timeout=REQUEST_TIMEOUT_SEC)

        if not resp.ok:
            err = f"RentCast HTTP {resp.status_code} - {resp.text[:ERROR_SNIPPET_MAX_LEN]}"
            errors.append(err)
            logger.warning(err)
        else:
            try:
                data = resp.json()
                if "data" not in data or "property" not in data.get("data", {}):
                    errors.append("RentCast response missing data/property")
                    logger.warning("RentCast response missing data/property")
                else:
                    rentcast_raw = data
                    logger.info("RentCast success")
            except ValueError as e:
                errors.append(f"RentCast JSON decode failed: {str(e)}")
                logger.warning(f"RentCast JSON decode failed: {str(e)}")

    except requests.Timeout:
        errors.append("RentCast request timed out")
        logger.warning("RentCast request timed out")
    except requests.RequestException as e:
        errors.append(f"RentCast network error: {str(e)}")
        logger.warning(f"RentCast network error: {str(e)}")
    except Exception as e:
        errors.append(f"RentCast unexpected error: {str(e)}")
        logger.exception("RentCast unexpected error")

    # ── Zillow Housing Market Trends ──────────────────────────────────────────
    zillow_market_raw: Optional[Dict] = None
    search_query_used = None

    try:
        headers = {
            "x-rapidapi-key": api_key,
            "x-rapidapi-host": "private-zillow.p.rapidapi.com"
        }

        if state.zip_code:
            search_query = state.zip_code
            search_query_used = f"ZIP {state.zip_code}"
        elif state.city and state.state:
            search_query = f"{state.city}, {state.state}"
            search_query_used = search_query
        else:
            logger.warning("Skipping market trends — no usable location (ZIP/city/state) available")

        if search_query:
            encoded_query = requests.utils.quote(search_query)
            url = (
                f"https://private-zillow.p.rapidapi.com/housing_market?"
                f"search_query={encoded_query}"
                f"&home_type=All_Homes"
                f"&exclude_rentalMarketTrends=true"
                f"&exclude_neighborhoods_zhvi=true"
            )

            resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT_SEC)

            if not resp.ok:
                err = f"Zillow market HTTP {resp.status_code} - {resp.text[:ERROR_SNIPPET_MAX_LEN]}"
                errors.append(err)
                logger.warning(err)
            else:
                try:
                    data = resp.json()
                    if not isinstance(data, dict) or "market_overview" not in data:
                        errors.append("Zillow market response missing market_overview")
                        logger.warning("Zillow market response missing market_overview")
                    else:
                        zillow_market_raw = data
                        logger.info(f"Zillow market success for {search_query_used}")
                except ValueError as e:
                    errors.append(f"Zillow market JSON decode failed: {str(e)}")
                    logger.warning(f"Zillow market JSON decode failed: {str(e)}")

    except requests.Timeout:
        errors.append("Zillow market request timed out")
        logger.warning("Zillow market request timed out")
    except requests.RequestException as e:
        errors.append(f"Zillow market network error: {str(e)}")
        logger.warning(f"Zillow market network error: {str(e)}")
    except Exception as e:
        errors.append(f"Zillow market unexpected error: {str(e)}")
        logger.exception("Zillow market unexpected error")

    # ── Crime Data by ZIP (optional) ──────────────────────────────────────────────
    crime_raw: Optional[Dict] = None

    try:
        if not state.zip_code:
            logger.info("No ZIP code available — skipping crime data fetch")
        else:
            headers = {
                "x-rapidapi-key": api_key,
                "x-rapidapi-host": "crime-data-by-zipcode-api.p.rapidapi.com"
            }
            url = f"https://crime-data-by-zipcode-api.p.rapidapi.com/crime_data?zip={state.zip_code}"

            resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT_SEC)

            if not resp.ok:
                err = f"Crime API HTTP {resp.status_code} - {resp.text[:ERROR_SNIPPET_MAX_LEN]}"
                errors.append(err)
                logger.warning(err)
            else:
                try:
                    crime_data = resp.json()
                    if not crime_data.get("success", False):
                        err = f"Crime API returned success=false for ZIP {state.zip_code}"
                        errors.append(err)
                        logger.warning(err)
                    else:
                        crime_raw = crime_data
                        logger.info(f"Crime API success for ZIP {state.zip_code}")

                        # Extract key grades for easier downstream use
                        overall = crime_data.get("Overall", {})
                        state.crime_overall_grade  = overall.get("Overall Crime Grade")
                        state.crime_violent_grade  = overall.get("Violent Crime Grade")
                        state.crime_property_grade = overall.get("Property Crime Grade")

                        if state.crime_overall_grade:
                            logger.info(
                                f"Crime grades → Overall: {state.crime_overall_grade}, "
                                f"Violent: {state.crime_violent_grade}, "
                                f"Property: {state.crime_property_grade}"
                            )

                except ValueError as e:
                    err = f"Crime API JSON decode failed: {str(e)}"
                    errors.append(err)
                    logger.warning(err)

    except requests.Timeout:
        err = f"Crime API request timed out for ZIP {state.zip_code}"
        errors.append(err)
        logger.warning(err)
    except requests.RequestException as e:
        err = f"Crime API network error: {str(e)}"
        errors.append(err)
        logger.warning(err)
    except Exception as e:
        err = f"Crime API unexpected error for ZIP {state.zip_code}: {str(e)}"
        errors.append(err)
        logger.exception("Crime API unexpected error")

    # ── Final validation ──────────────────────────────────────────────────────
    if not zillow_raw or not rentcast_raw:
        msg = "Failed to retrieve complete property data.\n" + "\n".join(errors)
        logger.error(f"Property data retrieval failed for {address}: {msg}")
        raise HTTPException(400, detail=msg + "\nPlease verify the address and try again.")

    # Market data is nice-to-have
    if not zillow_market_raw:
        logger.warning(f"Market trends unavailable for {address} — continuing without")

    # ── Store raw responses ───────────────────────────────────────────────────
    state.zillow_raw = zillow_raw
    state.rentcast_raw = rentcast_raw
    state.zillow_market_raw = zillow_market_raw
    state.crime_raw = crime_raw
    state.zpid = zpid
    state.data_retrieved = True


    # ── Extract scalars from property ─────────────────────────────────────────
    z_details = zillow_raw.get("propertyDetails", {})
    z_facts = z_details.get("resoFacts", {})
    rc_prop = rentcast_raw.get("data", {}).get("property", {})

    state.zestimate     = float(z_details.get("zestimate") or 0)
    state.tax_annual    = float(z_facts.get("taxAnnualAmount") or 0)
    state.hoa_monthly   = float(z_details.get("monthlyHoaFee") or 0)
    state.rent_estimate = float(rc_prop.get("rentEstimate", {}).get("value") or 0)

    # Auto-fill
    if state.purchase_price is None or state.purchase_price <= 0:
        state.purchase_price = state.zestimate
        logger.info(f"Auto-filled purchase_price from Zestimate: ${state.purchase_price:,.0f}")

    if state.estimated_rent is None or state.estimated_rent <= 0:
        state.estimated_rent = state.rent_estimate
        logger.info(f"Auto-filled estimated_rent from RentCast: ${state.estimated_rent:,.0f}")

    # ── Extract schools (optional) ────────────────────────────────────────────────
    schools_raw: Optional[List[Dict]] = None

    schools_list = z_details.get("schools", [])
    if isinstance(schools_list, list) and schools_list:
        schools_raw = schools_list
        state.schools_raw = schools_raw
        logger.info(f"Found {len(schools_raw)} schools in Zillow data")

        # Best-effort assignment of one school per typical grade band
        # (sorted by distance — closest first)
        for school in sorted(schools_raw, key=lambda s: s.get("distance", 999)):
            name = school.get("name")
            rating = school.get("rating")
            grades = school.get("grades", "")

            if not name or rating is None:
                continue

            # Elementary (PK-5 or similar)
            if not state.elementary_school_name and any(g in grades for g in ["PK", "K", "1", "2", "3", "4", "5"]):
                state.elementary_school_name = name
                state.elementary_school_rating = int(rating) if isinstance(rating, (int, str)) and str(rating).isdigit() else None
                logger.info(f"Assigned elementary: {name} (rating {state.elementary_school_rating})")

            # Middle (6-8)
            elif not state.middle_school_name and any(g in grades for g in ["6", "7", "8"]):
                state.middle_school_name = name
                state.middle_school_rating = int(rating) if isinstance(rating, (int, str)) and str(rating).isdigit() else None
                logger.info(f"Assigned middle: {name} (rating {state.middle_school_rating})")

            # High (9-12)
            elif not state.high_school_name and any(g in grades for g in ["9", "10", "11", "12"]):
                state.high_school_name = name
                state.high_school_rating = int(rating) if isinstance(rating, (int, str)) and str(rating).isdigit() else None
                logger.info(f"Assigned high: {name} (rating {state.high_school_rating})")

        # Log summary of assigned schools
        logger.info(
            f"Assigned schools: "
            f"Elem={state.elementary_school_name or 'N/A'} ({state.elementary_school_rating or '?'}), "
            f"Mid={state.middle_school_name or 'N/A'} ({state.middle_school_rating or '?'}), "
            f"High={state.high_school_name or 'N/A'} ({state.high_school_rating or '?'})"
        )
    else:
        logger.info("No schools data found in Zillow response")

    # ── Extract key market overview scalars ───────────────────────────────────
    if zillow_market_raw:
        overview = zillow_market_raw.get("market_overview", {})

        state.market_typical_value     = float(overview.get("typical_home_values") or 0)
        state.market_description       = overview.get("description", "").strip()
        state.market_inventory         = int(overview.get("for_sale_inventory") or 0)
        state.market_days_pending      = int(overview.get("median_days_to_pending") or 0)
        state.market_median_sale       = float(overview.get("median_sale_price") or 0)
        state.market_median_list       = float(overview.get("median_list_price") or 0)
        state.market_sale_to_list      = float(overview.get("market_saletolist_ratio") or 0)

        # Parse YoY change from description
        desc = state.market_description.lower()
        state.market_yoy_change_pct = 0.0
        if "down" in desc:
            try:
                pct_str = desc.split("down ")[-1].split("%")[0].strip()
                state.market_yoy_change_pct = -float(pct_str)
            except:
                pass
        elif "up" in desc:
            try:
                pct_str = desc.split("up ")[-1].split("%")[0].strip()
                state.market_yoy_change_pct = float(pct_str)
            except:
                pass

        logger.info(
            f"Market overview extracted → ZHVI ${state.market_typical_value:,.0f} "
            f"({state.market_yoy_change_pct:+.1f}% YoY) | "
            f"inventory {state.market_inventory:,} | "
            f"days pending {state.market_days_pending}"
        )

    # Critical data warnings
    if state.zestimate <= 0:
        logger.warning(f"Zestimate missing or zero for {address} (ZPID {state.zpid})")
    if state.rent_estimate <= 0:
        logger.warning(f"Rent estimate missing or zero for {address}")

    logger.info(
        f"Extracted → zestimate=${state.zestimate:,.0f} | "
        f"rent est=${state.rent_estimate:,.0f}/mo | "
        f"tax=${state.tax_annual:,.0f}/yr | "
        f"hoa=${state.hoa_monthly:,.0f}/mo"
    )

    logger.info(f"Property data retrieval successful - ZPID: {state.zpid}")

    return {
        "data_retrieved": True,
        "zpid": state.zpid,
        "zillow_raw": state.zillow_raw,
        "rentcast_raw": state.rentcast_raw,
        "zillow_market_raw": state.zillow_market_raw,
        "zestimate": state.zestimate,
        "rent_estimate": state.rent_estimate,
        "tax_annual": state.tax_annual,
        "hoa_monthly": state.hoa_monthly,
        "purchase_price": state.purchase_price,
        "estimated_rent": state.estimated_rent,
        # Location fields (extracted from Zillow)
        "zip_code": state.zip_code,
        "city": state.city,
        "state": state.state,
        # Market overview fields
        "market_typical_value": getattr(state, "market_typical_value", None),
        "market_description": getattr(state, "market_description", None),
        "market_yoy_change_pct": getattr(state, "market_yoy_change_pct", None),
        "market_inventory": getattr(state, "market_inventory", None),
        "market_days_pending": getattr(state, "market_days_pending", None),
        "market_median_sale": getattr(state, "market_median_sale", None),
        "market_sale_to_list": getattr(state, "market_sale_to_list", None),
        # Debug helper
        "search_query_used": search_query_used,
        "crime_raw": getattr(state, "crime_raw", None),
        "crime_overall_grade": getattr(state, "crime_overall_grade", None),
        "crime_violent_grade": getattr(state, "crime_violent_grade", None),
        "crime_property_grade": getattr(state, "crime_property_grade", None),

        "schools_raw": getattr(state, "schools_raw", None),
        "elementary_school_name": getattr(state, "elementary_school_name", None),
        "elementary_school_rating": getattr(state, "elementary_school_rating", None),
        "middle_school_name": getattr(state, "middle_school_name", None),
        "middle_school_rating": getattr(state, "middle_school_rating", None),
        "high_school_name": getattr(state, "high_school_name", None),
        "high_school_rating": getattr(state, "high_school_rating", None),
    }