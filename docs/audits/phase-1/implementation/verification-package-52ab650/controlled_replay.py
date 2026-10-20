import ast,sys
from pathlib import Path
program,fixture=sys.argv[1:]
tree=ast.parse(Path(program).read_text(encoding="utf-8"))
assign=[n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=="out_dir" for t in n.targets)]
assert len(assign)==1 and isinstance(assign[0].value,ast.Constant)
assign[0].value=ast.Constant(fixture)
ast.fix_missing_locations(tree)
exec(compile(tree,program,"exec"),{"__name__":"__main__"})
