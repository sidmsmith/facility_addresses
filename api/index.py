# api/index.py
from flask import Flask, request, jsonify, send_from_directory
import json
import os
import time
import requests
from requests.auth import HTTPBasicAuth
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

# === SECURE CONFIG (from Vercel Environment Variables) ===
HA_WEBHOOK_URL = "http://sidmsmith.zapto.org:8123/api/webhook/manhattan_facilityaddress"
HA_HEADERS = {"Content-Type": "application/json"}

AUTH_HOST = "salep-auth.sce.manh.com"
API_HOST = "salep.sce.manh.com"
USERNAME_BASE = "sdtadmin@"
PASSWORD = os.getenv("MANHATTAN_PASSWORD")
CLIENT_ID = "omnicomponent.1.0.0"
CLIENT_SECRET = os.getenv("MANHATTAN_SECRET")

# Critical: Fail fast if secrets missing
if not PASSWORD or not CLIENT_SECRET:
    raise Exception("Missing MANHATTAN_PASSWORD or MANHATTAN_SECRET environment variables")

# === HELPERS ===
def send_ha_message(payload):
    try:
        requests.post(HA_WEBHOOK_URL, json=payload, headers=HA_HEADERS, timeout=5)
    except:
        pass

def get_manhattan_token(org):
    url = f"https://{AUTH_HOST}/oauth/token"
    username = f"{USERNAME_BASE}{org.lower()}"
    data = {
        "grant_type": "password",
        "username": username,
        "password": PASSWORD
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    auth = HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
    try:
        r = requests.post(url, data=data, headers=headers, auth=auth, timeout=60, verify=False)
        if r.status_code == 200:
            return r.json().get("access_token")
    except Exception as e:
        print(f"[AUTH] Error: {e}")
    return None

def geocode_address(city, state):
    """Geocode a city/state pair using OpenStreetMap Nominatim API"""
    try:
        # Search for the location
        r = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": f"{city}, {state}", "format": "json", "limit": 1},
            headers={"User-Agent": "SID/3.0"},
            timeout=15
        )
        data = r.json()
        if not data:
            return {
                "address": f"{city} City Center",
                "zip_code": "",
                "lat": 0.0,
                "lng": 0.0,
                "country": "US",
                "state": state  # Keep original input on error
            }

        d = data[0]
        lat, lng = round(float(d["lat"]), 5), round(float(d["lon"]), 5)

        # Reverse geocode to get address details
        r2 = requests.get(
            "https://nominatim.openstreetmap.org/reverse",
            params={"lat": lat, "lon": lng, "format": "json"},
            headers={"User-Agent": "SID/3.0"},
            timeout=15
        )
        addr = r2.json().get("address", {})
        address = addr.get("road", "City Center")
        zip_code = addr.get("postcode", "")
        country = addr.get("country_code", "US").upper()
        
        # Extract state abbreviation from reverse geocoding (override user input)
        # Try different fields that might contain state abbreviation
        state_abbr = state  # Default to user input
        if "state_code" in addr:
            state_abbr = addr["state_code"]
        elif "ISO3166-2" in addr:
            # Format is like "US-GA" - extract the state part
            iso_code = addr["ISO3166-2"]
            if "-" in iso_code:
                state_abbr = iso_code.split("-")[-1]
        elif "state" in addr:
            # If we get full state name, try to extract abbreviation
            state_name = addr["state"]
            # Common state name to abbreviation mapping (US states)
            state_map = {
                "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR",
                "California": "CA", "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE",
                "Florida": "FL", "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID",
                "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS",
                "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
                "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS",
                "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV",
                "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY",
                "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK",
                "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC",
                "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT",
                "Vermont": "VT", "Virginia": "VA", "Washington": "WA", "West Virginia": "WV",
                "Wisconsin": "WI", "Wyoming": "WY"
            }
            if state_name in state_map:
                state_abbr = state_map[state_name]
            elif len(state_name) == 2:
                # Already an abbreviation
                state_abbr = state_name.upper()

        return {
            "address": address,
            "zip_code": zip_code,
            "lat": lat,
            "lng": lng,
            "country": country,
            "state": state_abbr  # Return the corrected state abbreviation
        }
    except Exception as e:
        print(f"[GEOCODE] Error for {city}, {state}: {e}")
        return {
            "address": f"{city} City Center",
            "zip_code": "",
            "lat": 0.0,
            "lng": 0.0,
            "country": "US",
            "state": state  # Keep original input on error
        }

def extract_errors(data):
    """Extract error messages from API response"""
    errors = []
    def find_messages(obj):
        if isinstance(obj, dict):
            if obj.get("Type") == "ERROR" and "Description" in obj:
                errors.append(obj["Description"])
            for v in obj.values():
                find_messages(v)
        elif isinstance(obj, list):
            for item in obj:
                find_messages(item)
    find_messages(data)
    return errors

# === API ROUTES ===
@app.route('/api/app_opened', methods=['POST'])
def app_opened():
    send_ha_message({"event": "sid_open"})
    return jsonify({"success": True})

