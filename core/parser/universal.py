"""
AeroNova Polyglot Optimization and Structural Decomposition Pipeline
Module: core/parser/universal
Implementation: Absolute, Multi-Era Self-Healing Grammar Loader
"""
import os
import sys
import re
import ast
import ctypes
import logging
import importlib
from enum import Enum
import hashlib
import time
import warnings
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

class UniversalParseError(Exception):
    """Raised when the parser cannot load a grammar module or parse source code."""
    pass

logger = logging.getLogger("AeroNova.Parser.Universal")
if not logger.handlers:
    logger.addHandler(logging.NullHandler())

MAX_FILE_BYTES = 1_000_000
PARSE_TIMEOUT_SECONDS = 5.0

LANGUAGE_BY_EXTENSION: Dict[str, str] = {
    ".py": "python", ".pyi": "python",
    ".rs": "rust",
    ".cpp": "cpp", ".cc": "cpp", ".cxx": "cpp", ".hpp": "cpp", ".hh": "cpp", ".hxx": "cpp",
    ".c": "c", ".h": "c",
    ".f": "fortran", ".f90": "fortran", ".f95": "fortran",
    ".f03": "fortran", ".for": "fortran",
    ".cob": "cobol", ".cbl": "cobol", ".cpy": "cobol",
}

GRAMMAR_MODULES: Dict[str, str] = {
    "python": "tree_sitter_python",
    "rust": "tree_sitter_rust",
    "cpp": "tree_sitter_cpp",
    "c": "tree_sitter_c",
    "fortran": "tree_sitter_fortran",
    "cobol": "tree_sitter_cobol",
}

_VERIFIED_LANGUAGE_CACHE: Dict[str, Any] = {}

_PyCapsule_IsValid: Optional[Any] = None
_PyCapsule_GetPointer: Optional[Any] = None
_PyCapsule_GetName: Optional[Any] = None
_PyCapsule_New: Optional[Any] = None

try:
    _pythonapi = ctypes.pythonapi
    if hasattr(_pythonapi, "PyCapsule_IsValid"):
        _PyCapsule_IsValid = _pythonapi.PyCapsule_IsValid
        _PyCapsule_IsValid.argtypes = [ctypes.py_object, ctypes.c_char_p]
        _PyCapsule_IsValid.restype = ctypes.c_int

    if hasattr(_pythonapi, "PyCapsule_GetPointer"):
        _PyCapsule_GetPointer = _pythonapi.PyCapsule_GetPointer
        _PyCapsule_GetPointer.argtypes = [ctypes.py_object, ctypes.c_char_p]
        _PyCapsule_GetPointer.restype = ctypes.c_void_p

    if hasattr(_pythonapi, "PyCapsule_GetName"):
        _PyCapsule_GetName = _pythonapi.PyCapsule_GetName
        _PyCapsule_GetName.argtypes = [ctypes.py_object]
        _PyCapsule_GetName.restype = ctypes.c_char_p

    if hasattr(_pythonapi, "PyCapsule_New"):
        _PyCapsule_New = _pythonapi.PyCapsule_New
        _PyCapsule_New.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_void_p]
        _PyCapsule_New.restype = ctypes.py_object
except Exception as exc:
    logger.warning("Dynamic CPython C-API bindings could not be fully initialized: %s", exc)

_tree_sitter_module: Optional[Any] = None
_TreeSitterParserClass: Optional[Any] = None
_TreeSitterLanguageClass: Optional[Any] = None

def _import_tree_sitter() -> Tuple[Any, Any, Any]:
    global _tree_sitter_module, _TreeSitterParserClass, _TreeSitterLanguageClass
    if _tree_sitter_module is not None:
        return _tree_sitter_module, _TreeSitterParserClass, _TreeSitterLanguageClass
    try:
        import tree_sitter
        _tree_sitter_module = tree_sitter
        _TreeSitterParserClass = tree_sitter.Parser
        _TreeSitterLanguageClass = tree_sitter.Language
        return _tree_sitter_module, _TreeSitterParserClass, _TreeSitterLanguageClass
    except ImportError as err:
        logger.critical("Dependency tree-sitter is missing from the active environment.")
        raise ImportError("The 'tree-sitter' library is required to run the AeroNova parser pipeline.") from err

def verify_language_behavioral(language_obj: Any) -> bool:
    if language_obj is None:
        return False
    _, parser_cls, _ = _import_tree_sitter()
    try:
        parser_instance = parser_cls(language_obj)
        syntax_tree = parser_instance.parse(b" ")
        if syntax_tree is not None:
            return True
    except Exception:
        pass
    try:
        parser_instance = parser_cls()
        if hasattr(parser_instance, "set_language"):
            parser_instance.set_language(language_obj)
            syntax_tree = parser_instance.parse(b" ")
            if syntax_tree is not None:
                return True
        elif hasattr(parser_instance, "language"):
            parser_instance.language = language_obj
            syntax_tree = parser_instance.parse(b" ")
            if syntax_tree is not None:
                return True
    except Exception:
        pass
    return False

