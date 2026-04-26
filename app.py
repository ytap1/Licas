import streamlit as st
import requests
import json
import base64
import socket
from datetime import datetime
from PIL import Image
import io

# ── Constants ─────────────────────────────────────────────────────────────────

GEMINI_API_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemma-3-27b-it:generateContent"
)
MAX_ITERATIONS = 10

# ── API key ───────────────────────────────────────────────────────────────────

def get_api_key():
    try:
        return st.secrets["GEMINI_API_KEY"]
    except Exception:
        return None

# ── Network detection ─────────────────────────────────────────────────────────

def is_online():
    try:
        socket.setdefaulttimeout(3)
        socket.getaddrinfo("generativelanguage.googleapis.com", 443)
        return True
    except Exception:
        return False

# ── Page config (must be first st call) ──────────────────────────────────────

st.set_page_config(
    page_title="LIKAS",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Scenario data ─────────────────────────────────────────────────────────────

SCENARIO_A = {
    "label": "Scenario A — WATCH (River rising, no breach)",
    "barangay": "Patubig, Marilao, Bulacan",
    "station_id": "ASTI-BUL-MAR-001",
    "timestamp": "2024-09-12T14:30:00+08:00",
    "internet": True,
    "water_level_m": 2.8,
    "threshold_m": 3.5,
    "threshold_pct": 80,
    "trend": "RISING",
    "rate_m_per_hr": 0.15,
    "rain_1hr": 18,
    "rain_3hr": 42,
    "rain_6hr": 67,
    "zones": [
        {"name": "Zone 1", "elevation_m": 1.2, "population": 340},
        {"name": "Zone 2", "elevation_m": 1.8, "population": 520},
        {"name": "Zone 3", "elevation_m": 2.4, "population": 290},
    ],
    "evacuation_centers": [
        {"name": "Patubig Elementary School", "capacity": 400, "distance_km": 0.8},
        {"name": "Marilao Municipal Gymnasium", "capacity": 800, "distance_km": 2.1},
    ],
    "flooded_roads": [],
    "photo_description": (
        "River water is elevated but still within embankment walls. "
        "Road beside the river (Riverside Drive) is completely dry. "
        "No visible overflow or breach. Water appears brown/murky, "
        "indicating upstream runoff. Embankment clearance estimated at approximately 0.7m remaining."
    ),
}

SCENARIO_B = {
    "label": "Scenario B — CRITICAL (Breach confirmed, single barangay)",
    "barangay": "Patubig, Marilao, Bulacan",
    "station_id": "ASTI-BUL-MAR-001",
    "timestamp": "2024-09-12T17:45:00+08:00",
    "internet": True,
    "water_level_m": 4.2,
    "threshold_m": 3.5,
    "threshold_pct": 120,
    "trend": "RISING",
    "rate_m_per_hr": 0.35,
    "rain_1hr": 38,
    "rain_3hr": 89,
    "rain_6hr": 134,
    "zones": [
        {"name": "Zone 1", "elevation_m": 1.2, "population": 340},
        {"name": "Zone 2", "elevation_m": 1.8, "population": 520},
        {"name": "Zone 3", "elevation_m": 2.4, "population": 290},
    ],
    "evacuation_centers": [
        {"name": "Patubig Elementary School", "capacity": 400, "distance_km": 0.8},
        {"name": "Marilao Municipal Gymnasium", "capacity": 800, "distance_km": 2.1},
    ],
    "flooded_roads": [
        "Burgos St — fully submerged, impassable",
        "Riverside Drive — ankle-deep, use caution",
    ],
    "photo_description": (
        "Floodwater is visibly overflowing the eastern embankment wall. "
        "Riverside Drive has approximately 20cm of water covering the road. "
        "One vehicle is stalled and partially submerged near the embankment. "
        "Residents visible on the road carrying belongings. "
        "Water is actively flowing over the embankment edge — breach confirmed."
    ),
}

SCENARIO_C = {
    "label": "Scenario C — CRITICAL + Offline (Multi-barangay flood)",
    "barangay": "Multiple — Patubig, Liang, Ibayo (Marilao, Bulacan)",
    "timestamp": "2024-09-12T20:15:00+08:00",
    "internet": False,
    "last_sync": "2024-09-12T19:58:00+08:00",
    "total_population": 3050,
    "stations": [
        {
            "id": "ASTI-BUL-MAR-001",
            "barangay": "Patubig",
            "water_level_m": 4.8,
            "threshold_m": 3.5,
            "threshold_pct": 137,
            "trend": "RISING",
            "rate_m_per_hr": 0.40,
        },
        {
            "id": "ASTI-BUL-MAR-002",
            "barangay": "Liang",
            "water_level_m": 3.6,
            "threshold_m": 3.5,
            "threshold_pct": 103,
            "trend": "RISING",
            "rate_m_per_hr": 0.25,
        },
        {
            "id": "ASTI-BUL-MAR-003",
            "barangay": "Ibayo",
            "water_level_m": 2.9,
            "threshold_m": 3.5,
            "threshold_pct": 83,
            "trend": "RISING",
            "rate_m_per_hr": 0.20,
        },
    ],
    "evacuation_centers": [
        {"name": "Patubig Elementary School", "capacity": 400, "distance_km": 0.8},
        {"name": "Liang Barangay Hall (2nd Floor)", "capacity": 200, "distance_km": 0.4},
        {"name": "Ibayo Elementary School", "capacity": 500, "distance_km": 1.2},
    ],
    "photo_description": (
        "Wide-angle photo showing two adjacent streets with brown floodwater "
        "reaching approximately 60-80cm depth. Residents visible on rooftops "
        "of single-story homes. One barangay tanod vehicle is partially submerged — "
        "only the roof and upper windows are visible. "
        "Streetlights are still on. Floodwater appears to be actively flowing."
    ),
}

SCENARIOS = {
    SCENARIO_A["label"]: SCENARIO_A,
    SCENARIO_B["label"]: SCENARIO_B,
    SCENARIO_C["label"]: SCENARIO_C,
}

# ── System prompt ─────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are LIKAS (Local Intelligence for Katastrophe Alert and Safety),
an AI disaster intelligence assistant for DRRM officers in the Philippines.

Your role:
1. Analyze flood sensor data and visual evidence from photos
2. Assess threat level: ADVISORY (50-74%), WATCH (75-89%), WARNING (90-99%), CRITICAL (100%+)
3. Identify which zones are at risk and in what order
4. Recommend safest evacuation routes avoiding flooded roads
5. Generate bilingual alerts — English and Tagalog (Grade 4 reading level)
6. Call the appropriate functions in the correct order

FUNCTION CALL ORDER (when applicable):
1. get_flood_map() first
2. calculate_safe_route() — one per affected zone
3. broadcast_alert() — one per alert level group
4. escalate_to_ndrrmc() — CRITICAL multi-barangay only

RULES:
- Always explain your reasoning before calling any function
- Never recommend evacuation without citing sensor evidence or visual confirmation
- Always estimate time before flood reaches next zone
- When in doubt, escalate — a missed alarm costs lives
- Tagalog must be Grade 4 reading level
- For CRITICAL multi-barangay, always call escalate_to_ndrrmc

ALERT LEVELS:
- ADVISORY: Monitor only, no broadcast
- WATCH: Notify Zone 1, prepare residents
- WARNING: Voluntary evacuation, broadcast all zones
- CRITICAL: Mandatory evacuation, full agentic chain
"""

# ── Tool definitions ──────────────────────────────────────────────────────────

TOOLS = [
    {
        "function_declarations": [
            {
                "name": "get_flood_map",
                "description": (
                    "Load pre-cached flood risk map for a barangay. Returns currently "
                    "flooded roads and safe roads. Always call this first before calculate_safe_route."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "barangay_code": {
                            "type": "string",
                            "description": "PSA barangay code",
                        },
                        "water_level_m": {
                            "type": "number",
                            "description": "Current water level in meters",
                        },
                    },
                    "required": ["barangay_code", "water_level_m"],
                },
            },
            {
                "name": "calculate_safe_route",
                "description": (
                    "Calculate safest evacuation route from a zone to an evacuation center, "
                    "avoiding flooded roads. Always call get_flood_map first."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "origin_zone": {"type": "string"},
                        "destination": {"type": "string"},
                        "flooded_roads": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                    },
                    "required": ["origin_zone", "destination", "flooded_roads"],
                },
            },
            {
                "name": "broadcast_alert",
                "description": (
                    "Send bilingual alert to residents via SMS and local WiFi mesh. "
                    "Only call at WATCH level or above."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "zones": {"type": "array", "items": {"type": "string"}},
                        "alert_level": {
                            "type": "string",
                            "enum": ["ADVISORY", "WATCH", "WARNING", "CRITICAL"],
                        },
                        "message_english": {"type": "string"},
                        "message_tagalog": {"type": "string"},
                        "include_route": {"type": "boolean"},
                    },
                    "required": [
                        "zones",
                        "alert_level",
                        "message_english",
                        "message_tagalog",
                    ],
                },
            },
            {
                "name": "escalate_to_ndrrmc",
                "description": (
                    "Queue formal situation report for NDRRMC. Report is sent when internet "
                    "is restored. Use at CRITICAL level with multiple barangays affected."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "situation_summary": {"type": "string"},
                        "affected_zones": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "actions_taken": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "estimated_affected_population": {"type": "integer"},
                    },
                    "required": [
                        "situation_summary",
                        "affected_zones",
                        "actions_taken",
                        "estimated_affected_population",
                    ],
                },
            },
        ]
    }
]

# ── Mock function implementations ─────────────────────────────────────────────

def execute_get_flood_map(barangay_code, water_level_m):
    flood_data = {
        "PH-BUL-MAR-001": {
            "barangay": "Patubig, Marilao",
            "flooded_at_current_level": (
                ["Burgos St", "Riverside Drive"] if water_level_m >= 4.0 else []
            ),
            "safe_roads": ["Maharlika Highway", "Rizal Avenue", "Nacional Road"],
            "routes": {
                "Zone 1": "Gomez St → Rizal Ave → Maharlika Hwy → Patubig Elementary School",
                "Zone 2": "Nacional Road → Maharlika Hwy → Marilao Municipal Gymnasium",
                "Zone 3": "Maharlika Hwy → Marilao Municipal Gymnasium",
            },
        },
        "PH-BUL-MAR-002": {
            "barangay": "Liang, Marilao",
            "flooded_at_current_level": (
                ["Liang riverside road"] if water_level_m >= 3.5 else []
            ),
            "safe_roads": ["Liang-Marilao Road", "Purok 1 Road"],
            "routes": {
                "Zone 1": "Purok 1 Road → Liang Barangay Hall (2nd Floor)",
                "Zone 2": "Liang-Marilao Road → Liang Barangay Hall (2nd Floor)",
            },
        },
        "PH-BUL-MAR-003": {
            "barangay": "Ibayo, Marilao",
            "flooded_at_current_level": [],
            "safe_roads": ["Ibayo Road", "Brgy. Road 3"],
            "routes": {
                "Zone 1": "Ibayo Road → Ibayo Elementary School",
                "Zone 2": "Brgy. Road 3 → Ibayo Elementary School",
            },
        },
    }
    return flood_data.get(barangay_code, {"error": f"No map for {barangay_code}"})


def execute_calculate_safe_route(origin_zone, destination, flooded_roads):
    routes = {
        ("Zone 1", "Patubig Elementary School"): {
            "route": "Gomez St → Rizal Avenue → Maharlika Highway → Patubig Elementary School",
            "distance_km": 0.8,
            "walk_minutes": 12,
            "status": "CLEAR",
        },
        ("Zone 2", "Marilao Municipal Gymnasium"): {
            "route": "Nacional Road → Maharlika Highway → Marilao Municipal Gymnasium",
            "distance_km": 2.1,
            "walk_minutes": 28,
            "status": "CLEAR",
        },
        ("Zone 1", "Liang Barangay Hall (2nd Floor)"): {
            "route": "Purok 1 Road → Liang Barangay Hall (2nd Floor)",
            "distance_km": 0.4,
            "walk_minutes": 6,
            "status": "CLEAR",
        },
        ("Zone 1", "Ibayo Elementary School"): {
            "route": "Ibayo Road → Ibayo Elementary School",
            "distance_km": 1.2,
            "walk_minutes": 16,
            "status": "CLEAR",
        },
    }
    key = (origin_zone, destination)
    result = routes.get(
        key,
        {
            "route": f"Proceed to {destination} via highest elevation roads",
            "distance_km": "unknown",
            "walk_minutes": "unknown",
            "status": "REROUTED",
        },
    )
    result["flooded_roads_avoided"] = flooded_roads
    return result


def execute_broadcast_alert(zones, alert_level, message_english, message_tagalog, include_route=True):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {
        "status": "BROADCAST_SENT",
        "alert_level": alert_level,
        "zones_alerted": zones,
        "timestamp": timestamp,
        "channels": ["SMS", "Local WiFi Mesh"],
        "recipients_estimated": len(zones) * 150,
        "route_included": include_route,
        "message_english": message_english,
        "message_tagalog": message_tagalog,
    }


def execute_escalate_to_ndrrmc(
    situation_summary, affected_zones, actions_taken, estimated_affected_population
):
    report_id = f"LIKAS-{datetime.now().strftime('%Y%m%d-%H%M')}"
    return {
        "status": "QUEUED",
        "report_id": report_id,
        "message": "Report queued. Will transmit automatically when internet is restored.",
        "affected_population": estimated_affected_population,
        "situation_summary": situation_summary,
        "affected_zones": affected_zones,
        "actions_taken": actions_taken,
    }


FUNCTION_MAP = {
    "get_flood_map": execute_get_flood_map,
    "calculate_safe_route": execute_calculate_safe_route,
    "broadcast_alert": execute_broadcast_alert,
    "escalate_to_ndrrmc": execute_escalate_to_ndrrmc,
}


def dispatch(function_name, args):
    func = FUNCTION_MAP.get(function_name)
    if not func:
        return {"error": f"Unknown function: {function_name}"}
    try:
        return func(**args)
    except Exception as e:
        return {"error": str(e)}

# ── Context prompt builder ────────────────────────────────────────────────────

def build_context(scenario, photo_description):
    if "stations" in scenario:
        stations_text = "\n".join([
            f"  [{s['barangay']}] {s['water_level_m']}m / {s['threshold_m']}m threshold "
            f"({s['threshold_pct']}%) — RISING at {s['rate_m_per_hr']}m/hr"
            for s in scenario["stations"]
        ])
        return (
            f"SITUATION REPORT — MULTI-BARANGAY\n"
            f"Timestamp: {scenario['timestamp']}\n"
            f"Internet: OFFLINE (last sync: {scenario.get('last_sync', 'unknown')})\n"
            f"Total population at risk: {scenario['total_population']}\n\n"
            f"SENSOR READINGS:\n{stations_text}\n\n"
            f"VISUAL EVIDENCE:\n{photo_description}\n\n"
            "Assess all three barangays, prioritize by urgency, calculate routes, "
            "broadcast alerts, and queue NDRRMC report. "
            "Internet is OFFLINE — use local WiFi mesh and SMS only."
        )

    flooded = (
        "\n".join([f"  - {r}" for r in scenario.get("flooded_roads", [])])
        or "  None reported"
    )
    zones_text = "\n".join([
        f"  - {z['name']}: {z['elevation_m']}m elevation, {z['population']} residents"
        for z in scenario["zones"]
    ])
    centers_text = "\n".join([
        f"  - {c['name']}: capacity {c['capacity']}, {c['distance_km']}km away"
        for c in scenario["evacuation_centers"]
    ])
    return (
        f"SITUATION REPORT\n"
        f"Timestamp: {scenario['timestamp']}\n"
        f"Location: {scenario['barangay']}\n"
        f"Internet: {'ONLINE' if scenario['internet'] else 'OFFLINE'}\n\n"
        f"SENSOR DATA (Station {scenario['station_id']}):\n"
        f"  Water Level: {scenario['water_level_m']}m / Threshold: {scenario['threshold_m']}m "
        f"({scenario['threshold_pct']}%)\n"
        f"  Trend: {scenario['trend']} at {scenario['rate_m_per_hr']}m/hr\n"
        f"  Rainfall: {scenario['rain_1hr']}mm/1hr | {scenario['rain_3hr']}mm/3hr | "
        f"{scenario['rain_6hr']}mm/6hr\n\n"
        f"ZONES:\n{zones_text}\n\n"
        f"EVACUATION CENTERS:\n{centers_text}\n\n"
        f"KNOWN FLOODED ROADS:\n{flooded}\n\n"
        f"VISUAL EVIDENCE:\n{photo_description}\n\n"
        "Assess threat level, identify at-risk zones, and take all necessary actions."
    )

# ── Offline fallbacks ─────────────────────────────────────────────────────────

OFFLINE_FALLBACKS = {
    "A": {
        "alert_level": "WATCH",
        "reasoning": (
            "Water level is at 80% of danger threshold (2.8m / 3.5m), rising at 0.15m/hr. "
            "Photo confirms river is elevated but embankment is intact — no breach visible. "
            "Sustained rainfall over 6 hours. At current rate, danger threshold reached in ~4.7 hours. "
            "WATCH level declared. Zone 1 residents notified to prepare."
        ),
        "function_call_log": [
            {
                "function": "broadcast_alert",
                "args": {
                    "zones": ["Zone 1"],
                    "alert_level": "WATCH",
                    "message_english": (
                        "WATCH ALERT — Brgy. Patubig, Zone 1. Water level is rising and at 80% "
                        "of danger threshold. No evacuation required yet. "
                        "Prepare your go-bag and stay informed."
                    ),
                    "message_tagalog": (
                        "BABALA — Brgy. Patubig, Zone 1. Ang tubig sa ilog ay tumataas. "
                        "Hindi pa kailangang lumikas. "
                        "Ihanda na ang inyong go-bag at makinig sa mga update."
                    ),
                    "include_route": False,
                },
                "result": execute_broadcast_alert(
                    ["Zone 1"],
                    "WATCH",
                    "WATCH ALERT — Brgy. Patubig, Zone 1. Water level rising.",
                    "BABALA — Brgy. Patubig, Zone 1. Ang tubig ay tumataas.",
                    False,
                ),
            }
        ],
    },
    "B": {
        "alert_level": "CRITICAL",
        "reasoning": (
            "CRITICAL — Sensor at 120% of danger threshold (4.2m / 3.5m), rising at 0.35m/hr. "
            "Photo CONFIRMS active embankment breach on eastern bank. "
            "Zone 1 (1.2m elevation) is at immediate risk. "
            "Zone 2 (1.8m) will be affected in ~1.7 hours. "
            "Burgos St is impassable. Routing via Gomez St and Rizal Ave. "
            "Mandatory evacuation for Zone 1. Warning for Zone 2."
        ),
        "function_call_log": [
            {
                "function": "get_flood_map",
                "args": {"barangay_code": "PH-BUL-MAR-001", "water_level_m": 4.2},
                "result": execute_get_flood_map("PH-BUL-MAR-001", 4.2),
            },
            {
                "function": "calculate_safe_route",
                "args": {
                    "origin_zone": "Zone 1",
                    "destination": "Patubig Elementary School",
                    "flooded_roads": ["Burgos St", "Riverside Drive"],
                },
                "result": execute_calculate_safe_route(
                    "Zone 1", "Patubig Elementary School", ["Burgos St", "Riverside Drive"]
                ),
            },
            {
                "function": "calculate_safe_route",
                "args": {
                    "origin_zone": "Zone 2",
                    "destination": "Marilao Municipal Gymnasium",
                    "flooded_roads": ["Burgos St"],
                },
                "result": execute_calculate_safe_route(
                    "Zone 2", "Marilao Municipal Gymnasium", ["Burgos St"]
                ),
            },
            {
                "function": "broadcast_alert",
                "args": {
                    "zones": ["Zone 1"],
                    "alert_level": "CRITICAL",
                    "message_english": (
                        "CRITICAL ALERT — Brgy. Patubig, Zone 1. MANDATORY EVACUATION. "
                        "River has breached embankment. Proceed immediately to "
                        "Patubig Elementary School via Gomez St → Rizal Ave → Maharlika Hwy. "
                        "AVOID Burgos St and Riverside Drive."
                    ),
                    "message_tagalog": (
                        "🚨 AGARANG LUMIKAS — Brgy. Patubig, Zone 1. Umapaw na ang ilog. "
                        "Pumunta na agad sa Patubig Elementary School. "
                        "Daanan: Gomez St → Rizal Ave → Maharlika Hwy. "
                        "HUWAG dumaan sa Burgos St at Riverside Drive."
                    ),
                    "include_route": True,
                },
                "result": execute_broadcast_alert(
                    ["Zone 1"], "CRITICAL", "MANDATORY EVACUATION.", "AGARANG LUMIKAS.", True
                ),
            },
            {
                "function": "broadcast_alert",
                "args": {
                    "zones": ["Zone 2"],
                    "alert_level": "WARNING",
                    "message_english": (
                        "WARNING — Brgy. Patubig, Zone 2. Flooding expected within 2 hours. "
                        "Prepare to evacuate to Marilao Municipal Gymnasium."
                    ),
                    "message_tagalog": (
                        "🔴 BABALA — Brgy. Patubig, Zone 2. "
                        "Inaasahang mag-baha sa loob ng 2 oras. "
                        "Maghanda na lumikas sa Marilao Municipal Gymnasium."
                    ),
                    "include_route": True,
                },
                "result": execute_broadcast_alert(
                    ["Zone 2"], "WARNING",
                    "WARNING — flooding expected in 2 hours.",
                    "BABALA — Mag-baha sa 2 oras.",
                    True,
                ),
            },
        ],
    },
    "C": {
        "alert_level": "CRITICAL",
        "reasoning": (
            "CRITICAL multi-barangay event. Internet is OFFLINE. "
            "Patubig at 137% — actively breached, evacuate immediately. "
            "Liang at 103% — just crossed threshold, evacuate now. "
            "Ibayo at 83% rising at 0.20m/hr — WARNING, prepare. "
            "Photo confirms widespread inundation, residents on rooftops. "
            "All alerts via local WiFi mesh and SMS. NDRRMC report queued."
        ),
        "function_call_log": [
            {
                "function": "broadcast_alert",
                "args": {
                    "zones": ["Patubig Zone 1", "Patubig Zone 2"],
                    "alert_level": "CRITICAL",
                    "message_english": (
                        "CRITICAL — Brgy. Patubig. MANDATORY EVACUATION. "
                        "River at 137% of danger level."
                    ),
                    "message_tagalog": (
                        "🚨 AGARANG LUMIKAS — Brgy. Patubig. "
                        "Lubhang mapanganib na ang antas ng tubig. Lumayo na agad."
                    ),
                    "include_route": True,
                },
                "result": execute_broadcast_alert(
                    ["Patubig Zone 1", "Patubig Zone 2"], "CRITICAL",
                    "MANDATORY EVACUATION.", "AGARANG LUMIKAS.", True,
                ),
            },
            {
                "function": "broadcast_alert",
                "args": {
                    "zones": ["Liang Zone 1", "Liang Zone 2"],
                    "alert_level": "CRITICAL",
                    "message_english": (
                        "CRITICAL — Brgy. Liang. MANDATORY EVACUATION. "
                        "River has crossed danger threshold."
                    ),
                    "message_tagalog": (
                        "🚨 AGARANG LUMIKAS — Brgy. Liang. "
                        "Lumampas na ang tubig sa mapanganib na antas."
                    ),
                    "include_route": True,
                },
                "result": execute_broadcast_alert(
                    ["Liang Zone 1", "Liang Zone 2"], "CRITICAL",
                    "MANDATORY EVACUATION.", "AGARANG LUMIKAS.", True,
                ),
            },
            {
                "function": "broadcast_alert",
                "args": {
                    "zones": ["Ibayo Zone 1", "Ibayo Zone 2"],
                    "alert_level": "WARNING",
                    "message_english": (
                        "WARNING — Brgy. Ibayo. Water rising rapidly. Prepare to evacuate."
                    ),
                    "message_tagalog": (
                        "🔴 BABALA — Brgy. Ibayo. "
                        "Mabilis na tumataas ang tubig. Maghanda na lumikas."
                    ),
                    "include_route": False,
                },
                "result": execute_broadcast_alert(
                    ["Ibayo Zone 1", "Ibayo Zone 2"], "WARNING",
                    "Water rising rapidly.", "Mabilis na tumataas ang tubig.", False,
                ),
            },
            {
                "function": "escalate_to_ndrrmc",
                "args": {
                    "situation_summary": (
                        "Major flood event — 3 barangays in Marilao, Bulacan. "
                        "Patubig 137%, Liang 103%, Ibayo 83% and rising. Internet offline."
                    ),
                    "affected_zones": [
                        "Patubig Zone 1 & 2",
                        "Liang Zone 1 & 2",
                        "Ibayo Zone 1 & 2",
                    ],
                    "actions_taken": [
                        "CRITICAL alerts broadcast to Patubig and Liang",
                        "WARNING broadcast to Ibayo",
                        "Evacuation routes calculated",
                    ],
                    "estimated_affected_population": 3050,
                },
                "result": execute_escalate_to_ndrrmc(
                    "Major flood — 3 barangays, Marilao Bulacan",
                    ["Patubig", "Liang", "Ibayo"],
                    ["Alerts broadcast", "Routes calculated"],
                    3050,
                ),
            },
        ],
    },
}

# ── Agentic loop (online) ─────────────────────────────────────────────────────

def run_online(scenario, photo_description, api_key):
    context = build_context(scenario, photo_description)
    messages = [{"role": "user", "parts": [{"text": SYSTEM_PROMPT + "\n\n" + context}]}]
    function_call_log = []
    final_text = ""

    for _ in range(MAX_ITERATIONS):
        payload = {
            "contents": messages,
            "tools": TOOLS,
            "generationConfig": {"temperature": 0.2, "maxOutputTokens": 2048},
        }
        response = requests.post(
            f"{GEMINI_API_URL}?key={api_key}",
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        candidate = data["candidates"][0]["content"]
        messages.append({"role": "model", "parts": candidate["parts"]})

        fn_calls = [p for p in candidate["parts"] if "functionCall" in p]
        if not fn_calls:
            for part in candidate["parts"]:
                if "text" in part:
                    final_text += part["text"]
            break

        tool_results = []
        for part in fn_calls:
            fc = part["functionCall"]
            result_data = dispatch(fc["name"], fc.get("args", {}))
            function_call_log.append({
                "function": fc["name"],
                "args": fc.get("args", {}),
                "result": result_data,
            })
            tool_results.append({
                "functionResponse": {
                    "name": fc["name"],
                    "response": {"result": result_data},
                }
            })
        messages.append({"role": "user", "parts": tool_results})

    return {"mode": "ONLINE", "reasoning": final_text, "function_call_log": function_call_log}

# ── run_analysis ──────────────────────────────────────────────────────────────

def run_analysis(scenario, photo_description, mode, api_key):
    scenario_id = scenario["label"][9]  # extracts "A", "B", or "C"

    if mode == "🔴 Simulate Offline Mode" or not api_key:
        fallback = OFFLINE_FALLBACKS[scenario_id]
        return {
            "mode": "OFFLINE (Simulated)",
            "reasoning": fallback["reasoning"],
            "alert_level": fallback["alert_level"],
            "function_call_log": fallback["function_call_log"],
        }

    if not is_online():
        st.warning("⚠️ No internet detected. Running offline simulation.")
        fallback = OFFLINE_FALLBACKS[scenario_id]
        return {
            "mode": "OFFLINE (Auto-detected)",
            "reasoning": fallback["reasoning"],
            "alert_level": fallback["alert_level"],
            "function_call_log": fallback["function_call_log"],
        }

    return run_online(scenario, photo_description, api_key)

# ── Alert color helper ────────────────────────────────────────────────────────

def alert_color(level):
    return {
        "ADVISORY": "🟡",
        "WATCH": "🟠",
        "WARNING": "🔴",
        "CRITICAL": "🚨",
    }.get(level, "⚠️")

# ── Result extraction helpers ─────────────────────────────────────────────────

def get_highest_alert(function_call_log):
    order = ["ADVISORY", "WATCH", "WARNING", "CRITICAL"]
    highest = None
    for call in function_call_log:
        if call["function"] == "broadcast_alert":
            level = call["args"].get("alert_level", "ADVISORY")
            if highest is None or order.index(level) > order.index(highest):
                highest = level
    return highest or "ADVISORY"


def get_broadcast_messages(function_call_log):
    return [
        {
            "english": c["args"].get("message_english", ""),
            "tagalog": c["args"].get("message_tagalog", ""),
            "zones": c["args"].get("zones", []),
            "alert_level": c["args"].get("alert_level", "ADVISORY"),
        }
        for c in function_call_log
        if c["function"] == "broadcast_alert"
    ]


def get_routes(function_call_log):
    return [
        {
            "zone": c["args"].get("origin_zone", ""),
            "destination": c["args"].get("destination", ""),
            "route": c.get("result", {}).get("route", ""),
            "distance_km": c.get("result", {}).get("distance_km", ""),
            "walk_minutes": c.get("result", {}).get("walk_minutes", ""),
            "status": c.get("result", {}).get("status", ""),
        }
        for c in function_call_log
        if c["function"] == "calculate_safe_route"
    ]

# ── Session state ─────────────────────────────────────────────────────────────

if "latest_alert" not in st.session_state:
    st.session_state.latest_alert = None

# ── Tabs ──────────────────────────────────────────────────────────────────────

tab1, tab2 = st.tabs(["🧭 Command View — DRRM Officer", "📢 Resident View"])

# =============================================================================
# TAB 1 — COMMAND VIEW
# =============================================================================

with tab1:
    st.title("🌊 LIKAS")
    st.caption("Local Intelligence for Katastrophe Alert and Safety")

    api_key = get_api_key()
    if not api_key:
        st.info(
            "ℹ️ No API key configured — offline simulation is active. "
            "Set `GEMINI_API_KEY` in Streamlit secrets to enable live Gemma analysis.",
            icon="🔑",
        )

    st.divider()

    # ── Scenario selector ─────────────────────────────────────────────────────
    selected_label = st.selectbox(
        "📋 Select Scenario",
        list(SCENARIOS.keys()),
        help="Choose a pre-loaded flood scenario to analyze",
    )
    scenario = SCENARIOS[selected_label]

    # ── Mode toggle ───────────────────────────────────────────────────────────
    mode = st.radio(
        "Mode",
        ["🌐 Live Mode (Gemma API)", "🔴 Simulate Offline Mode"],
        index=1 if not scenario.get("internet", True) else 0,
        horizontal=True,
        key=f"mode_{selected_label}",
    )
    st.caption(
        "*Offline mode simulates how LIKAS behaves when typhoon knocks out internet "
        "— Gemma reasoning runs from cached data.*"
    )

    st.divider()

    # ── Sensor data panel ─────────────────────────────────────────────────────
    with st.expander("📡 Sensor Data", expanded=True):
        if "stations" in scenario:
            st.markdown(f"**Location:** {scenario['barangay']}")
            st.markdown(f"**Timestamp:** {scenario['timestamp']}")
            st.metric("Internet Status", "🔴 OFFLINE")
            if "last_sync" in scenario:
                st.caption(f"Last sync: {scenario['last_sync']}")
            st.metric("Total Population at Risk", f"{scenario['total_population']:,}")
            st.markdown("**Station Readings:**")
            for s in scenario["stations"]:
                pct = s["threshold_pct"]
                badge = "🚨" if pct >= 100 else ("🔴" if pct >= 90 else "🟠")
                st.metric(
                    label=f"{badge} {s['barangay']} ({s['id']})",
                    value=f"{s['water_level_m']}m",
                    delta=f"{pct}% of threshold — RISING {s['rate_m_per_hr']}m/hr",
                )
        else:
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.metric(
                    "Water Level",
                    f"{scenario['water_level_m']}m",
                    f"Threshold {scenario['threshold_m']}m ({scenario['threshold_pct']}%)",
                )
            with c2:
                st.metric(
                    "Rainfall 1hr / 3hr / 6hr",
                    f"{scenario['rain_1hr']}mm",
                    f"{scenario['rain_3hr']}mm | {scenario['rain_6hr']}mm",
                )
            with c3:
                st.metric("Trend", scenario["trend"], f"{scenario['rate_m_per_hr']}m/hr")
            with c4:
                inet = "🟢 ONLINE" if scenario.get("internet", True) else "🔴 OFFLINE"
                st.metric("Internet Status", inet)

            if scenario.get("flooded_roads"):
                st.markdown("**⛔ Known Flooded Roads:**")
                for road in scenario["flooded_roads"]:
                    st.markdown(f"- {road}")

    st.divider()

    # ── Photo upload / description ────────────────────────────────────────────
    if "stations" not in scenario:
        uploaded = st.file_uploader(
            "📷 Upload Field Photo (JPG/PNG)",
            type=["jpg", "jpeg", "png"],
            help="Upload a photo from the flood site for visual reference",
        )
        if uploaded:
            st.image(
                Image.open(uploaded),
                caption="Uploaded field photo",
                use_container_width=True,
            )

    photo_description = st.text_area(
        "Or describe the flood situation manually",
        value=scenario["photo_description"],
        height=100,
        help="This description is sent to Gemma for analysis. Edit to match field observations.",
    )

    st.divider()

    # ── Analyze button ────────────────────────────────────────────────────────
    if st.button(
        "🔍 Analyze Situation & Generate Alert",
        use_container_width=True,
        type="primary",
    ):
        with st.spinner("Gemma 4 is analyzing the situation..."):
            try:
                result = run_analysis(scenario, photo_description, mode, api_key)
            except requests.exceptions.Timeout:
                st.error("⏱️ Request timed out. Check connection or switch to Offline mode.")
                result = None
            except requests.exceptions.HTTPError as exc:
                st.error(f"🔴 API error: {exc}. Check GEMINI_API_KEY or switch to Offline mode.")
                result = None
            except Exception as exc:
                st.error(f"🔴 Unexpected error: {exc}")
                result = None

        if result:
            log = result.get("function_call_log", [])
            alert_level = result.get("alert_level") or get_highest_alert(log)
            messages = get_broadcast_messages(log)
            routes = get_routes(log)

            # Persist to session state for Resident View
            if messages:
                st.session_state.latest_alert = {
                    "alert_level": alert_level,
                    "barangay": scenario["barangay"],
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "messages": messages,
                    "routes": routes,
                    "evacuation_centers": scenario.get("evacuation_centers", []),
                }

            st.success(f"Analysis complete — Mode: {result['mode']}")
            st.divider()

            # ── Reasoning ─────────────────────────────────────────────────────
            st.subheader("🧠 Gemma Reasoning")
            st.info(
                result.get("reasoning")
                or "*(Reasoning embedded in function calls — see ⚙️ Functions Called below.)*"
            )

            # ── Alert level badge ──────────────────────────────────────────────
            st.subheader("⚠️ Alert Level")
            emoji = alert_color(alert_level)
            if alert_level == "CRITICAL":
                st.error(f"{emoji} **{alert_level}** — Mandatory evacuation required")
            elif alert_level == "WARNING":
                st.warning(f"{emoji} **{alert_level}** — Voluntary evacuation in effect")
            elif alert_level == "WATCH":
                st.warning(f"{emoji} **{alert_level}** — Prepare to evacuate, stay alert")
            else:
                st.info(f"{emoji} **{alert_level}** — Monitor situation")

            # ── Functions called ───────────────────────────────────────────────
            with st.expander(f"⚙️ Functions Called ({len(log)})"):
                for i, call in enumerate(log, 1):
                    st.markdown(f"**{i}. `{call['function']}`**")
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.markdown("*Arguments*")
                        st.json(call["args"])
                    with col_b:
                        st.markdown("*Result*")
                        st.json(call["result"])
                    if i < len(log):
                        st.divider()

            # ── Alert messages ─────────────────────────────────────────────────
            if messages:
                st.subheader("📢 Alert Message")
                for msg in messages:
                    zones_str = ", ".join(msg["zones"])
                    st.markdown(
                        f"**{alert_color(msg['alert_level'])} {msg['alert_level']} — {zones_str}**"
                    )
                    col_en, col_tl = st.columns(2)
                    with col_en:
                        st.markdown("🇬🇧 **English**")
                        st.markdown(msg["english"])
                    with col_tl:
                        st.markdown("🇵🇭 **Tagalog**")
                        st.markdown(msg["tagalog"])
                    st.divider()

            # ── Evacuation routes ──────────────────────────────────────────────
            if routes:
                st.subheader("🗺️ Evacuation Route")
                for r in routes:
                    status_icon = "✅" if r["status"] == "CLEAR" else "⚠️"
                    st.success(
                        f"**{status_icon} {r['zone']} → {r['destination']}**\n\n"
                        f"📍 {r['route']}\n\n"
                        f"📏 {r['distance_km']} km  |  🚶 ~{r['walk_minutes']} min on foot"
                    )

# =============================================================================
# TAB 2 — RESIDENT VIEW
# =============================================================================

with tab2:
    alert = st.session_state.latest_alert

    if alert is None:
        st.info("📵 No alert generated yet. Run an analysis in the Command View tab first.")
        st.markdown("---")
        st.markdown("### How to generate an alert")
        st.markdown("1. Go to **🧭 Command View — DRRM Officer**")
        st.markdown("2. Select a scenario")
        st.markdown("3. Click **🔍 Analyze Situation & Generate Alert**")
    else:
        level = alert["alert_level"]
        emoji = alert_color(level)

        if level == "CRITICAL":
            st.error(f"# 🚨 {level}")
        elif level == "WARNING":
            st.warning(f"# 🔴 {level}")
        elif level == "WATCH":
            st.warning(f"# 🟠 {level}")
        else:
            st.info(f"# 🟡 {level}")

        st.markdown(f"### 📍 {alert['barangay']}")
        st.caption(f"⏱️ {alert['timestamp']}")
        st.divider()

        # Tagalog instructions — highest-priority message first
        if alert["messages"]:
            primary = alert["messages"][0]
            st.markdown("## 📋 INSTRUCTIONS")
            st.markdown(f"### {primary['tagalog']}")
            st.divider()

            for msg in alert["messages"][1:]:
                zones_str = ", ".join(msg["zones"])
                st.markdown(f"**{msg['alert_level']} — {zones_str}**")
                st.markdown(msg["tagalog"])
                st.divider()

        # Safe route — step-by-step
        if alert["routes"]:
            st.markdown("## 🗺️ SAFE ROUTE")
            for r in alert["routes"]:
                for i, step in enumerate(r["route"].split(" → "), 1):
                    st.markdown(f"{i}. **{step}**")
                st.caption(f"📏 {r['distance_km']} km  |  🚶 ~{r['walk_minutes']} min")
                st.divider()

        # Evacuation centers
        centers = alert.get("evacuation_centers", [])
        if centers:
            st.markdown("## 📍 EVACUATION CENTER")
            for center in centers:
                st.markdown(f"**{center['name']}**")
                st.markdown(
                    f"📏 {center['distance_km']} km away  |  👥 Capacity: {center['capacity']}"
                )
                st.divider()

        # English version (collapsible)
        if alert["messages"]:
            with st.expander("🇬🇧 English Version"):
                for msg in alert["messages"]:
                    zones_str = ", ".join(msg["zones"])
                    st.markdown(f"**{msg['alert_level']} — {zones_str}**")
                    st.markdown(msg["english"])
