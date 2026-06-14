import ast
from pathlib import Path
from typing import Optional


ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = ROOT / "src" / "mentor_lab"
MAX_MODULE_SLOC = 400
MAX_AVG_CLUSTERING = 0.180


def _source_modules() -> list[Path]:
    return sorted(
        path
        for path in SRC_ROOT.rglob("*.py")
        if "__pycache__" not in path.parts
    )


def _module_name(path: Path) -> str:
    relative = path.relative_to(ROOT / "src").with_suffix("")
    return ".".join(relative.parts)


MODULE_NAMES = {_module_name(path) for path in _source_modules()}


def _sloc(path: Path) -> int:
    return sum(
        1
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    )


def _import_graph() -> dict[str, set[str]]:
    modules = MODULE_NAMES
    graph = {module: set() for module in modules}

    for path in _source_modules():
        source = _module_name(path)
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                imported = _resolve_import_from(source, node)
                if imported in modules:
                    graph[source].add(imported)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    imported = _nearest_internal_module(alias.name, modules)
                    if imported:
                        graph[source].add(imported)

    return graph


def _resolve_import_from(source: str, node: ast.ImportFrom) -> Optional[str]:
    module = node.module or ""
    if node.level:
        package = source.split(".")[:-node.level]
        module = ".".join([*package, module]).rstrip(".")
    return _nearest_internal_module(module, MODULE_NAMES)


def _nearest_internal_module(module: str, modules: set[str]) -> Optional[str]:
    if module in modules:
        return module
    parts = module.split(".")
    while len(parts) > 1:
        parts.pop()
        candidate = ".".join(parts)
        if candidate in modules:
            return candidate
    return None


def _average_clustering(graph: dict[str, set[str]]) -> float:
    coefficients = []
    for node, neighbors in graph.items():
        if len(neighbors) < 2:
            coefficients.append(0.0)
            continue
        links = 0
        neighbor_list = sorted(neighbors)
        for left_index, left in enumerate(neighbor_list):
            for right in neighbor_list[left_index + 1 :]:
                if right in graph.get(left, set()) or left in graph.get(right, set()):
                    links += 1
        possible = len(neighbor_list) * (len(neighbor_list) - 1) / 2
        coefficients.append(links / possible)

    if not coefficients:
        return 0.0
    return sum(coefficients) / len(coefficients)


def test_python_modules_stay_under_400_sloc():
    offenders = [
        f"{path.relative_to(ROOT).as_posix()}: {_sloc(path)} SLOC"
        for path in _source_modules()
        if _sloc(path) > MAX_MODULE_SLOC
    ]

    assert offenders == []


def test_internal_dependency_graph_stays_decoupled():
    clustering = _average_clustering(_import_graph())

    assert clustering <= MAX_AVG_CLUSTERING
