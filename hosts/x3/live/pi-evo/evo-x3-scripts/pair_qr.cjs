const path=require('node:path'),os=require('node:os');const HOME=os.homedir();
const PKG=path.join(HOME,'.pi/agent/npm/node_modules/pi-mobile');
const jiti=require(path.join(HOME,'.local/lib/node_modules/@earendil-works/pi-coding-agent/node_modules/jiti'))(__filename);
const {HubLink}=jiti(path.join(PKG,'src/link.ts'));const {loadConfig,linkSecret}=jiti(path.join(PKG,'src/store.ts'));
const QR=require(path.join(HOME,'.pi/agent/npm/node_modules/qrcode'));
const out=process.argv[2];
const link=new HubLink({config:()=>loadConfig(),secret:linkSecret(),info:()=>({id:'qr-'+process.pid,name:'pair-qr',cwd:HOME}),onRequest:()=>null,
 onState:async(s)=>{if(s.kind!=='linked')return;try{const r=await link.request('pair',{});
  const l=r.links.find(x=>x.url.startsWith('https://evo-x3-1'))||r.links[0];
  await QR.toFile(out,l.url,{width:512,margin:2});console.log('QR_OK origin='+new URL(l.url).origin+' expires='+new Date(r.expiresAt).toISOString());}
  catch(e){console.log('ERR '+e.message)}link.stop();process.exit(0)}});
link.start();setTimeout(()=>{console.log('TIMEOUT state='+link.state.kind);process.exit(1)},20000);
