import ast
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.resolve()

seen = set()
deps = set()

def resolve_module(module: str):
    if not module:
        return None

    path = PROJECT_ROOT / module.replace(".", "/")

    if path.with_suffix(".py").exists():
        return path.with_suffix(".py")

    if path.is_dir() and (path / "__init__.py").exists():
        return path / "__init__.py"

    return None


def scan_file(file: Path):
    file = file.resolve()
    if file in seen:
        return

    seen.add(file)
    deps.add(file)

    try:
        tree = ast.parse(file.read_text())
    except Exception:
        return

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for name in node.names:
                mod = resolve_module(name.name)
                if mod:
                    scan_file(mod)

        elif isinstance(node, ast.ImportFrom):
            modname = node.module
            if node.level > 0:
                base = file.parent
                for _ in range(node.level - 1):
                    base = base.parent
                if modname:
                    modname = f"{base.name}.{modname}"
                else:
                    modname = base.name

            mod = resolve_module(modname)
            if mod:
                scan_file(mod)


if __name__ == "__main__":
    entry = PROJECT_ROOT / "main.py"   # change if needed
    scan_file(entry)

    # Only consider dependencies in the main directory
    main_deps = {f for f in deps if f.parent == PROJECT_ROOT}
    for d in main_deps:
        print(d)
    exit()

    # All .py files in the main directory
    main_py_files = set(PROJECT_ROOT.glob("*.py"))

    # Files to delete: those in main dir but not used
    to_delete = main_py_files - main_deps

    print("Deleting the following unused .py files in the main directory:")
    for f in to_delete:
        print(f"  {f.name}")
        # f.unlink()

    print("\nRemaining dependencies:")
    print("\n".join(sorted(str(p.relative_to(PROJECT_ROOT)) for p in deps)))
