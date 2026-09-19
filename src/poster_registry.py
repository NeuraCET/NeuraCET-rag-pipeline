"""Poster Registry for Drishti 2026

Manages the mapping of 2026 events to their static poster image files.
Strictly ensures posters are ONLY returned for 2026 events.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Optional

POSTERS_DIR = Path(__file__).resolve().parent.parent / "posters"
INDEX_PATH = POSTERS_DIR / "poster_index.json"

# Explicit high-confidence mappings from normalized keywords/event identifiers to actual poster filenames
POSTER_MAPPINGS: Dict[str, str] = {
    "8bit": "8bit.jpeg",
    "8-bit": "8bit.jpeg",
    "ansys": "ansys.jpeg",
    "arduino": "arduino.jpeg",
    "beyond progress": "beyondprogresstalk.jpeg",
    "biennale": "biennale.jpeg",
    "cad clash": "cadclash.png",
    "dance": "dance.jpeg",
    "dance workshop": "dance.jpeg",
    "decoding ai": "decodingaiworkshop.jpeg",
    "drone": "dronrace.jpg",
    "fpv": "dronrace.jpg",
    "sim-racing": "dronrace.jpg",
    "fpv drone sim racing": "dronrace.jpg",
    "drone sim racing": "dronrace.jpg",
    "ea fc": "eafc.jpeg",
    "fifa": "eafc.jpeg",
    "e-football": "efootball.jpeg",
    "efootball": "efootball.jpeg",
    "mahindra engine": "engineworkshop.jpeg",
    "engine assembly": "engineworkshop.jpeg",
    "engine dismantling": "engineworkshop.jpeg",
    "maxximo": "engineworkshop.jpeg",
    "supro": "engineworkshop.jpeg",
    "automobile engine": "engineworkshop.jpeg",
    "ic engine": "engineworkshop.jpeg",
    "escape room": "escaperoom.jpeg",
    "escape room - chaturanga cet": "escaperoom.jpeg",
    "etab": "etabs.png",
    "etabs": "etabs.png",
    "etab workshop": "etabs.png",
    "fig my ui": "figmyui.jpeg",
    "figma": "figmyui.jpeg",
    "industrial automation": "industrialautomation.jpeg",
    "learning circle": "learningcirclecloud.jpeg",
    "agentic ai": "learningcirclecloud.jpeg",
    "marathon": "marathon.jpeg",
    "d'run": "marathon.jpeg",
    "matlab": "matlab.jpeg",
    "model rocketry": "modelrocketry.jpeg",
    "model rocketry 101": "modelrocketry.jpeg",
    "rocketry": "modelrocketry.jpeg",
    "nix": "nix&nixos.jpeg",
    "nixos": "nix&nixos.jpeg",
    "nixos workshop": "nix&nixos.jpeg",
    "opencv": "opencv.jpeg",
    "computer vision": "opencv.jpeg",
    "overdefined": "overdefined.jpeg",
    "cad hackathon": "overdefined.jpeg",
    "privatisation of space": "paneldiscussionprivspace.jpeg",
    "space industry": "paneldiscussionprivspace.jpeg",
    "space industry panel discussion": "paneldiscussionprivspace.jpeg",
    "pcb": "pcbdesignworkshop.jpeg",
    "pcb design": "pcbdesignworkshop.jpeg",
    "pcb design workshop": "pcbdesignworkshop.jpeg",
    "pixelcraft": "pixelcraft.jpeg",
    "pixel craft": "pixelcraft.jpeg",
    "quantum": "quantumcomputingtech.jpeg",
    "quantum computing": "quantumcomputingtech.jpeg",
    "talk session on quantum computing": "quantumcomputingtech.jpeg",
    "photons": "quantumcomputingtech.jpeg",
    "race car": "racecardynamics.jpeg",
    "race car dynamics": "racecardynamics.jpeg",
    "rc plane": "rcplane.jpeg",
    "rc plane workshop": "rcplane.jpeg",
    "revitx": "revitx.png",
    "revit": "revitx.png",
    "bim": "revitx.png",
    "robotic arm": "roboticarmdev.jpeg",
    "robotic arm workshop": "roboticarmdev.jpeg",
    "robowar": "robowar.jpeg",
    "robowar 8kg": "robowar.jpeg",
    "robowar (8kg)": "robowar.jpeg",
    "robowar 25kg": "robowar.jpeg",
    "robowar (25kg)": "robowar.jpeg",
    "robocet": "robowar.jpeg",
    "robosoccer": "robowar.jpeg",
    "sensor fusion": "sensorfusion101.jpeg",
    "photography competition": "shephotography.jpeg",
    "shecet photography": "shephotography.jpeg",
    "she quiz": "shequiz.jpeg",
    "she cet": "shequiz.jpeg",
    "competition - she cet": "shequiz.jpeg",
    "women in tech quiz": "shequiz.jpeg",
    "quiz competition - women in tech": "shequiz.jpeg",
    "signal showdown": "signalshowdown.jpeg",
    "solidworks": "soldiworks.jpeg",
    "stellar odyssey": "stellarodysseytreasurehunt.jpeg",
    "treasure hunt": "stellarodysseytreasurehunt.jpeg",
    "tinyml": "tinyml.jpeg",
    "edge intelligence": "tinyml.jpeg",
    "unreal engine": "unrealengine.jpeg",
    "unreal engines": "unrealengine.jpeg",
    "unreal engines workshop": "unrealengine.jpeg",
    "unreal": "unrealengine.jpeg",
    "valorant": "valorant.jpeg",
    "verilog": "verilogandfgpa.jpeg",
    "fpga": "verilogandfgpa.jpeg",
    "website re:design": "webredesign.jpeg",
    "web redesign": "webredesign.jpeg",
    "whisper challenge": "whisperchlng.jpeg",
}


class PosterRegistry:
    def __init__(self, posters_dir: Path = POSTERS_DIR):
        self.posters_dir = posters_dir
        self.available_files = set()
        if self.posters_dir.exists():
            self.available_files = {
                f for f in os.listdir(self.posters_dir) if f != "poster_index.json"
            }

    def get_poster_for_query(self, query: str) -> Optional[str]:
        """Resolve a poster path for a query.
        
        POSTERS ARE ONLY FOR 2026 EVENTS.
        If the query relates to 2022, 2024, or unknown event, returns None.
        """
        lower_q = query.lower()

        # Past edition check: strictly NO poster if query asks about past years
        if any(yr in lower_q for yr in ["2024", "'24", "drishti 24", "2022", "'22", "drishti 22", "2019"]):
            if "2026" not in lower_q and "26" not in lower_q:
                return None

        # Check direct keyword mappings against query (longest phrase first)
        for key, filename in sorted(POSTER_MAPPINGS.items(), key=lambda x: len(x[0]), reverse=True):
            pattern = r"(?:\b|_)" + re.escape(key) + r"(?:\b|_)"
            if re.search(pattern, lower_q):
                if filename in self.available_files:
                    return f"/posters/{filename}"

        return None


# Global singleton
registry = PosterRegistry()
