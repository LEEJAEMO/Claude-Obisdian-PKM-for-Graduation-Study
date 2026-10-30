"""Folder-based task workspace. Python 3.10+, standard library only."""
from __future__ import annotations
import argparse
from contextlib import contextmanager
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import tempfile
import time
import uuid

VERSION='1.0.0'
AREAS={'Plan':'P','Spec':'S','Evidence':'E','Decisions':'D','Status':'ST','Log':'L','Modules':'M','Troubleshooting':'T'}
SKIP_INPUT={'.git','.codex','.claude','.agents','.agent','Project','PKM','AGENTS.md','AGENTS.override.md','node_modules','.venv','venv','__pycache__','.pytest_cache','dist','build','agent-workflow','preflight-check'}
HEADER='현재 파일 절대경로: '
BEGIN='<!-- shared-workspace:start -->'
END='<!-- shared-workspace:end -->'

def now():return datetime.now(timezone.utc).isoformat(timespec='milliseconds')
def sha(data):return hashlib.sha256(data).hexdigest()
def atomic(path,data):
 path.parent.mkdir(parents=True,exist_ok=True)
 fd,name=tempfile.mkstemp(prefix='.pending-',dir=path.parent)
 try:
  with os.fdopen(fd,'wb') as f:f.write(data);f.flush();os.fsync(f.fileno())
  os.replace(name,path)
 finally:
  if os.path.exists(name):os.unlink(name)

def addressed(path,body):
 body=body.lstrip('\ufeff')
 if body.startswith(HEADER):body=body.split('\n',1)[1] if '\n' in body else ''
 return HEADER+str(path.resolve())+'\n\n'+body.lstrip('\n')

