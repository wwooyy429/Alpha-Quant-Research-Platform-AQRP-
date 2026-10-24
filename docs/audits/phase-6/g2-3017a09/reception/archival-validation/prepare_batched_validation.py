from pathlib import Path
O=Path(__file__).resolve().parent
code=(O/'validate_archive.py').read_text(encoding='utf-8')
code=code.replace('import hashlib,json,subprocess','import hashlib,json,subprocess,io,zipfile')
old="""for n in originals:
 raw=git('show',C+':'+n)
 if (R/n).read_bytes()!=raw:assert n in allowed,n;changed.append(n)
 else:unchanged+=1
"""
new="""with zipfile.ZipFile(io.BytesIO(git('archive','--format=zip',C))) as z:
 assert {n for n in z.namelist() if not n.endswith('/')}==set(originals)
 for n in originals:
  raw=z.read(n)
  if (R/n).read_bytes()!=raw:assert n in allowed,n;changed.append(n)
  else:unchanged+=1
"""
assert old in code;code=code.replace(old,new)
old="new=[x for x in git('ls-files','--others','--exclude-standard','-z').decode('utf-8').strip('\\x00').split('\\x00') if x]"
new="new=sorted(set(x for x in git('ls-files','--cached','--others','--exclude-standard','-z').decode('utf-8').strip('\\x00').split('\\x00') if x)-set(originals))"
assert old in code;code=code.replace(old,new)
compile(code,'validate_archive_batched.py','exec')
(O/'validate_archive_batched.py').write_text(code,encoding='utf-8',newline='\n')
print('Batched fixed Git archive reader; unchanged byte equality/identity/permission assertions')