def extract_raw_pointer(capsule_or_int: Any) -> Optional[int]:
    if isinstance(capsule_or_int, int):
        return capsule_or_int
    if _PyCapsule_GetPointer is None:
        return None
    capsule_name = None
    if _PyCapsule_GetName is not None:
        try:
            capsule_name = _PyCapsule_GetName(capsule_or_int)
        except Exception:
            capsule_name = None
    try:
        ptr = _PyCapsule_GetPointer(capsule_or_int, capsule_name)
        if ptr:
            return int(ptr)
    except Exception as exc:
        logger.debug("Failed to extract raw pointer via PyCapsule_GetPointer: %s", exc)
    try:
        ptr = _PyCapsule_GetPointer(capsule_or_int, None)
        if ptr:
            return int(ptr)
    except Exception:
        pass
    return None

def wrap_pointer_in_capsule(ptr: int, name: bytes = b"tree_sitter.Language") -> Optional[Any]:
    if _PyCapsule_New is None:
        return None
    try:
        return _PyCapsule_New(ctypes.c_void_p(ptr), name, None)
    except Exception as exc:
        logger.debug("Failed to create PyCapsule from raw pointer: %s", exc)
        return None

def instantiate_era_compatible_language(target_ref: Any, name: str) -> Optional[Any]:
    _, _, lang_cls = _import_tree_sitter()

    # 1. Duck-Typing: If it is already a fully formed Language instance, test it
    if type(target_ref).__name__ == "Language" or hasattr(target_ref, "query"):
        if verify_language_behavioral(target_ref):
            return target_ref

    # 2. Extract raw C memory address regardless of incoming wrapper type
    ptr = None
    if isinstance(target_ref, int):
        ptr = target_ref
    elif target_ref is not None and (type(target_ref).__name__ == "PyCapsule" or "Capsule" in str(type(target_ref))):
        ptr = extract_raw_pointer(target_ref)

    if ptr is not None:
        # Try direct integer injection if supported by the binding compilation
        try:
            lang_instance = lang_cls(ptr, name)
            if verify_language_behavioral(lang_instance): return lang_instance
        except Exception: pass
        try:
            lang_instance = lang_cls(ptr)
            if verify_language_behavioral(lang_instance): return lang_instance
        except Exception: pass

        # Repackage the pointer into capsules matching every historical naming era
        for capsule_name in [b"tree_sitter.Language", b"tree_sitter_language", name.encode("utf-8"), None]:
            capsule = wrap_pointer_in_capsule(ptr, capsule_name)
            if capsule is not None:
                try:
                    lang_instance = lang_cls(capsule, name)
                    if verify_language_behavioral(lang_instance): return lang_instance
                except Exception: pass
                try:
                    lang_instance = lang_cls(capsule)
                    if verify_language_behavioral(lang_instance): return lang_instance
                except Exception: pass

    # 3. Direct Fallback Pass
    try:
        lang_instance = lang_cls(target_ref, name)
        if verify_language_behavioral(lang_instance): return lang_instance
    except Exception: pass
    try:
        lang_instance = lang_cls(target_ref)
        if verify_language_behavioral(lang_instance): return lang_instance
    except Exception: pass

    return None