class Workspace:
 def __init__(self,root):
  self.root=Path(root).resolve(strict=True)
  if not self.root.is_dir() or self.root==Path(self.root.anchor):raise ValueError('choose an existing task directory, not a filesystem root')
  self.system=self.root/'PKM/System'
 def safe(self,relative):
  path=self.root/relative
  if not path.resolve().is_relative_to(self.root) or path.is_symlink():raise ValueError('path leaves task workspace')
  # Reject directory links/junctions too, including redirected parents within root.
  cur=path
  while cur!=self.root:
   if cur.exists() and (cur.is_symlink() or (hasattr(cur,'is_junction') and cur.is_junction())):raise ValueError('redirected workspace path')
   cur=cur.parent
  return path
 def manifest(self):
  p=self.safe('PKM/System/workspace.json')
  if not p.is_file():raise ValueError('install the workspace first')
  data=json.loads(p.read_text(encoding='utf-8'))
  if data.get('format')!='folder-pkm-v1':raise ValueError('unrecognized workspace format')
  return data
 @contextmanager
 def lock(self):
  self.manifest();p=self.safe('PKM/System/.writer.lock');deadline=time.perf_counter()+5
  while True:
   try:fd=os.open(p,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600);os.close(fd);break
   except FileExistsError:
    if time.perf_counter()>=deadline:raise ValueError('another writer is active; inspect it instead of removing its lock')
    time.sleep(.05)
  try:yield
  finally:p.unlink()
 def event(self,kind,summary,details=None):
  p=self.safe('PKM/System/events.jsonl');row={'id':uuid.uuid4().hex,'at_utc':now(),'kind':kind,'summary':summary,'details':details or {}}
  with p.open('ab') as f:f.write((json.dumps(row,ensure_ascii=False)+'\n').encode());f.flush();os.fsync(f.fileno())
  return row
 def markdown(self,path,body):atomic(path,addressed(path,body).encode('utf-8'))
 def install(self,source,copy_inputs=False):
  source=Path(source).resolve(strict=True)
  if not (source/'AGENTS.md').is_file() or not (source/'PKM/index.md').is_file():raise ValueError('invalid distribution root')
  manifest_path=self.safe('PKM/System/workspace.json')
  if manifest_path.exists():
   self.manifest()
   report=self.check()
   return {'installed':False,'reason':'already installed; existing content preserved','check':report}
  # Do not merge an unrelated preexisting PKM into this workspace automatically.
  pkm=self.safe('PKM')
  if pkm.exists() and any(pkm.iterdir()):raise ValueError('nonempty PKM exists; inspect before installing')
  inputs=[]
  if copy_inputs:
   if self.root==Path.home().resolve():raise ValueError('refusing to copy a home directory as task input')
   inputs=[p for p in self.root.iterdir() if p.name not in SKIP_INPUT and not p.name.startswith('.') and p.resolve()!=source and not source.is_relative_to(p.resolve()) and p.resolve().is_relative_to(self.root) and not p.is_symlink()]
  old_agents=self.safe('AGENTS.md').read_bytes() if self.safe('AGENTS.md').exists() else None
  for p in source.rglob('*'):
   rel=p.relative_to(source)
   if not p.is_file() or any(x in {'.git','__pycache__','tests'} for x in rel.parts) or rel.as_posix()=='AGENTS.md':continue
   target=self.safe(rel)
   if target.exists():continue
   data=p.read_bytes()
   if p.suffix.lower()=='.md':self.markdown(target,data.decode('utf-8').replace('{{ROOT}}',str(self.root)))
   else:atomic(target,data)
  agent_body=(source/'AGENTS.md').read_text(encoding='utf-8').split('\n',1)[1].replace('{{ROOT}}',str(self.root)).lstrip('\n')
  if old_agents is not None:
   atomic(self.safe('PKM/System/Backups/AGENTS-before-install.txt'),old_agents)
   previous=old_agents.decode('utf-8-sig')
   if previous.startswith(HEADER):previous=previous.split('\n',1)[1]
   agent_body=previous.rstrip()+'\n\n'+BEGIN+'\n'+agent_body+'\n'+END+'\n'
  self.markdown(self.safe('AGENTS.md'),agent_body)
  atomic(manifest_path,(json.dumps({'format':'folder-pkm-v1','version':VERSION,'installed_at':now(),'root_at_install':str(self.root),'copied_inputs':[]},ensure_ascii=False,indent=2)+'\n').encode())
  with self.lock():
   mappings=[]
   for p in inputs:
    target=self.safe(Path('Project')/p.name)
    if target.exists():
     mappings.append({'source':str(p),'target':str(target),'status':'target exists, not overwritten'});continue
    if p.is_dir():
     # Copy only ordinary files; no external symlink following or dependency trees.
     for q in p.rglob('*'):
      if not q.is_file() or q.is_symlink() or any(x in SKIP_INPUT or x.startswith('.') for x in q.relative_to(p).parts):continue
      if any(parent.is_symlink() for parent in q.parents if parent!=p and parent.is_relative_to(p)):continue
      dest=self.safe(target.relative_to(self.root)/q.relative_to(p));self._copy_input(q,dest)
    else:self._copy_input(p,target)
    mappings.append({'source':str(p),'target':str(target),'status':'working copy; original preserved'})
   data=self.manifest();data['copied_inputs']=mappings;atomic(manifest_path,(json.dumps(data,ensure_ascii=False,indent=2)+'\n').encode())
   self.event('installed','root AGENTS + Project + indexed PKM created',{'copied_inputs':mappings})
   for area,title,body in [('Spec','task','실제 과제의 목표·요구·가정·입출력·수용 기준을 이 문서에 짧게 작성한다. 아직 요구가 입력되지 않았다.'),('Plan','task','현재 요구와 관련 파일을 연결해 다음 작업을 정리한다. 아직 구현하지 않았다.'),('Status','current','완료: 작업 공간 설치. 미실행: 실제 과제 구현·검증. 다음: 과제를 읽고 목표를 공유한다.')]:
    self._new(area,title,body,'draft',[])
  return {'installed':True,'root':str(self.root),'instructions':str(self.root/'AGENTS.md'),'project':str(self.root/'Project'),'pkm':str(self.root/'PKM'),'copied_inputs':mappings,'check':self.check(),'next':'Explicitly read root AGENTS.md, PKM/index.md and the needed area index in the current session; continue the task in Project/.'}
 def _copy_input(self,source,target):
  raw=source.read_bytes()
  if source.suffix.lower()=='.md':self.markdown(target,raw.decode('utf-8-sig'))
  else:atomic(target,raw)
 def entries(self,area):
  if area not in AREAS:raise ValueError('unknown PKM area')
  folder=self.safe('PKM/'+area)
  return sorted(p for p in folder.glob('*.md') if p.name!='index.md')
 def read(self,relative):
  p=self.safe(relative)
  if p.suffix.lower()!='.md' or not p.is_file():raise ValueError('choose an existing Markdown file')
  raw=p.read_bytes()
  return {'path':str(p),'sha256':sha(raw),'content':raw.decode('utf-8')}
 def _index(self,area):
  p=self.safe(f'PKM/{area}/index.md');text=p.read_text(encoding='utf-8')
  if '<!-- entries:start -->' not in text or '<!-- entries:end -->' not in text:raise ValueError('area index markers missing; preserve custom guide and repair explicitly')
  rows=['| 문서 | 현재 절대경로 |','|---|---|']
  for q in self.entries(area):rows.append(f'| [{q.stem}]({q.name}) | `{q.resolve()}` |')
  replacement='<!-- entries:start -->\n'+'\n'.join(rows)+'\n<!-- entries:end -->'
  text=re.sub(r'<!-- entries:start -->.*?<!-- entries:end -->',lambda _:replacement,text,flags=re.S)
  self.markdown(p,text)
 def new(self,area,title,body,status='draft',related=None):
  with self.lock():return self._new(area,title,body,status,related or [])
 def _new(self,area,title,body,status,related):
  if area not in AREAS:raise ValueError('unknown PKM area')
  if not isinstance(title,str) or not title.strip() or len(title)>150:raise ValueError('title must have 1..150 characters')
  if not isinstance(body,str) or len(body.encode())>131072:raise ValueError('body must be text up to 128 KiB')
  if not isinstance(related,list) or not all(isinstance(x,str) for x in related):raise ValueError('related must be a list of path/ID strings')
  count=max([int(m[1]) for p in self.entries(area) if (m:=re.match(re.escape(AREAS[area])+r'(\d+)-',p.name))]+[0])+1
  slug=re.sub(r'[^\w-]+','-',title.strip(),flags=re.U).strip('-')[:60] or 'note'
  ident=f'{AREAS[area]}{count:03}';p=self.safe(f'PKM/{area}/{ident}-{slug}.md')
  content=f'# {ident} — {title}\n\n상태: {status}\n관련: '+(', '.join(related) or '아직 연결 없음')+'\n\n'+body+'\n'
  self.markdown(p,content)
  self.event('document_created',title,{'path':str(p),'id':ident,'area':area,'status':status})
  self._index(area)
  return {'id':ident,'path':str(p),'index':str(self.root/f'PKM/{area}/index.md'),'sha256':sha(p.read_bytes())}
 def update(self,relative,body,expected_sha):
  if not isinstance(body,str) or len(body.encode())>131072:raise ValueError('body too large')
  p=self.safe(relative)
  if not p.is_relative_to(self.root/'PKM') or p.suffix!='.md' or p.name=='index.md' or 'System' in p.relative_to(self.root).parts:raise ValueError('update a PKM category document; use normal host editing for code and guides')
  with self.lock():
   old=self.read(relative)
   if expected_sha!=old['sha256']:raise ValueError('document changed; reread')
   content=addressed(p,body).encode()
   if content==p.read_bytes():return {'saved':False,'path':str(p),'sha256':old['sha256']}
   backup=self.safe('PKM/System/History/'+uuid.uuid4().hex+'.txt');atomic(backup,p.read_bytes())
   self.event('save_started',str(p),{'before_sha256':old['sha256'],'intended_sha256':sha(content),'backup':str(backup)})
   atomic(p,content);self.event('document_saved',str(p),{'sha256':sha(content)})
   area=p.relative_to(self.root/'PKM').parts[0];self._index(area)
   return {'saved':True,'path':str(p),'sha256':sha(content)}
 def check(self):
  self.manifest();issues=[];count=0
  files=[self.safe('AGENTS.md')]
  for folder in ['Project','PKM']:
   files.extend(p for p in self.safe(folder).rglob('*.md') if not any(x in {'.git','node_modules','.venv','venv','__pycache__'} for x in p.relative_to(self.root).parts))
  for p in files:
   count+=1
   if p.is_symlink() or not p.resolve().is_relative_to(self.root):issues.append({'path':str(p),'issue':'redirected file'});continue
   text=p.read_text(encoding='utf-8-sig')
   if text.split('\n',1)[0]!=HEADER+str(p.resolve()):issues.append({'path':str(p),'issue':'missing or stale first-line absolute path'})
   if '{{ROOT}}' in text:issues.append({'path':str(p),'issue':'unrendered root token'})
  for area in AREAS:
   index=self.safe(f'PKM/{area}/index.md')
   if not index.is_file():issues.append({'path':str(index),'issue':'missing index'});continue
   text=index.read_text(encoding='utf-8')
   for p in self.entries(area):
    if p.name not in text:issues.append({'path':str(index),'issue':'unindexed document '+p.name})
  return {'markdown_files':count,'issues':issues,'ok':not issues,'project':str(self.root/'Project'),'pkm':str(self.root/'PKM')}
 def repair_paths(self):
  with self.lock():
   manifest=self.manifest();previous_root=manifest.get('current_root',manifest.get('root_at_install',''))
   files=[self.safe('AGENTS.md')]+[p for d in ['Project','PKM'] for p in self.safe(d).rglob('*.md') if not any(x in {'.git','node_modules','.venv','venv','__pycache__'} for x in p.relative_to(self.root).parts)]
   changed=0
   for p in files:
    self.safe(p.relative_to(self.root));old=p.read_text(encoding='utf-8-sig');body=old.replace('{{ROOT}}',str(self.root))
    if p==self.root/'AGENTS.md' and previous_root:body=body.replace('과제 루트: `'+previous_root+'`','과제 루트: `'+str(self.root)+'`')
    new=addressed(p,body)
    if new!=old:
     atomic(self.safe('PKM/System/History/path-'+uuid.uuid4().hex+'.txt'),p.read_bytes());atomic(p,new.encode());changed+=1
   for area in AREAS:self._index(area)
   manifest['current_root']=str(self.root);atomic(self.safe('PKM/System/workspace.json'),(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode())
   self.event('path_headers_refreshed','Refreshed current file locations',{'changed':changed})
  return {'changed':changed,'check':self.check()}
 def brief(self):
  self.manifest();view={}
  for area in ['Spec','Plan','Status','Decisions','Evidence']:
   view[area]=[{'path':str(p),'excerpt':p.read_text(encoding='utf-8')[:1800],'truncated':len(p.read_text(encoding='utf-8'))>1800} for p in self.entries(area)[-3:]]
  return {'root':str(self.root),'project':str(self.root/'Project'),'pkm':str(self.root/'PKM'),'current_records':view,'note':'Exact document excerpts, not an independent completion verdict; open the area index and needed originals.'}

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',required=True)
 s=p.add_subparsers(dest='command',required=True)
 i=s.add_parser('install');i.add_argument('--source',default=str(Path(__file__).resolve().parents[2]));i.add_argument('--copy-inputs',action='store_true')
 s.add_parser('check');s.add_parser('brief');s.add_parser('repair-paths')
 r=s.add_parser('read');r.add_argument('path')
 n=s.add_parser('new');n.add_argument('area',choices=list(AREAS));n.add_argument('title');n.add_argument('--body-file',required=True);n.add_argument('--status',default='draft')
 u=s.add_parser('update');u.add_argument('path');u.add_argument('--body-file',required=True);u.add_argument('--expected-sha',required=True)
 a=p.parse_args()
 try:
  w=Workspace(a.root)
  if a.command=='install':result=w.install(a.source,a.copy_inputs)
  elif a.command=='read':result=w.read(a.path)
  elif a.command=='new':result=w.new(a.area,a.title,Path(a.body_file).read_text(encoding='utf-8'),a.status)
  elif a.command=='update':result=w.update(a.path,Path(a.body_file).read_text(encoding='utf-8'),a.expected_sha)
  elif a.command=='repair-paths':result=w.repair_paths()
  else:result=getattr(w,a.command)()
  print(json.dumps(result,ensure_ascii=False,indent=2))
  if a.command=='check' and not result['ok']:raise SystemExit(1)
 except (ValueError,OSError) as e:p.exit(2,str(e)+'\n')

if __name__=='__main__':main()