@app.route('/api/auth', methods=['POST'])
def auth():
    org = request.json.get('org', '').strip()
    if not org:
        return jsonify({"success": False, "error": "ORG required"})
    token = get_manhattan_token(org)
    if token:
        send_ha_message({"event": "sid_auth", "org": org, "success": True})
        return jsonify({"success": True, "token": token})
    send_ha_message({"event": "sid_auth", "org": org, "success": False})
    return jsonify({"success": False, "error": "Auth failed"})

@app.route('/api/geocode', methods=['POST'])
def geocode():
    """Geocode a single city/state pair"""
    data = request.json
    city = data.get('city', '').strip()
    state = data.get('state', '').strip()
    
    if not city or not state:
        return jsonify({"success": False, "error": "City and state required"})
    
    result = geocode_address(city, state)
    return jsonify({"success": True, "result": result})

@app.route('/api/generate', methods=['POST'])
def generate():
    """Generate facility addresses JSON from city/state pairs"""
    data = request.json
    org = data.get('org', '').strip()
    facilities_str = data.get('facilities', '').strip()
    
    if not org:
        return jsonify({"success": False, "error": "ORG required"})
    if not facilities_str:
        return jsonify({"success": False, "error": "Facilities required"})
    
    # Parse facilities string (City, State; City, State)
    facilities_list = [p.strip() for p in facilities_str.replace(";", ",").split(",") if p.strip()]
    
    if len(facilities_list) % 2 != 0:
        return jsonify({"success": False, "error": "Facilities must be in pairs (City, State)"})
    
    results = []
    total_pairs = len(facilities_list) // 2
    
    send_ha_message({"event": "sid_generate", "org": org, "count": total_pairs})
    
    # Geocode each pair
    for i in range(0, len(facilities_list), 2):
        city = facilities_list[i]
        state = facilities_list[i+1]
        
        # Geocode with rate limiting
        geo_result = geocode_address(city, state)
        time.sleep(1.1)  # Rate limit delay
        
        # Use corrected state from geocoding (handles full state names like "Georgia" -> "GA")
        corrected_state = geo_result.get("state", state)
        
        entry = {
            "FacilityId": f"{org}-DM{(i//2)+1}",
            "FacilityAddress": {
                "Address1": geo_result["address"],
                "City": city,
                "State": corrected_state,  # Use corrected state abbreviation
                "PostalCode": geo_result["zip_code"],
                "Country": geo_result["country"]
            },
            "Latitude": f"{geo_result['lat']:.5f}",
            "Longitude": f"{geo_result['lng']:.5f}",
            "Description": f"{city}-DC",
            "DmDeployed": "true"
        }
        results.append(entry)
    
    return jsonify({
        "success": True,
        "data": {"Data": results},
        "count": total_pairs
    })

@app.route('/api/upload', methods=['POST'])
def upload():
    """Upload facility addresses JSON to Manhattan WMS"""
    data = request.json
    org = data.get('org', '').strip()
    token = data.get('token', '').strip()
    json_data = data.get('json_data')
    
    if not org or not token:
        return jsonify({"success": False, "error": "ORG and token required"})
    
    if not json_data:
        return jsonify({"success": False, "error": "JSON data required"})
    
    # Parse JSON if it's a string
    if isinstance(json_data, str):
        try:
            json_data = json.loads(json_data)
        except json.JSONDecodeError:
            return jsonify({"success": False, "error": "Invalid JSON format"})
    
    url = f"https://{API_HOST}/facility/api/facility/facility/bulkImport"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print("=" * 80)
    print("[UPLOAD] API Call Details")
    print("=" * 80)
    print(f"[UPLOAD] URL: {url}")
    print(f"[UPLOAD] Headers: Authorization: Bearer [REDACTED]")
    print(f"[UPLOAD] Payload: {json.dumps(json_data, indent=2)}")
    print("-" * 80)
    
    try:
        r = requests.post(url, json=json_data, headers=headers, timeout=60, verify=False)
        
        print(f"[UPLOAD] Response Status: {r.status_code}")
        print(f"[UPLOAD] Response: {r.text[:1000]}")
        print("=" * 80)
        
        if r.status_code not in (200, 201):
            return jsonify({
                "success": False,
                "error": f"API {r.status_code}: {r.text[:500]}"
            })
        
        resp = r.json()
        data = resp.get("data", {})
        total = data.get("TotalCount", 0)
        success = data.get("SuccessCount", 0)
        failed = data.get("FailedCount", 0)
        errors = extract_errors(resp)
        
        summary = f"Total: {total} | Success: {success} | Failed: {failed}"
        if errors:
            summary += "\n\nErrors:\n" + "\n".join(f"• {e}" for e in errors)
        
        send_ha_message({
            "event": "sid_upload",
            "org": org,
            "total": total,
            "success": success,
            "failed": failed
        })
        
        return jsonify({
            "success": True,
            "summary": summary,
            "total": total,
            "success": success,
            "failed": failed,
            "errors": errors
        })
    except Exception as e:
        print(f"[UPLOAD] Exception: {e}")
        return jsonify({
            "success": False,
            "error": f"Upload failed: {str(e)}"
        })

# === FALLBACK: Serve index.html for SPA ===
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(os.path.dirname(os.path.dirname(__file__)), 'index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)

