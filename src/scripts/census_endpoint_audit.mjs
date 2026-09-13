/** Post-hoc saved-endpoint audit. No model evaluations or changes to census rules. */
import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
export async function audit(root) {
 const base='results/site_census_2026-09-06';
 const pins={};
 const read=async rel=>{const b=await fs.readFile(path.join(root,rel)); pins[rel]=crypto.createHash('sha256').update(b).digest('hex');return JSON.parse(b);};
 const p=await read(base+'/readout_full/per_site.json');
 assert.equal(p.partial,false); assert.equal(p.missing.length,0);
 const six=['Ni31Cr29Cu5Mn35','Fe25Co25Ni25Cr25','Cu26Ni9Cr31Co33','Ni34Fe6Cu29Co31','Cu8Cr23Mn35Co34','Cu22Fe30Co32Mn15'];
 const rows=p.rows.filter(r=>six.includes(r.formula)&&r.tag==='mpa0'&&['CENSUS-1','CENSUS-3'].includes(r.arm));
 const cache={};
 async function get(r){if(!cache[r.manifest]) cache[r.manifest]=await read(base+'/results/'+r.manifest+'_result.json'); assert.equal(crypto.createHash('sha256').update((await fs.readFile(path.join(root,base+'/results/'+r.manifest+'_result.json'))).toString('utf8').replaceAll('\r\n','\n')).digest('hex'),p.manifests_read[r.manifest].result_sha256_lf); const row=cache[r.manifest].results.find(x=>x.formula===r.formula).row; const s=row.per_site_records.find(x=>x.seed===r.seed&&x.site_index===r.site_index);assert(s);return {s,clean:row.decoration_records.find(x=>x.seed===r.seed).relaxed_slab};}
 function vector(a,b,st){return a.map((v,k)=>{for(let j=0;j<3;j++)if(j!==k)assert(Math.abs(st.cell_A[k][j])<1e-10,'orthogonal cell required'); const d=v-b[k], L=st.cell_A[k][k];return st.pbc[k]?d-Math.round(d/L)*L:d;});}
 const norm=a=>Math.hypot(...a);
 const dist=(a,b,st)=>norm(vector(a,b,st));
 const steps=(oh,o,ooh)=>[oh,o-oh,ooh-o,4.92-ooh];
 const eta=(oh,o,ooh)=>Math.max(...steps(oh,o,ooh))-1.23;
 const count=(rs,key)=>Object.fromEntries([...new Set(rs.map(r=>r[key]))].sort().map(k=>[k,rs.filter(r=>r[key]===k).length]));
 const median=xs=>{xs=[...xs].sort((a,b)=>a-b);let n=xs.length;return n? (xs[Math.floor((n-1)/2)]+xs[Math.floor(n/2)])/2:null;};
 const summary=rs=>({n:rs.length,eta_min_V:rs.length?Math.min(...rs.map(r=>r.eta_V)):null,eta_median_V:median(rs.map(r=>r.eta_V)),metals:count(rs,'initial_metal'),O_categories:count(rs,'O_category'),OOH_categories:count(rs,'OOH_category'),pls:count(rs,'pls'),strict_intact:rs.filter(r=>r.all_states_intact).length,adsorbate_intact:rs.filter(r=>r.all_states_adsorbate_intact).length});
 const details=[];
 for(const r of rows){const {s,clean}=await get(r);assert(Math.abs(eta(s.dG_OH,s.dG_O,s.dG_OOH)-r.eta_V)<1e-10);assert(Math.abs(s.eta-r.eta_V)<1e-10);
  const geom={};for(const sp of ['OH','O','OOH']){const st=s.relaxed_states[sp];assert.deepEqual(st.symbols.slice(0,clean.symbols.length),clean.symbols);const fixed=new Set(st.fixed_atom_indices);const ds=clean.positions_A.map((pos,i)=>({index:i,symbol:clean.symbols[i],distance_A:dist(st.positions_A[i],pos,st),vector_A:vector(st.positions_A[i],pos,st)}));const free=ds.filter(x=>!fixed.has(x.index)).sort((a,b)=>b.distance_A-a.distance_A);const m=s.initial_binding_metal_index;geom[sp]={max_free:free[0],rms_free_A:Math.sqrt(free.reduce((t,x)=>t+x.distance_A**2,0)/free.length),binding_metal_displacement:ds[m],n_free_above_0_5_A:free.filter(x=>x.distance_A>0.5).length};
   if(sp==='O'){const a=st.symbols.length-1; const contacts=st.symbols.map((sym,i)=>({index:i,symbol:sym,distance_A:dist(st.positions_A[a],st.positions_A[i],st)})).filter(x=>x.index<clean.symbols.length&&x.symbol!=='O').sort((a,b)=>a.distance_A-b.distance_A);assert(Math.abs(contacts[0].distance_A-r.O_m_o_A)<1e-9);geom.O.contacts=contacts.slice(0,3);geom.O.binding_metal_lattice_O_neighbors=clean.symbols.map((sym,i)=>({index:i,symbol:sym,clean_A:dist(clean.positions_A[m],clean.positions_A[i],clean),O_state_A:dist(st.positions_A[m],st.positions_A[i],st)})).filter(x=>x.symbol==='O').sort((a,b)=>a.clean_A-b.clean_A).slice(0,6);}
  }
  const starts=s.start_records.O.map(x=>({...x,delta_from_retained_eV:x.energy_eV-s.relaxed_states.O.energy_eV,eta_O_substitution_V:eta(s.dG_OH,s.dG_O+x.energy_eV-s.relaxed_states.O.energy_eV,s.dG_OOH)}));
  details.push({...r,steps_eV:steps(s.dG_OH,s.dG_O,s.dG_OOH),geometry:geom,O_starts:starts,O_energy_minimum_eta_floor_V:Math.max(s.dG_OH,(s.dG_OOH-s.dG_OH)/2,4.92-s.dG_OOH)-1.23,O_energy_floor_plateau_eV:[s.dG_OOH-Math.max(s.dG_OH,(s.dG_OOH-s.dG_OH)/2,4.92-s.dG_OOH),s.dG_OH+Math.max(s.dG_OH,(s.dG_OOH-s.dG_OH)/2,4.92-s.dG_OOH)]});
 }
 const alloys={}; for(const f of six){const rs=details.filter(r=>r.formula===f).sort((a,b)=>a.eta_V-b.eta_V||a.seed-b.seed||a.site_index-b.site_index);assert.equal(rs.length,120);assert.equal(new Set(rs.map(r=>r.seed+'/'+r.site_index)).size,120);assert.equal(new Set(rs.map(r=>r.seed)).size,30);alloys[f]={all:summary(rs),lowest_12:summary(rs.slice(0,12)),Cr:summary(rs.filter(r=>r.initial_metal==='Cr')),non_Cr:summary(rs.filter(r=>r.initial_metal!=='Cr')),O_reconstructed:summary(rs.filter(r=>r.geometry.O.max_free.distance_A>0.5)),O_not_reconstructed:summary(rs.filter(r=>r.geometry.O.max_free.distance_A<=0.5)),winner:rs[0]};}
 const matched=[];for(const f of six){const w=alloys[f].winner; for(const tag of ['omat0','mp0','matpes']){const rr=p.rows.find(r=>r.formula===f&&r.tag===tag&&r.seed===w.seed&&r.site_index===w.site_index);if(rr)matched.push(rr);}}
 const tags=[...new Set(p.rows.map(r=>r.tag))];
 return {role:'post-hoc descriptive endpoint analysis; O-energy substitution is arithmetic only, not an unreconstructed counterfactual',input_sha256:pins,checks:{n_sites:details.length,n_alloys:six.length,eta_raw_and_CHE_verified:true,O_distances_independently_verified:true,orthogonal_cells_verified:true},model_tags:tags,alloys,matched_winner_models:matched,sites:details};
}
