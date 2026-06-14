import os
import shutil
import re

def main():
    base_dir = r"c:\Users\yeswa\Desktop\LifeGraphBackend"
    src_dir = os.path.join(base_dir, "src")
    
    # New directories
    new_dirs = [
        "foundation",
        "foundation/domains",
        "engines",
        "engines/domains",
        "orchestration",
        "orchestration/agents",
        "ingestion",
        "api",
        "analytics"
    ]
    
    for d in new_dirs:
        os.makedirs(os.path.join(src_dir, d), exist_ok=True)
        init_file = os.path.join(src_dir, d, "__init__.py")
        if not os.path.exists(init_file):
            with open(init_file, "w") as f:
                pass
            
    os.makedirs(os.path.join(base_dir, "tests_legacy"), exist_ok=True)
    os.makedirs(os.path.join(base_dir, "tests_v2"), exist_ok=True)

    # Moves
    moves = [
        # orchestration
        ("src/agents/orchestrator", "src/orchestration/agents/orchestrator"),
        ("src/workflows", "src/orchestration/workflows"),
        
        # engines
        ("src/agents", "src/engines/agents"),
        ("src/domains/adaptive", "src/engines/domains/adaptive"),
        ("src/domains/simulator", "src/engines/domains/simulator"),
        ("src/domains/prevention", "src/engines/domains/prevention"),
        ("src/domains/verification", "src/engines/domains/verification"),
        ("src/domains/risk", "src/engines/domains/risk"),
        ("src/domains/mission_detection", "src/engines/domains/mission_detection"),
        
        # foundation
        ("src/core", "src/foundation/core"),
        ("src/infrastructure", "src/foundation/infrastructure"),
        ("src/shared", "src/foundation/shared"),
        ("src/graph", "src/foundation/graph"),
        ("src/domains/products", "src/foundation/domains/products"),
        ("src/domains/missions", "src/foundation/domains/missions"),
        ("src/domains/users", "src/foundation/domains/users"),
        ("src/domains/carts", "src/foundation/domains/carts"),
        ("src/domains/memory", "src/foundation/domains/memory"),
        ("src/domains/relationships", "src/foundation/domains/relationships"),
        ("src/domains/graph", "src/foundation/domains/graph"),
        
        # ingestion
        ("src/data_ingestion", "src/ingestion"),
        
        # tests
        ("tests", "tests_legacy")
    ]
    
    for src, dst in moves:
        src_path = os.path.join(base_dir, src)
        dst_path = os.path.join(base_dir, dst)
        if os.path.exists(src_path):
            shutil.move(src_path, dst_path)

    # Now fix imports in all python files
    # We will replace these prefixes with the new ones
    import_replacements = {
        r"\bagents\.orchestrator\b": "orchestration.agents.orchestrator",
        r"\bagents\b": "engines.agents",
        r"\bworkflows\b": "orchestration.workflows",
        r"\bdomains\.adaptive\b": "engines.domains.adaptive",
        r"\bdomains\.simulator\b": "engines.domains.simulator",
        r"\bdomains\.prevention\b": "engines.domains.prevention",
        r"\bdomains\.verification\b": "engines.domains.verification",
        r"\bdomains\.risk\b": "engines.domains.risk",
        r"\bdomains\.mission_detection\b": "engines.domains.mission_detection",
        r"\bcore\b": "foundation.core",
        r"\binfrastructure\b": "foundation.infrastructure",
        r"\bshared\b": "foundation.shared",
        r"\bgraph\b": "foundation.graph", # this might catch some false positives but hopefully fine inside 'from graph' or 'import graph'
        r"\bdomains\.products\b": "foundation.domains.products",
        r"\bdomains\.missions\b": "foundation.domains.missions",
        r"\bdomains\.users\b": "foundation.domains.users",
        r"\bdomains\.carts\b": "foundation.domains.carts",
        r"\bdomains\.memory\b": "foundation.domains.memory",
        r"\bdomains\.relationships\b": "foundation.domains.relationships",
        r"\bdomains\.graph\b": "foundation.domains.graph",
        r"\bdata_ingestion\b": "ingestion"
    }
    
    # We should only replace imports, i.e., lines starting with `import ` or `from `
    # or inside strings? Just do regex for `from {old}` and `import {old}` to be safer.
    
    safe_replacements = []
    for old, new in import_replacements.items():
        # Match 'from old' or 'import old'
        # e.g. from agents.orchestrator import ...
        # old is regex string like r"\bagents\.orchestrator\b"
        
        safe_replacements.append((
            re.compile(r"^(from\s+)" + old + r"(\s+import|\.)", re.MULTILINE),
            r"\g<1>" + new + r"\g<2>"
        ))
        safe_replacements.append((
            re.compile(r"^(import\s+)" + old + r"(\s+as|\s*$|\.)", re.MULTILINE),
            r"\g<1>" + new + r"\g<2>"
        ))
        
        # also handle cases where it's part of a longer import, e.g. from x.y import z -> this is covered if it's the start.
        # What about `foundation.graph.repository` used as a string or type annotation?
        # Let's also do a general replace just for things like `graph.repository.GraphRepository`
        # if it's a known old path. But let's stick to import statements first, and run the server to see.

    for root, dirs, files in os.walk(base_dir):
        if 'node_modules' in root or '.git' in root or '__pycache__' in root:
            continue
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                new_content = content
                for pattern, repl in safe_replacements:
                    new_content = pattern.sub(repl, new_content)
                
                # Special cases: local_app.py has `import app` ? Actually app.py is in src, api is in src.
                
                if new_content != content:
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(new_content)
                    print(f"Updated {path}")

if __name__ == "__main__":
    main()
