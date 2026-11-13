const fs=require('fs');
const w=JSON.parse(fs.readFileSync(process.argv[2]));
const by={};for(const n of w.nodes)by[n.name]=n;
function run(code,ctx){return new Function('$input','$','$getWorkflowStaticData','require',code)(ctx.input,ctx.$,()=>ctx.sd,require);}
for(const f of ['t-lt5','t-10k','t-nurture']){
  const p=JSON.parse(fs.readFileSync('../'+f+'/lead-payload.json'));
  p.email='real-looking@gmail.com';p.page_url='https://businessgrowr.com/scorecard-v2?utm_source=fb';
  const map=run(by['Map Scorecard'].parameters.jsCode,{input:{first:()=>({json:{body:p,headers:{}}})},sd:{}})[0].json;
  const pick={contactId:'c1',contact:{tags:[]}};
  const sa=run(by['SA — build'].parameters.jsCode,{input:{first:()=>({json:{}})},$:(n)=>({first:()=>({json:n==='Map Scorecard'?map:pick})}),sd:{}});
  console.log(f,'route='+map.route,'lt5k='+map.lt5k,'tags='+map.tags.join('|'),'SA='+(sa.length?sa[0].json.meta_body.data[0].event_source_url+' form='+sa[0].json.meta_body.data[0].custom_data.form:'none'));
}
