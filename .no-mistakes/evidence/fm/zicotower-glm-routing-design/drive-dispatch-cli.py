import http.server, json, os, pathlib, subprocess, threading
root=pathlib.Path.cwd()
work=root/'.tmp-dispatch-validation'
home=work/'home'
(home/'data'/'Fix.1').mkdir(parents=True)
(home/'escape').mkdir()
log=[]
requests=[]
mode='ready'
class Endpoint(http.server.BaseHTTPRequestHandler):
 def do_GET(self):
  requests.append(self.path)
  if mode=='redirect':
   self.send_response(302); self.send_header('Location','https://example.com/health'); self.end_headers(); return
  body={'status':'loading' if mode=='loading' else 'ok'} if self.path=='/health' else {'data':[{'id':'demo-model','context_length':16384,'revision':'fixture-revision'}]}
  self.reply(body)
 def do_POST(self):
  data=json.loads(self.rfile.read(int(self.headers['Content-Length'])))
  requests.append({'path':self.path,'model':data['model'],'tool_choice':data['tool_choice']})
  self.reply({'choices':[{'finish_reason':'tool_calls','message':{'tool_calls':[{'function':{'name':'probe','arguments':json.dumps({'value':'wrong' if mode=='bad-tool' else 'ready'})}}]}}]})
 def reply(self,body):
  data=json.dumps(body).encode(); self.send_response(200); self.send_header('Content-Length',str(len(data))); self.end_headers(); self.wfile.write(data)
 def log_message(self,*args): pass
server=http.server.HTTPServer(('127.0.0.1',0),Endpoint)
thread=threading.Thread(target=server.serve_forever,daemon=True); thread.start()
base=f'http://127.0.0.1:{server.server_port}/v1'
catalog=work/'models.json'
def config(url=base,context=16384):
 catalog.write_text(json.dumps({'providers':{'demo':{'baseUrl':url,'api':'openai-completions','models':[{'id':'demo-model','contextWindow':context,'maxTokens':2048}]}}}))
def run(label,args,row=None,ok=True):
 p=subprocess.run(['bin/fm-dispatch-evidence.sh',*args],input=None if row is None else json.dumps(row),text=True,capture_output=True,env={**os.environ,'FM_HOME':str(home)})
 log.append(f'CASE: {label}\n$ FM_HOME=<disposable-home> bin/fm-dispatch-evidence.sh '+ ' '.join(args)+f'\nexit={p.returncode}\nstdout: {p.stdout}stderr: {p.stderr}')
 assert (p.returncode==0)==ok,(label,p.stdout,p.stderr)
 return p
shadow={'task_class':'bounded coding','proposed':'demo/demo-model','selected':'codex/gpt','confidence':0.9}
outcome={'run_id':'manual-1','task_class':'bounded coding','provider':'demo','model':'demo-model','accepted':True,'elapsed_seconds':12,'interventions':0,'rework_minutes':0,'cloud_egress':False}
try:
 run('uppercase-and-dot shadow record',['record','Fix.1','shadow'],shadow)
 run('uppercase-and-dot outcome record',['record','Fix.1','outcome'],outcome)
 target=home/'data'/'Fix.1'/'dispatch-evidence.jsonl'
 before=target.read_bytes()
 events=[json.loads(x) for x in before.splitlines()]
 assert [x['kind'] for x in events]==['shadow','outcome'] and all(x['task']=='Fix.1' for x in events)
 assert target.stat().st_mode & 0o777==0o600
 log.append('Persisted private evidence (mode 0600):\n'+before.decode())
 run('path traversal rejected',['record','../escape','shadow'],shadow,False)
 assert not (home/'escape'/'dispatch-evidence.jsonl').exists()
 for label,row in [('prompt rejected',{**shadow,'prompt':'do not store'}),('nested value rejected',{**shadow,'basis':{}}),('invalid duration rejected',{**outcome,'elapsed_seconds':-1}),('nonfinite rejected',{**outcome,'elapsed_seconds':float('nan')}),('overlong field rejected',{**shadow,'reason':'x'*501})]:
  run(label,['record','Fix.1','outcome' if 'run_id' in row else 'shadow'],row,False)
 assert target.read_bytes()==before
 (home/'data'/'Linked').symlink_to(home/'data'/'Fix.1',target_is_directory=True)
 run('symlink task directory rejected',['record','Linked','shadow'],shadow,False)
 (home/'data'/'Target').mkdir()
 (home/'data'/'Target'/'dispatch-evidence.jsonl').symlink_to(target)
 run('symlink evidence file rejected',['record','Target','shadow'],shadow,False)
 assert target.read_bytes()==before
 config()
 args=['check-local','demo/demo-model','--catalog',str(catalog),'--expected-url',base]
 p=run('healthy exact tuple and forced tool call',args)
 assert json.loads(p.stdout)['tool_canary']=='passed'
 for setting in ['loading','redirect','bad-tool']:
  mode=setting; run(setting+' endpoint rejected',args,ok=False)
 mode='ready'
 config(context=32768); run('insufficient serving context rejected',args,ok=False)
 config(); run('model alias mismatch rejected',[*args[:1],'demo/other',*args[2:]],ok=False)
 run('expected endpoint mismatch rejected',args[:-1]+['http://127.0.0.1:9/v1'],ok=False)
 run('missing independent expected endpoint rejected',args[:-2],ok=False)
 n=len(requests)
 config('http://8.8.8.8:8000/v1'); run('public endpoint rejected before network access',args[:-1]+['http://8.8.8.8:8000/v1'],ok=False)
 assert len(requests)==n
 config('http://127.0.0.1:9/v1'); run('unavailable endpoint rejected',args[:-1]+['http://127.0.0.1:9/v1'],ok=False)
 log.append('Disposable endpoint received requests:\n'+json.dumps(requests,indent=2))
 log.append('All direct CLI assertions passed; endpoint is a disposable protocol dependency, not a real model or hardware performance trial.')
finally:
 server.shutdown();server.server_close()
 evidence=pathlib.Path('/Users/zicofernandes/.no-mistakes/evidence/01M515NNRHF0B7TR5Y8KZ285CZ/dispatch-cli-transcript.txt')
 evidence.write_text('\n\n'.join(log)+'\n')
print('Direct CLI scenarios passed; transcript: '+str(evidence))
