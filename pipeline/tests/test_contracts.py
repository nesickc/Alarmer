"""Checks the shared contract in contracts/ (plan task 0.3, docs/adr/0011).

The level engines (plan 1.9 in Python, 3.2 in Kotlin) will run the golden vectors. These tests keep the files
themselves honest: valid against their schemas, consistent with each other, and covering every spec §6 rule.
"""

import json
import re
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

import alarmer

REPO = Path(__file__).resolve().parents[2]
CONTRACTS = REPO / "contracts"
GOLDEN = CONTRACTS / "golden"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validator(schema: dict, definition: str | None = None) -> Draft202012Validator:
    """A validator for the whole schema, or for one of its $defs."""
    if definition is not None:
        schema = {"$ref": f"#/$defs/{definition}", "$defs": schema["$defs"]}
    return Draft202012Validator(schema, format_checker=Draft202012Validator.FORMAT_CHECKER)


def errors(v: Draft202012Validator, instance) -> list[str]:
    return [f"{'/'.join(map(str, e.absolute_path))}: {e.message}" for e in v.iter_errors(instance)]


RECORD_SCHEMA = load(CONTRACTS / "record.schema.json")
GOLDEN_SCHEMA = load(GOLDEN / "golden.schema.json")
ENVELOPE = validator(RECORD_SCHEMA)
RECORD = validator(RECORD_SCHEMA, "record")

EXAMPLES = sorted((CONTRACTS / "examples").glob("*.json"))
VALID_TRACK = load(CONTRACTS / "examples" / "envelope.json")["records"][0]

WORLD = load(GOLDEN / "world.json")
PARAMS = load(GOLDEN / "params.json")
AREAS = {a["id"]: a for a in WORLD["areas"]}
LAUNCH_AREAS = {a["id"]: a for a in WORLD["launch_areas"]}
USERS = {u["id"]: u for u in WORLD["users"]}
VECTOR_FILES = sorted((GOLDEN / "vectors").glob("*.json"))
VECTORS = [v for path in VECTOR_FILES for v in load(path)["vectors"]]


# --- Record schema -----------------------------------------------------------------------------------------------


@pytest.mark.parametrize("schema", [RECORD_SCHEMA, GOLDEN_SCHEMA], ids=["record", "golden"])
def test_schema_is_valid(schema):
    Draft202012Validator.check_schema(schema)


def test_schema_version_matches_pipeline():
    assert RECORD_SCHEMA["properties"]["v"]["const"] == alarmer.WIRE_FORMAT_VERSION


@pytest.mark.parametrize("path", EXAMPLES, ids=lambda p: p.stem)
def test_example_envelope_is_valid(path):
    assert errors(ENVELOPE, load(path)) == []


def test_spec_record_example_is_valid():
    spec = (REPO / "docs" / "spec.md").read_text(encoding="utf-8")
    section = spec.split("### 5.2 Record", 1)[1]
    example = re.search(r"```json\n(.*?)\n```", section, re.DOTALL).group(1)
    assert errors(RECORD, json.loads(example)) == []


def test_envelope_of_another_version_is_rejected():
    assert errors(ENVELOPE, load(CONTRACTS / "examples" / "heartbeat.json") | {"v": 2})


@pytest.mark.parametrize("field", RECORD_SCHEMA["$defs"]["record"]["required"])
def test_required_field_is_required(field):
    assert errors(RECORD, {k: v for k, v in VALID_TRACK.items() if k != field})


INVALID_CHANGES = {
    "unknown kind": {"kind": "drone"},
    "unknown type": {"type": "uav.geran_9"},
    "raw post text": {"text": "Шахед на Харків"},
    "local time": {"last_seen": "2026-10-30T23:14:02+02:00"},
    "conf above 1": {"conf": 1.5},
    "heading of 360": {"heading": {"deg": 360, "pm": 30}},
    "empty area list": {"area": []},
    "dest without radius": {"dest": {"id": None, "lat": 49.99, "lon": 36.23}},
    "track without position": {"pos": None},
    "launch without type": {"kind": "launch", "type": None},
    "reason on a track": {"reason": {"kind": "track"}},
    "official alert without area": {"kind": "official_alert"},
}


