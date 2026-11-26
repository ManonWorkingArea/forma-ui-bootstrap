#!/usr/bin/env python3
"""Read-only Forma V34 reference tooling. Browser capture is optional."""
import argparse, hashlib, json, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / 'references'
HTML = ROOT / 'assets/mockup/standalone.html'

def load(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def emit(x): print(json.dumps(x, ensure_ascii=False, indent=2))
def registry(): return load(REF/'COMPONENT_REGISTRY.json')['components']
def pages(): return load(REF/'PAGE_INDEX.json')['pages']
def visual(): return load(REF/'VISUAL_KEYS.json')
def layouts(): return load(REF/'LAYOUT_REGISTRY.json')['templates']
def layout(id):
    for row in layouts():
        if row['id']==id: return row
    raise ValueError(f"Unknown layout id: {id}. Use 'layouts' to list valid ids.")
def search(rows,q): return [x for x in rows if q.casefold() in json.dumps(x,ensure_ascii=False).casefold()]
def manifest(): return load(REF/'MANIFEST.json')
def check_manifest():
    m=manifest(); rows=[]
    for rel,expected in m['sha256'].items():
        p=ROOT/rel; actual=hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None
        rows.append({'file':rel,'matches':actual==expected,'sha256':actual})
    return {'baseline':m['baseline'],'ok':all(x['matches'] for x in rows),'files':rows}
def inventory(p):
    d=load(p)
    if not isinstance(d,dict) or d.get('format')!='forma-ui-inventory.v1' or not isinstance(d.get('elements'),list): raise ValueError('Expected forma-ui-inventory.v1 export')
    if d.get('elementCount')!=len(d['elements']): raise ValueError('Inventory count mismatch')
    return d

def locate(q,limit=8):
    if not q.strip(): raise ValueError('Nonempty literal required')
    if len(q)>240: raise ValueError('Use a short selector, handler, or literal')
    out=[]
    for path in [HTML,ROOT/'assets/mockup/ui-inspector.js']:
        s=path.read_text(encoding='utf-8'); start=0
        while len(out)<limit:
            i=s.find(q,start)
            if i<0:break
            out.append({'file':str(path.relative_to(ROOT)),'line':s.count('\n',0,i)+1,'column':i-s.rfind('\n',0,i),'characterOffset':i,'excerpt':s[max(0,i-95):i+len(q)+120].replace('\n',' ')})
            start=i+len(q)
        if len(out)>=limit:break
    return out

def context(component):
    rows=[r for r in registry() if r['component']==component]
    keys=[k for k in visual()['keys'] if component in k['components'] or any(component.startswith(x+'.') for x in k['components'])]
    return {'component':component,'mappings':rows,'mappingStatus':'mapped' if rows else 'not in adapter; may be runtime fallback or proposed explicit name','visualKeys':keys,'tokens':visual()['tokens'],'contract':'references/DESIGN_SYSTEM.md','identity':'references/UI_INSPECTOR_CONTRACT.md','warning':'Selectors are legacy adapter hints, not production APIs. Preserve existing behavior. Confirm reference in browser.'}

def reference_data(p):
    d=load(p)
    if not isinstance(d,dict) or not all(k in d for k in ('component','reference','route','bounds')): raise ValueError('Expected selected Element reference JSON')
    return d

def issue(ref,problem,expected):
    d=reference_data(ref); c=context(d['component']); hint=d.get('sourceHint') or {}; queries=[]
    for q in [hint.get('handler'),hint.get('domId'),*hint.get('classes',[])]:
        if q and q not in queries:queries.append(q)
    return {'format':'forma-ui-task.v1','baseline':'V34','reference':d,'problem':problem,'expected':expected,'context':c,'sourceCandidates':{q:locate(q,3) for q in queries[:4]},'acceptance':['Before/after screenshots at reported viewport and relevant alternate widths','Preserve existing behavior and shared component contracts','No horizontal scrolling on DataTable; no overlap; visible focus','Record actual test results and unresolved differences'],'identityWarning':'Fallback DOM hash may change after restructure; do not guess a replacement. Re-export after changes.'}

def compare(a,b):
    a,b=inventory(a),inventory(b)
    if a['route']!=b['route']:raise ValueError('Compare inventories from the same route only')
    def group(d):
        out={}
        for x in d['elements']:out.setdefault(x['reference'],[]).append(x)
        return out
    aa,bb=group(a),group(b); common=set(aa)&set(bb); changes=[]; ambiguous=[]
    for k in sorted(common):
        if len(aa[k])!=1 or len(bb[k])!=1:ambiguous.append(k);continue
        x,y=aa[k][0],bb[k][0]; fields={z:{'before':x.get(z),'after':y.get(z)} for z in ('bounds','visibleBounds','state','label','component') if x.get(z)!=y.get(z)}
        if fields:changes.append({'reference':k,'changes':fields})
    return {'route':a['route'],'beforeViewport':a['viewport'],'afterViewport':b['viewport'],'sameViewport':a['viewport']==b['viewport'],'changed':changes,'onlyBefore':sorted(set(aa)-set(bb)),'onlyAfter':sorted(set(bb)-set(aa)),'ambiguous':ambiguous,'warning':'Inventory is viewport-visible, not complete DOM. Missing/changed references are not automatically regressions; responsive layouts and DOM fallback IDs can differ.'}

def capture(args):
    if not check_manifest()['ok']:raise ValueError('Pinned baseline verification failed')
    try:from playwright.sync_api import sync_playwright
    except ImportError as e:raise ValueError('Optional browser capture requires Python playwright and Chromium; all other commands are offline stdlib.') from e
    route=args.route.lstrip('#')
    if not re.fullmatch(r'(pilot|starter)/(admin|public|utility)/[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*',route):raise ValueError('Use a local mockup hash route, not a URL')
    if not (320<=args.width<=2560 and 300<=args.height<=1800):raise ValueError('Viewport outside supported capture range')
    out=Path(args.out).resolve();out.mkdir(parents=True,exist_ok=True);errors=[]
    with sync_playwright() as pw:
        opts={'headless':True,'args':['--disable-dev-shm-usage']}
        if args.chromium:opts['executable_path']=args.chromium
        browser=pw.chromium.launch(**opts)
        try:
            ctx=browser.new_context(viewport={'width':args.width,'height':args.height},has_touch=args.width<600,device_scale_factor=1)
            ctx.route(re.compile(r'^https?://'),lambda r:r.abort())
            page=ctx.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
            page.set_content(HTML.read_text(encoding='utf-8'),wait_until='load',timeout=20000)
            page.evaluate('(r)=>location.hash=r','#'+route)
            page.wait_for_timeout(700)
            if page.locator('#app').count()==0:raise ValueError('Mockup app not found')
            if page.get_by_text('Page not found', exact=True).is_visible() and route.split('/')[-1]!='404':raise ValueError('Reference route rendered Page not found; check pages index')
            # Disable debug for clean capture. Re-enable independently in the editor frame if present.
            page.evaluate('window.FormaUIInspector?.disable()')
            page.wait_for_timeout(180);page.screenshot(path=str(out/'clean.png'),timeout=10000)
            page.evaluate('window.FormaUIInspector?.enable()');page.wait_for_timeout(350)
            frames=[]
            for i,f in enumerate(page.frames):
                try:
                    if not f.evaluate('!!window.FormaUIInspector'):continue
                    f.evaluate('FormaUIInspector.enable()');f.wait_for_timeout(250)
                    rows=f.evaluate('FormaUIInspector.visible')
                    if not rows:continue
                    data={'format':'forma-ui-inventory.v1','route':rows[0]['route'],'viewport':f.evaluate('({width:innerWidth,height:innerHeight})'),'mode':f.evaluate('FormaUIInspector.mode'),'filter':'','elementCount':len(rows),'elements':rows}
                    name=f'inventory-{i}.json';(out/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');frames.append({'frame':i,'route':data['route'],'count':len(rows),'inventory':name})
                except Exception as e:errors.append('frame '+str(i)+': '+str(e))
            page.screenshot(path=str(out/'debug.png'),timeout=10000)
            result={'requestedRoute':route,'actualHash':page.evaluate('location.hash'),'title':page.title(),'visibleHeading':page.locator('h1:visible').first.text_content(timeout=2000) if page.locator('h1:visible').count() else None,'viewport':{'width':args.width,'height':args.height},'frames':frames,'errors':errors,'documentOverflow':page.evaluate('document.documentElement.scrollWidth>innerWidth'),'baselineSha256':hashlib.sha256(HTML.read_bytes()).hexdigest(),'note':'Exact bundled mockup rendered in Chromium using set_content; network blocked. Inspect screenshots and actual heading; capture is not route acceptance or a full visual audit.'}
            (out/'capture.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
            return result
        finally:browser.close()

def main():
    p=argparse.ArgumentParser(description=__doc__);s=p.add_subparsers(dest='cmd',required=True)
    s.add_parser('verify');s.add_parser('tokens')
    for cmd in ('components','pages','keys','layouts'):
        q=s.add_parser(cmd);q.add_argument('query',nargs='?',default='')
    q=s.add_parser('context');q.add_argument('component')
    q=s.add_parser('layout');q.add_argument('id')
    q=s.add_parser('locate');q.add_argument('literal');q.add_argument('--limit',type=int,default=8)
    q=s.add_parser('inspect');q.add_argument('inventory');q.add_argument('query',nargs='?',default='')
    q=s.add_parser('issue');q.add_argument('reference');q.add_argument('--problem',required=True);q.add_argument('--expected',required=True)
    q=s.add_parser('compare');q.add_argument('before');q.add_argument('after')
    q=s.add_parser('capture');q.add_argument('route');q.add_argument('--width',type=int,default=1440);q.add_argument('--height',type=int,default=900);q.add_argument('--out',required=True);q.add_argument('--chromium',default=None)
    a=p.parse_args()
    try:
        if a.cmd=='verify':r=check_manifest()
        elif a.cmd=='tokens':r=visual()['tokens']
        elif a.cmd=='components':r=search(registry(),a.query)
        elif a.cmd=='pages':r=search(pages(),a.query)
        elif a.cmd=='keys':r=search(visual()['keys'],a.query)
        elif a.cmd=='layouts':r=search(layouts(),a.query)
        elif a.cmd=='layout':r=layout(a.id)
        elif a.cmd=='context':r=context(a.component)
        elif a.cmd=='locate':r=locate(a.literal,max(1,min(a.limit,30)))
        elif a.cmd=='inspect':
            d=inventory(a.inventory);r={'route':d['route'],'viewport':d['viewport'],'matches':search(d['elements'],a.query)}
        elif a.cmd=='issue':r=issue(a.reference,a.problem,a.expected)
        elif a.cmd=='compare':r=compare(a.before,a.after)
        else:r=capture(a)
        emit(r)
        if (a.cmd=='verify' and not r['ok']) or (a.cmd=='capture' and (not r['frames'] or r['errors'])):return 1
        return 0
    except Exception as e:print(f'Error: {e}',file=sys.stderr);return 1
if __name__=='__main__':sys.exit(main())
