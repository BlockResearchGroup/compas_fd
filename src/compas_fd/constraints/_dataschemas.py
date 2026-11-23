"""Geometry payload schemas used by the legacy constraint serialization API."""

from collections.abc import Mapping
from copy import deepcopy

# COMPAS 3 removed the geometry classes' DATASCHEMA attributes. Retain the
# COMPAS 2 payload schemas for callers using the constraint classes' schemas.
NUMBER = {"type": "number"}
INTEGER = {"type": "integer"}
DEGREE = {"type": "integer", "exclusiveMinimum": 0}
BOOLEAN = {"type": "boolean"}
XYZ = {"type": "array", "items": NUMBER, "minItems": 3, "maxItems": 3}
NUMBERS = {"type": "array", "items": NUMBER}
INTEGERS = {"type": "array", "items": INTEGER}
FRAME = {"type": "object", "properties": {"point": XYZ, "xaxis": XYZ, "yaxis": XYZ}, "required": ["point", "xaxis", "yaxis"]}
CIRCLE = {"type": "object", "properties": {"radius": {"type": "number", "minimum": 0}, "frame": FRAME}, "required": ["radius", "frame"]}
LINE = {"type": "object", "properties": {"start": XYZ, "end": XYZ}, "required": ["start", "end"]}
PLANE = {"type": "object", "properties": {"point": XYZ, "normal": XYZ}, "required": ["point", "normal"]}
CURVE = {
    "type": "object",
    "properties": {
        "points": {"type": "array", "items": XYZ, "minItems": 2},
        "weights": NUMBERS,
        "knots": NUMBERS,
        "multiplicities": INTEGERS,
        "degree": DEGREE,
        "is_periodic": BOOLEAN,
    },
    "minProperties": 6,
    "additionalProperties": False,
}
SURFACE = {
    "type": "object",
    "properties": {
        "points": {"type": "array", "items": {"type": "array", "items": XYZ}},
        "weights": {"type": "array", "items": NUMBERS},
        "knots_u": NUMBERS,
        "knots_v": NUMBERS,
        "mults_u": INTEGERS,
        "mults_v": INTEGERS,
        "degree_u": DEGREE,
        "degree_v": DEGREE,
        "is_periodic_u": BOOLEAN,
        "is_periodic_v": BOOLEAN,
    },
    "minProperties": 10,
    "additionalProperties": False,
}


def constraint_schema(geometry: Mapping[str, object]) -> dict[str, object]:
    return {
        "type": "object",
        "properties": {"geometry": deepcopy(geometry), "rhino_guid": {"type": "string"}},
        "required": ["geometry"],
    }
