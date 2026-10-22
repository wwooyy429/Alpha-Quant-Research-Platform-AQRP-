import pathlib,json,hashlib,shutil
O=pathlib.Path(__file__).parent;OLD=O.parent/'work-p4-g2-18439f3-independent';C=O.parent/'p4-g2-recheck-3c87579';FIX='3c8757949b0fd5c97953b06a74ebc2d0e56676e4'
sdk=next((O.parent.parent/'runs/gwp4r').iterdir());(O/'SDK_LOCATION.txt').write_text(str(sdk),encoding='utf-8')
for name in ['independent_reference.py','verify_behavior.py','verify_evidence.py','run_legacy.py']:
 text=(OLD/name).read_text(encoding='utf-8').replace('p4-g2-18439f3-review','p4-g2-recheck-3c87579').replace('18439f31536295aea42e57e566d07cce345a35cf',FIX)
 text=text.replace("next((O/'sdk').iterdir())","pathlib.Path((O/'SDK_LOCATION.txt').read_text(encoding='utf-8'))")
 text=text.replace('b79f2bd4aff65971bb2f65797cb3e47a5494f2cf','354c931ef05d8d16237efac5826ae47302175f4f').replace('len(tests)==799','len(tests)==844').replace('current installed 0.4.0','current installed 0.4.1.dev1')
 (O/name).write_text(text,encoding='utf-8')
# Original scanner script expects this layout. Store only its independently hashed executable here.
scanner=O/'sdk'/'scanner';scanner.mkdir(parents=True,exist_ok=True)
if (sdk/'gitleaks.exe').exists():shutil.copyfile(sdk/'gitleaks.exe',scanner/'gitleaks.exe')
for n in ['INDEPENDENT_EXPECTED_RESULTS.json']:
 if (OLD/n).exists():shutil.copyfile(OLD/n,O/('previous-'+n))
print(json.dumps({'sdk':str(sdk),'fixed':FIX,'adapted_scripts':4}))
