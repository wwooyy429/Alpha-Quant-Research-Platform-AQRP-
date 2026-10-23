import subprocess,sys,pathlib,json,datetime
root=pathlib.Path(__file__).parent
label=sys.argv[1];cwd=sys.argv[2];argv=sys.argv[3:]
start=datetime.datetime.now(datetime.timezone.utc).isoformat()
with (root/(label+'.stdout.log')).open('wb') as out,(root/(label+'.stderr.log')).open('wb') as err:
 p=subprocess.run(argv,cwd=cwd,stdout=out,stderr=err)
record={'argv':argv,'cwd':cwd,'started_utc':start,'ended_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'exit_code':p.returncode,'fixed_sha':'1c5a7e62cace7c3e66b7cc7f12fd564cb0013654','actual_executor':'GPT Work supplemental reviewer'}
(root/(label+'.command.json')).write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'label':label,'exit_code':p.returncode}));sys.exit(p.returncode)
