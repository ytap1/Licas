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