def load_language(language_name: str, library_path: Optional[str] = None) -> Any:
    normalized_name = language_name.lower().replace("-", "_")
    cache_key = f"{normalized_name}:{library_path or 'none'}"
    if cache_key in _VERIFIED_LANGUAGE_CACHE:
        return _VERIFIED_LANGUAGE_CACHE[cache_key]

    try:
        module_target = GRAMMAR_MODULES.get(normalized_name, f"tree_sitter_{normalized_name}")
        grammar_module = importlib.import_module(module_target)
        for attr_name in ("language", "get_language", "binding"):
            if hasattr(grammar_module, attr_name):
                resolved_endpoint = getattr(grammar_module, attr_name)
                if callable(resolved_endpoint):
                    try:
                        resolved_endpoint = resolved_endpoint()
                    except Exception:
                        continue
                lang_instance = instantiate_era_compatible_language(resolved_endpoint, normalized_name)
                if lang_instance is not None:
                    _VERIFIED_LANGUAGE_CACHE[cache_key] = lang_instance
                    return lang_instance
    except ImportError:
        pass

    for package_name in ("tree_sitter_language_pack", "tree_sitter_languages"):
        try:
            pack_module = importlib.import_module(package_name)
            for func_name in ("get_language", "get_binding"):
                if hasattr(pack_module, func_name):
                    resolver_func = getattr(pack_module, func_name)
                    try:
                        resolved_endpoint = resolver_func(normalized_name)
                        lang_instance = instantiate_era_compatible_language(resolved_endpoint, normalized_name)
                        if lang_instance is not None:
                            _VERIFIED_LANGUAGE_CACHE[cache_key] = lang_instance
                            return lang_instance
                    except Exception:
                        continue
        except ImportError:
            pass

    if library_path and os.path.exists(library_path):
        try:
            abs_library_path = os.path.abspath(library_path)
            shared_library = ctypes.CDLL(abs_library_path)
            target_symbol = f"tree_sitter_{normalized_name}"
            if not hasattr(shared_library, target_symbol):
                target_symbol = f"tree_sitter_{normalized_name}_language"
            if hasattr(shared_library, target_symbol):
                symbol_func = getattr(shared_library, target_symbol)
                symbol_func.restype = ctypes.c_void_p
                symbol_func.argtypes = []
                raw_ptr = symbol_func()
                if raw_ptr:
                    lang_instance = instantiate_era_compatible_language(raw_ptr, normalized_name)
                    if lang_instance is not None:
                        _VERIFIED_LANGUAGE_CACHE[cache_key] = lang_instance
                        return lang_instance
        except Exception as exc:
            logger.debug("Failed to load language dynamic library via CDLL: %s", exc)

    raise UniversalParseError(f"Failed to load and behaviorally validate grammar '{language_name}'")

def _load_language(language: str):
    return load_language(language)

def _build_parser(language: str):
    return get_universal_parser(language)._raw_parser

class UniversalParser:
    def __init__(self, language_name: str, library_path: Optional[str] = None):
        _import_tree_sitter()
        self.language_name: str = language_name
        self.library_path: Optional[str] = library_path
        self.language_asset: Any = load_language(language_name, library_path)
        self._raw_parser: Any = self._instantiate_parser()

    def _instantiate_parser(self) -> Any:
        _, parser_cls, _ = _import_tree_sitter()
        try:
            return parser_cls(self.language_asset)
        except (TypeError, ValueError):
            pass
        try:
            parser_instance = parser_cls()
            if hasattr(parser_instance, "set_language"):
                parser_instance.set_language(self.language_asset)
            elif hasattr(parser_instance, "language"):
                parser_instance.language = self.language_asset
            else:
                setattr(parser_instance, "language", self.language_asset)
            return parser_instance
        except Exception as exc:
            raise UniversalParseError(f"Failed to bind language grammar to Parser across all eras: {exc}")

    def parse(self, source_code: Union[str, bytes], old_tree: Optional[Any] = None) -> Any:
        encoded_bytes: bytes = source_code.encode("utf-8") if isinstance(source_code, str) else source_code
        try:
            return self._raw_parser.parse(encoded_bytes, old_tree)
        except TypeError:
            pass
        try:
            return self._raw_parser.parse(encoded_bytes)
        except Exception as exc:
            raise UniversalParseError(f"Parser execution failed under active runtime: {exc}")

def get_universal_parser(language_name: str, library_path: Optional[str] = None) -> UniversalParser:
    return UniversalParser(language_name, library_path)

# --- BACKWARD COMPATIBLE UAST TRANSFORMATION MIXINS ---
class NodeCategory(str, Enum):
    DECLARATION = "DECLARATION"; STATEMENT = "STATEMENT"; EXPRESSION = "EXPRESSION"
    IDENTIFIER = "IDENTIFIER"; LITERAL = "LITERAL"; TYPE = "TYPE"; KEYWORD = "KEYWORD"
    COMMENT = "COMMENT"; PUNCTUATION = "PUNCTUATION"; MODULE = "MODULE"
    ERROR = "ERROR"; UNKNOWN = "UNKNOWN"

CANONICAL_KIND: Dict[str, Dict[str, str]] = {
    "python": {"function_definition": "function_declaration", "class_definition": "type_declaration", "import_statement": "import_declaration", "import_from_statement": "import_declaration", "module": "translation_unit"},
    "rust": {"function_item": "function_declaration", "struct_item": "type_declaration", "enum_item": "type_declaration", "union_item": "type_declaration", "trait_item": "type_declaration", "type_item": "type_declaration", "use_declaration": "import_declaration", "mod_item": "module_declaration", "source_file": "translation_unit"},
    "cpp": {"function_definition": "function_declaration", "class_specifier": "type_declaration", "struct_specifier": "type_declaration", "namespace_definition": "module_declaration", "preproc_include": "import_declaration", "translation_unit": "translation_unit"},
    "c": {"function_definition": "function_declaration", "struct_specifier": "type_declaration", "union_specifier": "type_declaration", "preproc_include": "import_declaration", "translation_unit": "translation_unit"}
}

