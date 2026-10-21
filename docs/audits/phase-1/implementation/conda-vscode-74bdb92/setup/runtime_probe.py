import sys,sysconfig,platform,importlib.metadata as m,json,hashlib,ssl,os
from pathlib import Path
r={"python":sys.version,"version":list(sys.version_info[:3]),"executable":sys.executable,"implementation":platform.python_implementation(),"machine":platform.machine(),"is_64_bit":sys.maxsize>2**32,"gil_disabled":bool(sysconfig.get_config_var("Py_GIL_DISABLED")),"prefix":sys.prefix,"base_prefix":sys.base_prefix,"conda_prefix":os.environ.get("CONDA_PREFIX"),"openssl":ssl.OPENSSL_VERSION,"executable_sha256":hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest(),"packages":sorted([{"name":d.metadata["Name"],"version":d.version} for d in m.distributions()],key=lambda x:x["name"].lower())}
try:
 import aqrp
 r["aqrp_import_path"]=aqrp.__file__
except ImportError:
 r["aqrp_import_path"]=None
print(json.dumps(r,indent=2))