@pytest.mark.parametrize("change", INVALID_CHANGES.values(), ids=INVALID_CHANGES.keys())
def test_invalid_record_is_rejected(change):
    assert errors(RECORD, VALID_TRACK | change)


# Types aren't tied to kinds (ADR-0011): a new fast weapon's launch, or a ballistic missile with a known position.
VALID_CHANGES = {
    "track of a ballistic missile": {"type": "ballistic.iskander_m"},
    "launch of a cruise missile": {"kind": "launch", "type": "cruise.kh22"},
    "threat of a cruise missile": {"kind": "ballistic_threat", "type": "cruise.kh22"},
}


@pytest.mark.parametrize("change", VALID_CHANGES.values(), ids=VALID_CHANGES.keys())
def test_any_type_goes_with_any_typed_kind(change):
    assert errors(RECORD, VALID_TRACK | change) == []


# --- Golden vectors and their fixtures --------------------------------------------------------------------------


def test_world_and_params_match_schema():
    assert errors(validator(GOLDEN_SCHEMA, "world"), WORLD) == []
    assert errors(validator(GOLDEN_SCHEMA, "params"), PARAMS) == []


@pytest.mark.parametrize("path", VECTOR_FILES, ids=lambda p: p.stem)
def test_vector_file_matches_schema(path):
    assert errors(validator(GOLDEN_SCHEMA, "vectorFile"), load(path)) == []


@pytest.mark.parametrize("vector", VECTORS, ids=lambda v: v["id"])
def test_vector_record_is_valid(vector):
    assert errors(RECORD, vector["record"]) == []


@pytest.mark.parametrize("vector", VECTORS, ids=lambda v: v["id"])
def test_vector_references_exist(vector):
    record = vector["record"]
    assert vector["user"] in USERS
    for area in (record.get("area") or []) + (record.get("no_threat_to") or []):
        assert area in AREAS
    if record.get("launch_area"):
        assert record["launch_area"] in LAUNCH_AREAS
    if (record.get("dest") or {}).get("id"):
        assert record["dest"]["id"] in AREAS


def test_vector_ids_are_unique():
    ids = [v["id"] for v in VECTORS]
    assert len(ids) == len(set(ids))


def test_every_rule_has_a_vector():
    rules = set(GOLDEN_SCHEMA["$defs"]["rule"]["enum"])
    assert rules - {rule for v in VECTORS for rule in v["rules"]} == set()


PARENT_LEVEL = {
    "oblast": None,
    "raion": "oblast",
    "hromada": "raion",
    "district": "hromada",
    "neighbourhood": "hromada",
}


def test_area_parents_are_one_level_up():
    for area in AREAS.values():
        parent = area["parent"]
        assert (AREAS[parent]["level"] if parent else None) == PARENT_LEVEL[area["level"]], area["id"]


def test_neighbours_are_mutual_hromadas():
    for area in AREAS.values():
        for other in area.get("neighbours", []):
            assert area["level"] == AREAS[other]["level"] == "hromada"
            assert area["id"] in AREAS[other].get("neighbours", [])


def test_polygon_rings_are_closed():
    geometries = [a["geometry"] for a in AREAS.values() if "geometry" in a]
    geometries += [a["geometry"] for a in LAUNCH_AREAS.values()]
    for ring in (g["coordinates"][0] for g in geometries if g["type"] == "Polygon"):
        assert ring[0] == ring[-1]


def test_params_fallback_launch_area_exists():
    assert PARAMS["ballistic"]["fallback_launch_area"] in LAUNCH_AREAS


def contains(polygon: dict, lat: float, lon: float) -> bool:
    """Even-odd ray casting in plain lon/lat; enough for the fixture's small, crude polygons."""
    inside = False
    ring = polygon["coordinates"][0]
    for (x1, y1), (x2, y2) in zip(ring, ring[1:], strict=False):
        if (y1 > lat) != (y2 > lat) and lon < x1 + (lat - y1) * (x2 - x1) / (y2 - y1):
            inside = not inside
    return inside


@pytest.mark.parametrize("user", WORLD["users"], ids=lambda u: u["id"])
def test_user_lies_in_exactly_its_listed_areas(user):
    containing = {
        a["id"] for a in AREAS.values() if "geometry" in a and contains(a["geometry"], user["lat"], user["lon"])
    }
    assert containing == set(user["areas"])