_COMMENT_TYPES = {"comment", "line_comment", "block_comment", "doc_comment"}
def detect_language(path: Union[str, Path]) -> Optional[str]:
    return LANGUAGE_BY_EXTENSION.get(Path(path).suffix.lower())

def supported_extensions() -> List[str]:
    return sorted(LANGUAGE_BY_EXTENSION)

def supported_languages() -> List[str]:
    return sorted(set(LANGUAGE_BY_EXTENSION.values()))

def _categorize(language: str, node_type: str, named: bool, is_error: bool, is_missing: bool) -> NodeCategory:
    if is_error or is_missing or node_type == "ERROR": return NodeCategory.ERROR
    if node_type in _COMMENT_TYPES: return NodeCategory.COMMENT
    canonical = CANONICAL_KIND.get(language, {}).get(node_type)
    if canonical:
        if canonical.endswith("_declaration"): return NodeCategory.DECLARATION
        if canonical.endswith("translation_unit"): return NodeCategory.MODULE
    if not named: return NodeCategory.KEYWORD if node_type.isalpha() else NodeCategory.PUNCTUATION
    lowered = node_type.lower()
    if lowered.endswith(("_definition", "_declaration", "_item", "_specifier", "_declarator")): return NodeCategory.DECLARATION
    if lowered.endswith(("_statement",)): return NodeCategory.STATEMENT
    if lowered.endswith(("_expression", "_expr")): return NodeCategory.EXPRESSION
    if lowered in ("type_identifier", "primitive_type", "type"): return NodeCategory.TYPE
    if "identifier" in lowered: return NodeCategory.IDENTIFIER
    if any(x in lowered for x in ("literal", "number", "string", "char", "integer", "float", "boolean")): return NodeCategory.LITERAL
    return NodeCategory.UNKNOWN

def _flatten(root, language: str, source: bytes) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
    nodes: List[Dict[str, Any]] = []
    counts = {"error": 0, "missing": 0}
    def visit(node, parent_id: Optional[int]) -> int:
        node_id = len(nodes)
        is_error = bool(node.is_error) or node.type == "ERROR"
        is_missing = bool(node.is_missing)
        if is_error: counts["error"] += 1
        if is_missing: counts["missing"] += 1
        record = {
            "id": node_id, "parent": parent_id, "children": [], "type": node.type,
            "grammar": getattr(node, "grammar_name", node.type),
            "category": _categorize(language, node.type, node.is_named, is_error, is_missing).value,
            "canonical_kind": CANONICAL_KIND.get(language, {}).get(node.type),
            "named": bool(node.is_named), "start_byte": node.start_byte, "end_byte": node.end_byte,
            "start_point": [node.start_point[0], node.start_point[1]], "end_point": [node.end_point[0], node.end_point[1]],
            "is_error": is_error, "is_missing": is_missing,
        }
        if is_error or is_missing:
            record["canonical_kind"] = "missing_placeholder" if is_missing else "error_placeholder"
        nodes.append(record)
        for child in node.children:
            child_id = visit(child, node_id)
            record["children"].append(child_id)
        if not node.children:
            record["text"] = source[node.start_byte:node.end_byte].decode("utf-8", "replace")
        return node_id
    visit(root, None)
    return nodes, counts

def semantic_hash_from_nodes(nodes: List[Dict[str, Any]]) -> str:
    tokens = [n.get("canonical_kind") or n["type"] for n in nodes if n["category"] not in ("COMMENT", "PUNCTUATION") and n["named"]]
    return hashlib.sha256("\n".join(tokens).encode("utf-8")).hexdigest()

def _node_name(node_id: int, nodes: List[Dict[str, Any]], source_text: str) -> Optional[str]:
    queue = list(nodes[node_id]["children"])
    while queue:
        child = nodes[queue.pop(0)]
        if child["type"] in ("identifier", "type_identifier", "name", "field_identifier"):
            return child.get("text") or source_text[child["start_byte"]:child["end_byte"]]
        queue.extend(child["children"])
    return None

def extract_symbols(uast: Dict[str, Any], source: str = "") -> Dict[str, List[str]]:
    nodes = uast["nodes"]
    funcs, types = [], []
    for n in nodes:
        if n.get("canonical_kind") == "function_declaration":
            nm = _node_name(n["id"], nodes, source)
            if nm: funcs.append(nm)
        elif n.get("canonical_kind") == "type_declaration":
            nm = _node_name(n["id"], nodes, source)
            if nm: types.append(nm)
    return {"functions": sorted(set(funcs)), "types": sorted(set(types))}

