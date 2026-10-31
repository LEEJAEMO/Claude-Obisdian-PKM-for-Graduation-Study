from pathlib import Path
import hashlib,json,shutil,subprocess,sys,tempfile,unittest
from unittest.mock import patch

SYSTEM=Path(__file__).resolve().parents[1]
SOURCE=SYSTEM.parents[1]
sys.path.insert(0,str(SYSTEM))
import workspace
from workspace import Workspace,AREAS,HEADER

class WorkspaceTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(prefix='workspace-test-',dir=SYSTEM.parent.parent.parent)
  self.root=Path(self.tmp.name)/'과제 root with spaces';self.root.mkdir()
  self.original=self.root/'README.md';self.original.write_bytes(b'# provided task\n')
  (self.root/'main.py').write_bytes(b'print("starter")\n')
  self.w=Workspace(self.root)
 def tearDown(self):self.tmp.cleanup()
 def install(self):return self.w.install(SOURCE,True)
 def test_author_and_model_preserved_when_human_edits_ai_document(self):
  self.install();ai=Workspace(self.root,workspace.identity('ai','test-model','test fixture'))
  doc=ai.new('Spec','author test','AI draft');p=Path(doc['path']);rel=p.relative_to(self.root)
  human=Workspace(self.root,workspace.identity('human','ignored','user confirmed'))
  human.update(rel,'# Human revision',doc['sha256'])
  meta,_=workspace.split_metadata(p.read_text(encoding='utf-8'))
  self.assertEqual(meta['과제 루트 기준 상대경로'],rel.as_posix())
  self.assertEqual(meta['최초 작성 모델'],'test-model')
  self.assertEqual(meta['최초 작성 주체'],'ai')
  self.assertEqual(meta['최근 수정 주체'],'human')
  self.assertEqual(meta['최근 수정 모델'],'not-applicable')
  before=meta.copy();human.repair_paths()
  self.assertEqual(before,workspace.split_metadata(p.read_text(encoding='utf-8'))[0])
  self.assertTrue(human.check()['ok'])
 def test_unknown_original_not_attributed_to_installer(self):
  ai=Workspace(self.root,workspace.identity('ai','test-model','test fixture'));ai.install(SOURCE,True)
  meta,_=workspace.split_metadata((self.root/'Project/README.md').read_text(encoding='utf-8'))
  self.assertEqual(meta['최초 작성 주체'],'unknown')
  self.assertEqual(meta['최초 작성 모델'],'unknown')
 def test_legacy_path_only_and_missing_relative_are_detected_and_repaired(self):
  self.install();p=self.w.entries('Spec')[0]
  p.write_text(HEADER+str(p)+'\n\n# legacy\n',encoding='utf-8')
  self.assertFalse(self.w.check()['ok']);self.w.repair_paths()
  meta,body=workspace.split_metadata(p.read_text(encoding='utf-8'))
  self.assertEqual(meta['최초 작성 주체'],'unknown');self.assertEqual(body,'# legacy')
  self.assertTrue(self.w.check()['ok'])
 def test_mixed_and_unknown_model_identity(self):
  self.install();mixed=Workspace(self.root,workspace.identity('mixed','unknown','human and AI contributions confirmed'))
  doc=mixed.new('Log','shared drafting','Both contributed');meta,_=workspace.split_metadata(Path(doc['path']).read_text(encoding='utf-8'))
  self.assertEqual(meta['최초 작성 주체'],'mixed');self.assertEqual(meta['최초 작성 모델'],'unknown')
  with self.assertRaises(ValueError):workspace.identity('ai','model\ninjection','test')
 def test_root_layout_and_all_path_headers(self):
  r=self.install();self.assertTrue(r['check']['ok'])
  for name in ['AGENTS.md','Project','PKM']:self.assertTrue((self.root/name).exists())
  self.assertTrue((self.root/'PKM/index.md').exists())
  for a in AREAS:self.assertTrue((self.root/f'PKM/{a}/index.md').exists())
  for p in [self.root/'AGENTS.md',*self.root.joinpath('PKM').rglob('*.md'),*self.root.joinpath('Project').rglob('*.md')]:
   self.assertEqual(p.read_text(encoding='utf-8').splitlines()[0],HEADER+str(p.resolve()))
  self.assertNotIn('{{ROOT}}',(self.root/'AGENTS.md').read_text(encoding='utf-8'))
 def test_inputs_are_working_copies_originals_unchanged(self):
  original=self.original.read_bytes();starter=(self.root/'main.py').read_bytes()
  self.install()
  self.assertEqual(self.original.read_bytes(),original)
  self.assertEqual((self.root/'main.py').read_bytes(),starter)
  self.assertEqual((self.root/'Project/main.py').read_bytes(),starter)
  self.assertIn('# provided task',(self.root/'Project/README.md').read_text(encoding='utf-8'))
 def test_existing_root_instructions_preserved_and_current_session_readable(self):
  p=self.root/'AGENTS.md';p.write_text('# Platform\nUse provided test command.\n',encoding='utf-8');old=p.read_bytes()
  self.install();text=p.read_text(encoding='utf-8')
  self.assertIn('Use provided test command.',text)
  self.assertIn('모든 .md',text)
  self.assertEqual((self.root/'PKM/System/Backups/AGENTS-before-install.txt').read_bytes(),old)
  self.assertIn('PKM/index.md',text)
 def test_index_guides_and_multiple_documents_per_area(self):
  self.install();p=self.root/'PKM/Spec/index.md';guide=p.read_text(encoding='utf-8').split('<!-- entries:start -->')[0]
  a=self.w.new('Spec','filter','R-002: filter records',related=['P001','Project/main.py'])
  b=self.w.new('Spec','export','R-003: export records')
  self.assertNotEqual(a['id'],b['id']);text=p.read_text(encoding='utf-8')
  for r in [a,b]:self.assertIn(Path(r['path']).name,text)
  self.assertEqual(workspace.split_metadata(guide)[1],workspace.split_metadata(text.split('<!-- entries:start -->')[0])[1])
 def test_update_history_and_stale_write(self):
  self.install();p=self.w.entries('Spec')[0];rel=p.relative_to(self.root);old=self.w.read(rel)
  self.w.update(rel,'# Updated task\nR-004: empty input behavior',old['sha256'])
  with self.assertRaises(ValueError):self.w.update(rel,'stale',old['sha256'])
  backups=list((self.root/'PKM/System/History').glob('*.txt'))
  self.assertIn(old['content'],[p.read_text(encoding='utf-8') for p in backups])
  self.assertTrue(self.w.check()['ok'])
 def test_reinstall_is_idempotent_preserves_content(self):
  self.install();p=self.w.entries('Status')[0];old=self.w.read(p.relative_to(self.root));self.w.update(p.relative_to(self.root),'# Current\nnext: implement parser',old['sha256'])
  before=p.read_bytes();r=self.w.install(SOURCE,True)
  self.assertFalse(r['installed']);self.assertEqual(p.read_bytes(),before)
 def test_path_and_index_check_detects_direct_edit_omissions(self):
  self.install();p=self.root/'PKM/Plan/P999-direct.md';p.write_text('# no header\n',encoding='utf-8')
  report=self.w.check();self.assertFalse(report['ok'])
  self.assertTrue(any(x['issue'].startswith('unindexed') for x in report['issues']))
  self.assertTrue(any('first-line' in x['issue'] for x in report['issues']))
  self.w.repair_paths();self.assertTrue(self.w.check()['ok'])
 def test_relocated_workspace_can_refresh_actual_addresses(self):
  self.install();dest=Path(self.tmp.name)/'새 위치';shutil.copytree(self.root,dest)
  moved=Workspace(dest);self.assertFalse(moved.check()['ok'])
  moved.repair_paths();self.assertTrue(moved.check()['ok'])
  self.assertTrue((dest/'AGENTS.md').read_text(encoding='utf-8').startswith(HEADER+str(dest)))
  self.assertIn('과제 루트: `'+str(dest)+'`',(dest/'AGENTS.md').read_text(encoding='utf-8'))
 def test_no_arbitrary_paths_or_unrelated_pkm_overwrite(self):
  with self.assertRaises(ValueError):self.w.safe('../outside.md')
  (self.root/'PKM').mkdir();(self.root/'PKM/own.txt').write_text('keep',encoding='utf-8')
  with self.assertRaises(ValueError):self.install()
  self.assertEqual((self.root/'PKM/own.txt').read_text(encoding='utf-8'),'keep')
 def test_project_execution_and_pkm_state_are_separate(self):
  self.install();run=subprocess.run([sys.executable,str(self.root/'Project/main.py')],cwd=self.root/'Project',capture_output=True,text=True)
  self.assertEqual(run.returncode,0);self.assertEqual(run.stdout.strip(),'starter')
  doc=self.w.new('Evidence','starter check','Actual stdout: starter; exit 0',status='passed',related=['Project/main.py'])
  self.assertTrue(Path(doc['path']).is_relative_to(self.root/'PKM/Evidence'))
  self.assertFalse((self.root/'PKM/main.py').exists())
 def test_brief_is_read_only_and_returns_folder_documents(self):
  self.install();before={str(p):p.read_bytes() for p in (self.root/'PKM').rglob('*') if p.is_file()}
  view=self.w.brief();self.assertIn('Spec',view['current_records']);self.assertTrue(view['current_records']['Spec'])
  self.assertEqual(before,{str(p):p.read_bytes() for p in (self.root/'PKM').rglob('*') if p.is_file()})
 def test_cli_install_new_check_from_other_cwd(self):
  command=[sys.executable,'-B','-X','utf8',str(SYSTEM/'workspace.py'),'--root',str(self.root)]
  for args in [['install','--source',str(SOURCE),'--copy-inputs'],['brief'],['check']]:
   run=subprocess.run(command+args,cwd=self.tmp.name,capture_output=True,encoding='utf-8',timeout=20)
   self.assertEqual(run.returncode,0,run.stderr);self.assertIsInstance(json.loads(run.stdout),dict)
 def test_install_does_not_copy_git_configs_or_cache(self):
  for name in ['.git','.codex','node_modules']:
   (self.root/name).mkdir();(self.root/name/'keep.txt').write_text('not task input',encoding='utf-8')
  self.install()
  for name in ['.git','.codex','node_modules']:self.assertFalse((self.root/'Project'/name).exists())
 def test_failed_write_never_logs_success(self):
  self.install();p=self.w.entries('Spec')[0];rel=p.relative_to(self.root);old=self.w.read(rel);real=workspace.atomic
  def fail(target,data):
   if target==p:raise OSError('simulated write failure')
   return real(target,data)
  with patch('workspace.atomic',side_effect=fail),self.assertRaises(OSError):self.w.update(rel,'failed replacement',old['sha256'])
  self.assertEqual(p.read_text(encoding='utf-8'),old['content'])
  last=json.loads((self.root/'PKM/System/events.jsonl').read_text(encoding='utf-8').splitlines()[-1]);self.assertEqual(last['kind'],'save_started')

if __name__=='__main__':unittest.main()