def _empty_uast(language: str, source: bytes, file_path: Optional[str], flags: Dict[str, Any]) -> Dict[str, Any]:
    return {"metadata": {"language": language, "file_path": file_path, "file_hash": hashlib.sha256(source).hexdigest(), "source_bytes": len(source), "byte_span": [0, len(source)], "node_count": 0, "parser_flags": flags}, "root": None, "nodes": [], "semantic_hash": hashlib.sha256(b"").hexdigest()}

def parse_bytes(source: bytes, language: str, *, file_path: Optional[str] = None) -> Dict[str, Any]:
    base_flags = {"fallback": False, "fallback_reason": None, "has_error": False, "error_nodes": 0, "missing_nodes": 0, "error_locations": [], "truncated": False, "parse_seconds": 0.0}
    if len(source) > MAX_FILE_BYTES:
        return _empty_uast(language, source, file_path, dict(base_flags, fallback=True, fallback_reason="file_too_large", truncated=True))

    univ_parser = get_universal_parser(language)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try: univ_parser._raw_parser.timeout_micros = int(PARSE_TIMEOUT_SECONDS * 1_000_000)
        except Exception: pass

    start = time.monotonic()
    try: tree = univ_parser._raw_parser.parse(source)
    except Exception as exc:
        return _empty_uast(language, source, file_path, dict(base_flags, fallback=True, fallback_reason=f"parse_exception:{exc}"))
    elapsed = time.monotonic() - start

    if tree is None or elapsed > PARSE_TIMEOUT_SECONDS:
        return _empty_uast(language, source, file_path, dict(base_flags, fallback=True, fallback_reason="parse_timeout", truncated=True, parse_seconds=round(elapsed, 4)))

    nodes, counts = _flatten(tree.root_node, language, source)
    err_locs = [{"node_id": n["id"], "kind": "missing" if n["is_missing"] else "error", "start_byte": n["start_byte"], "end_byte": n["end_byte"], "start_point": n["start_point"]} for n in nodes if n["is_error"] or n["is_missing"]]

    flags = dict(base_flags, has_error=bool(tree.root_node.has_error), error_nodes=counts["error"], missing_nodes=counts["missing"], error_locations=err_locs, parse_seconds=round(elapsed, 4))
    uast = {"metadata": {"language": language, "file_path": file_path, "file_hash": hashlib.sha256(source).hexdigest(), "source_bytes": len(source), "byte_span": [tree.root_node.start_byte, tree.root_node.end_node.end_byte if hasattr(tree.root_node, 'end_node') else tree.root_node.end_byte], "node_count": len(nodes), "parser_flags": flags}, "root": 0 if nodes else None, "nodes": nodes}
    uast["semantic_hash"] = semantic_hash_from_nodes(nodes)
    return uast

def parse_source(source: str, language: str, *, file_path: Optional[str] = None) -> Dict[str, Any]:
    return parse_bytes(source.encode("utf-8"), language, file_path=file_path)

def parse_file(path: Union[str, Path], language: Optional[str] = None) -> Dict[str, Any]:
    file_path = Path(path)
    resolved = language or detect_language(file_path)
    if resolved is None: raise UniversalParseError(f"Unsupported extension: {file_path.suffix}")
    return parse_bytes(file_path.read_bytes(), resolved, file_path=str(file_path))

def semantic_hash(source: str, language: str) -> str:
    return parse_source(source, language)["semantic_hash"]


# ---------------------------------------------------------------------------
# Autonomous Self-Healing AST Parsing Layer
# ---------------------------------------------------------------------------
# A standalone, schema-erasure engine that resolves PyCapsule/ctypes struct
# offset drift between tree-sitter ABI 14 (0.21.x) and ABI 15 (0.22+/0.25.x),
# and falls back to zero-dependency parsers (stdlib ``ast`` for Python; a regex
# block-scope token flattener for everything else) when native parsing trips.
#
# This is an ADDITIONAL backend. The top-level UAST endpoints above
# (parse_bytes/parse_source/parse_file) intentionally keep their existing UAST
# schema and are NOT routed through this engine, so every downstream consumer
# (extract_symbols, semantic_hash, the registry ingest, the semantic mapper,
# the structural merger, etc.) keeps working unchanged. Use
# ``get_self_healing_parser()`` to obtain the recovery engine explicitly.

_engine_logger = logging.getLogger("AeroNova.Parser.SelfHealing")
if not _engine_logger.handlers:
    _engine_logger.addHandler(logging.NullHandler())

HAS_TREE_SITTER = False
try:
    import tree_sitter as _ts_runtime
    from tree_sitter import Parser as _TSParser, Language as _TSLanguageCls
    HAS_TREE_SITTER = True
except ImportError:
    _TSParser = None
    _TSLanguageCls = None
    _engine_logger.warning("Native tree-sitter bindings not detected in current runtime environment.")


class SelfHealingParser:
    """
    An autonomous parser wrapper that validates language struct layouts,
    extracts FFI pointers safely, and provides robust fallback parsers for
    continuous operation during binary/ABI conflicts.
    """

    def __init__(self, languages: Optional[List[str]] = None):
        # Default to the languages this project actually ships grammars for,
        # so bootstrap does not emit spurious "broken grammar" telemetry.
        self.languages = languages or list(GRAMMAR_MODULES.keys())
        self.language_cache: Dict[str, Any] = {}
        self.broken_languages: set = set()
        self.active_parser: Optional[Any] = None
        self._bootstrap_parsers()

    def _bootstrap_parsers(self) -> None:
        """Bootstraps available native grammars and validates their binary structures."""
        if not HAS_TREE_SITTER:
            return
        for lang in self.languages:
            try:
                lang_obj = self._load_language_safely(lang)
                if lang_obj and self._verify_language_behavioral(lang, lang_obj):
                    self.language_cache[lang] = lang_obj
                    _engine_logger.info("Successfully loaded and verified grammar for '%s'", lang)
                else:
                    self.broken_languages.add(lang)
                    _engine_logger.error("Validation failed for native grammar '%s'. Flagged for fallback routing.", lang)
            except Exception as e:
                self.broken_languages.add(lang)
                _engine_logger.error("Error bootstrapping native grammar '%s': %s. Enforcing fallback routing.", lang, e)

    def _load_language_safely(self, lang_name: str) -> Optional[Any]:
        """
        Dynamically extracts and constructs the Language object, handling
        differences between raw pointer and PyCapsule interfaces across versions.
        Delegates to the era-agnostic loader matrix where possible, then falls
        back to direct shared-library pointer wrapping.
        """
        try:
            return load_language(lang_name)
        except Exception as e:
            _engine_logger.debug("Era-agnostic loader failed for '%s': %s. Attempting dynamic extraction.", lang_name, e)

        lib_name = f"tree_sitter_{lang_name}"
        search_paths = [os.getcwd(), "/usr/local/lib", "/usr/lib"]
        if "VIRTUAL_ENV" in os.environ:
            search_paths.append(os.path.join(os.environ["VIRTUAL_ENV"], "lib"))

        shared_lib_path = None
        for path in search_paths:
            if not os.path.isdir(path):
                continue
            for root, _, files in os.walk(path):
                for file in files:
                    if lib_name in file and (file.endswith(".so") or file.endswith(".dll") or file.endswith(".dylib")):
                        shared_lib_path = os.path.join(root, file)
                        break
                if shared_lib_path:
                    break
            if shared_lib_path:
                break

        if not shared_lib_path:
            return None

        try:
            lib = ctypes.CDLL(shared_lib_path)
            lang_func = getattr(lib, f"tree_sitter_{lang_name}")
            lang_func.restype = ctypes.c_void_p
            raw_pointer = lang_func()
            if not raw_pointer:
                return None
            # Re-box through the canonical capsule matrix, then fall back to raw int.
            instance = instantiate_era_compatible_language(int(raw_pointer), lang_name)
            if instance is not None:
                return instance
            try:
                return _TSLanguageCls(raw_pointer)
            except Exception:
                return None
        except Exception as e:
            _engine_logger.error("Dynamic shared library pointer wrapping failed for '%s': %s", lang_name, e)
            return None

    def _verify_language_behavioral(self, lang_name: str, language_obj: Any) -> bool:
        """Execute a real, syntactically complex parse to isolate offset drift."""
        try:
            parser = _build_parser_from_language(language_obj)
        except Exception as e:
            _engine_logger.error("Parser initialization rejected grammar for '%s': %s", lang_name, e)
            return False

        test_inputs = {
            "python": b"def _validate_run():\n    results = [True, 'test_val']\n    return results\n",
            "rust": b"fn _validate_run() -> i32 {\n    let val = 42;\n    return val;\n}\n",
            "javascript": b"function _validate_run() {\n    const val = 100;\n    return val;\n}\n",
            "json": b"{\n    \"valid\": true,\n    \"nodes\": [1, 2, 3]\n}\n",
            "sql": b"SELECT id, name FROM users\nWHERE status = 'active'\nORDER BY id DESC;\n",
        }
        test_bytes = test_inputs.get(lang_name, b"// Dynamic structure sanity array verification test\n")
        try:
            tree = parser.parse(test_bytes)
            if not tree or not tree.root_node:
                return False
            if tree.root_node.child_count == 0 and len(test_bytes) > 10:
                _engine_logger.warning("Empty parse tree during verification for '%s'. Offsets may be corrupt.", lang_name)
                return False
            return True
        except Exception as parse_err:
            _engine_logger.error("Structural alignment verification failed for '%s': %s", lang_name, parse_err)
            return False

    def parse(self, source: Union[str, bytes], language: str) -> Dict[str, Any]:
        source_bytes = source if isinstance(source, bytes) else source.encode("utf-8")
        source_str = source.decode("utf-8") if isinstance(source, bytes) else source

        if HAS_TREE_SITTER and language in self.language_cache and language not in self.broken_languages:
            try:
                parser = _build_parser_from_language(self.language_cache[language])
                tree = parser.parse(source_bytes)
                if tree and tree.root_node:
                    return self._serialize_tree_sitter_node(tree.root_node, source_bytes)
            except Exception as e:
                _engine_logger.error("Intercepted core exception '%s' during parsing of %s. Activating fallback parser.", e, language)
                self.broken_languages.add(language)

        return self._execute_fallback_parse(source_str, language)

    def _serialize_tree_sitter_node(self, node: Any, source_bytes: bytes) -> Dict[str, Any]:
        text_segment = source_bytes[node.start_byte:node.end_byte]
        children_list = []
        for i in range(node.child_count):
            child = node.child(i)
            if child:
                children_list.append(self._serialize_tree_sitter_node(child, source_bytes))
        return {
            "type": str(node.type),
            "text": text_segment.decode("utf-8", errors="replace"),
            "start_byte": int(node.start_byte),
            "end_byte": int(node.end_byte),
            "start_point": (int(node.start_point[0]), int(node.start_point[1])),
            "end_point": (int(node.end_point[0]), int(node.end_point[1])),
            "children": children_list,
        }

    def _execute_fallback_parse(self, source: str, language: str) -> Dict[str, Any]:
        if language == "python":
            try:
                return self._parse_with_python_ast(source)
            except Exception as e:
                _engine_logger.error("Python stdlib fallback failed: %s. Defaulting to lexical token flattener.", e)
                return self._parse_with_lexical_flattener(source, "python")
        return self._parse_with_lexical_flattener(source, language)

    def _parse_with_python_ast(self, source: str) -> Dict[str, Any]:
        parsed_tree = ast.parse(source)
        source_lines = source.splitlines()

        def get_byte_index(line_0_indexed: int, col: int) -> int:
            if line_0_indexed < 0 or line_0_indexed >= len(source_lines):
                return 0
            accumulated = sum(len(line) + 1 for line in source_lines[:line_0_indexed])
            return accumulated + col

        def walk_ast_node(node: ast.AST) -> Dict[str, Any]:
            node_type = type(node).__name__
            start_line = getattr(node, "lineno", 1) - 1
            start_col = getattr(node, "col_offset", 0)
            end_line = getattr(node, "end_lineno", getattr(node, "lineno", 1)) - 1
            end_col = getattr(node, "end_col_offset", getattr(node, "col_offset", 0))

            start_byte = get_byte_index(start_line, start_col)
            end_byte = get_byte_index(end_line, end_col)

            node_text = ""
            try:
                if start_line == end_line:
                    if start_line < len(source_lines):
                        node_text = source_lines[start_line][start_col:end_col]
                else:
                    segments = []
                    if start_line < len(source_lines):
                        segments.append(source_lines[start_line][start_col:])
                    for idx in range(start_line + 1, end_line):
                        if idx < len(source_lines):
                            segments.append(source_lines[idx])
                    if end_line < len(source_lines):
                        segments.append(source_lines[end_line][:end_col])
                    node_text = "\n".join(segments)
            except Exception:
                pass

            children_list = []
            for _field, value in ast.iter_fields(node):
                if isinstance(value, list):
                    for child_item in value:
                        if isinstance(child_item, ast.AST):
                            children_list.append(walk_ast_node(child_item))
                elif isinstance(value, ast.AST):
                    children_list.append(walk_ast_node(value))

            return {
                "type": f"ast_{node_type}",
                "text": node_text,
                "start_byte": start_byte,
                "end_byte": max(start_byte, end_byte),
                "start_point": (max(0, start_line), max(0, start_col)),
                "end_point": (max(0, end_line), max(0, end_col)),
                "children": children_list,
            }

        return {
            "type": "module",
            "text": source,
            "start_byte": 0,
            "end_byte": len(source.encode("utf-8")),
            "start_point": (0, 0),
            "end_point": (max(0, len(source_lines) - 1), max(0, len(source_lines[-1]) if source_lines else 0)),
            "children": [walk_ast_node(parsed_tree)],
        }

    def _parse_with_lexical_flattener(self, source: str, language: str) -> Dict[str, Any]:
        source_lines = source.splitlines()
        source_bytes = source.encode("utf-8")
        total_len = len(source_bytes)

        root: Dict[str, Any] = {
            "type": "source_file" if language != "python" else "module",
            "text": source, "start_byte": 0, "end_byte": total_len,
            "start_point": (0, 0),
            "end_point": (max(0, len(source_lines) - 1), max(0, len(source_lines[-1]) if source_lines else 0)),
            "children": [],
        }

        comment_rx = re.compile(r"(\/\/.*|\/\*[\s\S]*?\*\/|#.*)")
        string_rx = re.compile(r"(\"[^\"]*\"|'[^']*')")
        word_rx = re.compile(r"([a-zA-Z_][a-zA-Z0-9_]*)")
        brace_rx = re.compile(r"([{}()\[\];])")
        combined_rx = re.compile(f"{comment_rx.pattern}|{string_rx.pattern}|{word_rx.pattern}|{brace_rx.pattern}")

        current_char_offset = 0
        active_block_stack: List[Dict[str, Any]] = [root]

        for line_num, line_str in enumerate(source_lines):
            line_bytes = line_str.encode("utf-8")
            line_start_byte = current_char_offset

            for match in combined_rx.finditer(line_str):
                token_text = match.group(0)
                match_start = match.start()
                match_end = match.end()

                token_start_byte = line_start_byte + len(line_str[:match_start].encode("utf-8"))
                token_end_byte = line_start_byte + len(line_str[:match_end].encode("utf-8"))

                node_type = "token"
                if token_text in ["{", "(", "["]:
                    node_type = "block_start"
                elif token_text in ["}", ")", "]"]:
                    node_type = "block_end"
                elif token_text == ";":
                    node_type = "delimiter"
                elif token_text.startswith(("//", "/*", "#")):
                    node_type = "comment"
                elif token_text.startswith(("\"", "'")):
                    node_type = "string"
                else:
                    if token_text in ["fn", "def", "function", "class", "struct", "impl", "let", "const", "var"]:
                        node_type = "keyword"
                    else:
                        node_type = "identifier"

                node: Dict[str, Any] = {
                    "type": node_type, "text": token_text, "start_byte": token_start_byte, "end_byte": token_end_byte,
                    "start_point": (line_num, match_start), "end_point": (line_num, match_end), "children": [],
                }

                if node_type == "block_start":
                    container_node = {
                        "type": "lexical_block", "text": token_text, "start_byte": token_start_byte, "end_byte": token_end_byte,
                        "start_point": (line_num, match_start), "end_point": (line_num, match_end), "children": [node],
                    }
                    active_block_stack[-1]["children"].append(container_node)
                    active_block_stack.append(container_node)
                elif node_type == "block_end":
                    active_block_stack[-1]["children"].append(node)
                    if len(active_block_stack) > 1:
                        closed_block = active_block_stack.pop()
                        closed_block["end_byte"] = token_end_byte
                        closed_block["end_point"] = (line_num, match_end)
                        try:
                            closed_block["text"] = source_bytes[closed_block["start_byte"]:token_end_byte].decode("utf-8")
                        except Exception:
                            pass
                else:
                    active_block_stack[-1]["children"].append(node)

            current_char_offset += len(line_bytes) + 1

        while len(active_block_stack) > 1:
            unfinished = active_block_stack.pop()
            unfinished["end_byte"] = total_len
            unfinished["end_point"] = root["end_point"]
            try:
                unfinished["text"] = source_bytes[unfinished["start_byte"]:total_len].decode("utf-8")
            except Exception:
                pass

        return root


def _build_parser_from_language(language_obj: Any) -> Any:
    """Construct a tree-sitter Parser bound to *language_obj* across binding eras."""
    parser = _TSParser()
    try:
        if hasattr(parser, "set_language"):
            parser.set_language(language_obj)
        else:
            parser.language = language_obj
        return parser
    except (TypeError, AttributeError):
        # Newer bindings only accept the language via constructor.
        return _TSParser(language_obj)


_SELF_HEALING_ENGINE: Optional["SelfHealingParser"] = None


def get_self_healing_parser(languages: Optional[List[str]] = None) -> "SelfHealingParser":
    """Return a lazily-constructed, process-wide self-healing recovery engine."""
    global _SELF_HEALING_ENGINE
    if languages is not None:
        return SelfHealingParser(languages)
    if _SELF_HEALING_ENGINE is None:
        _SELF_HEALING_ENGINE = SelfHealingParser()
    return _SELF_HEALING_ENGINE
