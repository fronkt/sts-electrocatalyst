$ErrorActionPreference='Stop'
$root=Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $PSScriptRoot))
Set-Location -LiteralPath $root
$d=$PSScriptRoot
$utf=New-Object System.Text.UTF8Encoding($false)
function SaveJson($name,$value){[IO.File]::WriteAllText((Join-Path $d $name),($value | ConvertTo-Json -Depth 35)+"`n",$utf)}
function SaveLines($name,$rows){$lines=@($rows | ForEach-Object {$_ | ConvertTo-Json -Depth 35 -Compress}); [IO.File]::WriteAllText((Join-Path $d $name),($lines -join "`n")+"`n",$utf)}
function Hash($path){(Get-FileHash -Algorithm SHA256 -LiteralPath $path).Hash.ToLowerInvariant()}
function ReadJson($path){Get-Content -Raw -LiteralPath $path | ConvertFrom-Json}
function Plain($text){[regex]::Replace([regex]::Replace([string]$text,'<[^>]+>',''),'\s+',' ').Trim()}
$occPath='results/s2_2026-09-19/literature_complementary/citation_occurrences.jsonl'
$occ=@(Get-Content -LiteralPath $occPath | ForEach-Object {$_ | ConvertFrom-Json})
$inventory=ReadJson 'results/s2_2026-09-19/literature_complementary/sources.json'
$priorPath='results/s2_2026-09-19/primary_identity_review/identity_review.json'
$prior=ReadJson $priorPath
$observations=@(ReadJson (Join-Path $d 'primary_page_observations.json'))
$receipts=@(ReadJson (Join-Path $d 'crossref_receipts.json'))+@(ReadJson (Join-Path $d 'crossref_receipts_supplement.json'))
$books=@{}
foreach($r in $receipts){
 if($r.status -notin @('DOI_RESOLVED','CACHE_REUSED')){continue}
 if((Hash $r.raw_path) -ne $r.sha256){throw ('Metadata hash mismatch: '+$r.doi)}
 $m=(ReadJson $r.raw_path).message
 if($m.DOI.ToLowerInvariant() -ne $r.doi.ToLowerInvariant()){throw 'Returned DOI mismatch'}
 $id='doi:'+$r.doi.ToLowerInvariant()
 $books[$id]=[pscustomobject][ordered]@{canonical_identity=$id;doi=$r.doi.ToLowerInvariant();title=(Plain ($m.title -join ' '));title_as_registered=@($m.title);authors=@($m.author | ForEach-Object {($_.given+' '+$_.family).Trim()});author_metadata=@($m.author);container_title=@($m.'container-title');volume=$m.volume;issue=$m.issue;page=$m.page;article_number=$m.'article-number';provider_type=$m.type;published=$m.published;published_online=$m.'published-online';published_print=$m.'published-print';posted=$m.posted;relation=$m.relation;metadata_evidence=@([ordered]@{provider='Crossref';url=$r.url;raw_path=$r.raw_path;sha256=$r.sha256;retrieved_utc=$r.retrieved_utc});local_identity_checked_files=@($prior.files | Where-Object {$_.canonical_identity -eq $id});primary_page_observations=@($observations | Where-Object {$_.identity -eq $id});inclusion_status='NOT_SCREENED';method_coding_status='NOT_CODED';preferred_version_for_screening=$null;methods_bundle_complete=$null}
}
foreach($b in $observations){
 if($books.ContainsKey($b.identity)){continue}
 $books[$b.identity]=[pscustomobject][ordered]@{canonical_identity=$b.identity;doi=if($b.identity.StartsWith('doi:')){$b.identity.Substring(4)}else{$null};title=$b.title;title_as_registered=@($b.title);authors=@($b.authors);provider_type=if($b.identity.StartsWith('arxiv:')){'preprint'}else{$b.resource_type};metadata_evidence=@([ordered]@{provider='Primary page';url=$b.url;observation_path='results/s2_2026-09-20/complementary_identity_review/primary_page_observations.json';observation_file_sha256=(Hash (Join-Path $d 'primary_page_observations.json'));observed_utc=$b.observed_utc});primary_page_observations=@($b);local_identity_checked_files=@();inclusion_status='NOT_SCREENED';method_coding_status='NOT_CODED';preferred_version_for_screening=$null;methods_bundle_complete=$null}
}
$dataPath='results/s2_2026-09-20/primary_download_receipts/zenodo_datacite.json'
$data=ReadJson $dataPath
if($data.data.attributes.doi -ne '10.5281/zenodo.12635'){throw 'DataCite DOI mismatch'}
$books['doi:10.5281/zenodo.12635'].metadata_evidence+=@([ordered]@{provider='DataCite';url='https://api.datacite.org/dois/10.5281/zenodo.12635';raw_path=$dataPath;sha256=(Hash $dataPath);receipt_path='results/s2_2026-09-20/primary_download_receipts/tertiary_access.json';note='Crossref 404 preserved; DOI uses DataCite registry.'})
$relations=New-Object System.Collections.Generic.List[object]
foreach($a in $observations | Where-Object {$_.identity -like 'arxiv:*'}){
 $doi=$a.related_journal_doi
 $basis='Explicit primary arXiv Related DOI field; publisher-deposited title and complete author tuple compared.'
 if($a.identity -eq 'arxiv:2410.01650'){
  $doi=$a.candidate_journal_doi;$j=$books['doi:'+$doi]
  if((Plain $a.title).ToLowerInvariant() -ne (Plain $j.title).ToLowerInvariant()){throw 'Wander title mismatch'}
  if(($a.authors -join '|') -ne ($j.authors -join '|')){throw 'Wander full author tuple mismatch'}
  $basis='Exact primary arXiv title and all four ordered author names match publisher DOI metadata; preprint 2024-10-02 and journal online 2025-02-10 retained. No title-fuzzy join.'
 }
 if($doi){
  if(-not $books.ContainsKey('doi:'+$doi)){throw ('Missing related DOI '+$doi)}
  $relations.Add([pscustomobject][ordered]@{from_identity=$a.identity;to_identity=('doi:'+$doi);relation='PREPRINT_JOURNAL_SAME_WORK';basis=$basis;primary_url=$a.url;preferred_version_for_screening=$null;note=if($a.identity -eq 'arxiv:2605.20985'){'Journal metadata has September 2026 month precision only; first-publication relation to September 18 cutoff remains unresolved. No journal-version selection made.'}else{'Identity relation only; later eligibility review selects the in-window version.'}})
 }
}
$relations.Add([pscustomobject]@{from_identity='doi:10.5281/zenodo.12635';to_identity='doi:10.1021/jp511426q';relation='SUPPORTING_DATA_FOR';basis='Zenodo primary record names exact article title and ordered creators';primary_url='https://zenodo.org/records/12635';preferred_version_for_screening=$null;note='Dataset remains a separate citable resource.'})
$relations.Add([pscustomobject]@{from_identity='url:https://github.com/zhongnanxu/rutile-OER';to_identity='doi:10.1021/jp511426q';relation='SUPPORTING_REPOSITORY_FOR';basis='Primary repository description names exact manuscript and authors';primary_url='https://github.com/zhongnanxu/rutile-OER';preferred_version_for_screening=$null;note='Repository not equated with versioned Zenodo release.'})
$div=@(ReadJson (Join-Path $d 'divanis_doi_candidates.json'))
$aliases=@{}
$aliasRows=@(
'042a9a45fd59a65e935a|doi:10.1039/c4cp00571f',
'0e5a6e9f2185ae021f12|doi:10.1021/jp409373c',
'3e018d49ed36f278e938|doi:10.1021/acs.jpcc.4c07477',
'421ddbbc082f03babf8f|doi:10.1002/cctc.201000397',
'4522ce6766f5f95d148b|arxiv:2512.05938',
'506e58c4a7a56d73c346|doi:10.1021/jp047349j',
'5e3c224d680664a3412f|doi:10.1021/jp511426q',
'698b2a528635e2658c36|doi:10.1016/j.coelec.2018.03.025',
'7b5139536c7330701308|doi:10.1002/cctc.201402756',
'9aa6a5424705ccc44899|doi:10.1103/physrevlett.118.077201',
'9dad04ac123a53fb58fe|doi:10.1103/physrevmaterials.8.014409',
'c14093648a21d0ff4299|url:https://www.quantum-espresso.org/Doc/INPUT_PW.html#ensemble_energies',
'c23fb82148d66c871688|doi:10.1021/acscatal.2c03997',
'c6d615cf577f0fd44074|doi:10.1039/d2cp04814k',
'cf8011f26f6fb551f9d0|url:https://gitlab.com/QEF/q-e/-/blob/master/Doc/Hubbard_input.tex',
'd86f9b657dd201db4891|doi:10.1021/acs.jpcc.6b09141',
'dee34036ea11ef8524bf|doi:10.1021/acs.jpcc.7b02383')
foreach($line in $aliasRows){$v=$line.Split('|');$aliases['unresolved:complementary:named-'+$v[0]]=$v[1]}
$aliases['unresolved:complementary:tran-4119-screen']='doi:10.1039/d4nr01390e'
$unresolvedNotes=@{
'unresolved:complementary:named-24b29ecfe2885b083970'='Paz is a surname without title/year/identifier; preserve as person/publication lead.'
'unresolved:complementary:named-62ab4bbed067a6aea16d'='Sole occurrence says Nabat and Paz carried publications. Known DOI 10.1103/physrevd.111.072002 identifies a Nabat article but does not establish this vague mention refers to that particular work.'
'unresolved:complementary:named-5a634e3ec4590cc08d04'='Holm names a multiple-testing procedure; no specific publication title/year/edition is cited. Do not assume the original paper.'
'unresolved:complementary:named-70de0b7df16a77028a0f'='Primary publisher identifies DOI 10.1021/acs.jpcc.7b03481 as Dickens/Norskov defect-site article. This key also holds a separate Briquet-critique context; fulltext support for joining it is absent. Preserve all three occurrences without forcing one canonical work.'
'unresolved:complementary:named-7d228ade81e3dc88fa12'='Program books means multiple unspecified editions without exact titles/files/URLs.'
'unresolved:complementary:named-87827a5550308c5e219c'='Reuter/Scheffler framework has no year/title/journal; multiple works could fit.'
'unresolved:complementary:named-a44e6b08a23bfff08dd3'='Otani Tsukuba ESM-RISM tutorial has no date/title/URL. Exact MOLs repository is verified separately and does not establish tutorial identity.'
'unresolved:documentation:qe-hp-manual-or-mailing-list'='Conflates hp.x manual and unspecified mailing-list advice. Need exact manual version and message URL/date; do not substitute HP journal article.'
}
$notesByRef=@{
5='Raw ESI M. T. M. lacks surname; primary RSC and deposited eight-author list identify Marc T. M. Koper. Crossref page start-only 1245; publisher 1245-1249. https://pubs.rsc.org/en/content/articlelanding/2013/sc/c2sc21601a'
7='Published title spells Infuence; preserve typo. Previous primary review retains differing ACS header/detailed online dates.'
9='ESI 2015 is issue year; deposited online date 2014-11-06. Both retained.'
11='ESI ncomms9253 is DOI suffix; article number 8253. Full ordered eight-author list/year match. https://www.nature.com/articles/ncomms9253'
12='ESI Sciencemag 2016,352,6283 supplies issue 6283. Full 25-author tuple matches Science 352(6283),333-337.'
15='ESI ncomms14169 matches DOI suffix and article number. https://www.nature.com/articles/ncomms14169'
17='Author CV points to later correction DOI 10.1021/acscatal.8b01775. Linked warning only, not an additional discovered candidate; inspect during article review.'
20='ESI 2018 agrees with publication metadata; copyright 2017 in local PDF is not first publication.'
23='Two Qian Zhang authors retained with registered (m)/(f) disambiguators.'
24='ESI 2019 is issue year; primary article PDF online 2018-02-19, Crossref print 2019-02 only. https://pure.tue.nl/ws/portalfiles/portal/116894860/1_s2.0_S0920586118300920_main.pdf'
25='Methodological reference with 2004 dates retained regardless of later screening window.'
}
$links=New-Object System.Collections.Generic.List[object]
$divReview=New-Object System.Collections.Generic.List[object]
foreach($group in $occ | Group-Object normalized_identity | Sort-Object Name){
 $key=$group.Name;$canonical=$null;$status='UNRESOLVED';$basis='';$notes='';$candidates=@($group.Group.possible_identity_keys | ForEach-Object {$_} | Where-Object {$_} | Sort-Object -Unique)
 if($key.StartsWith('doi:')){$canonical=$key;$status='RESOLVED_IDENTIFIER';$basis='Literal source DOI equals primary DOI identifier; surrounding scientific claims unverified.'}
 elseif($key -match '^unresolved:complementary:divanis-ref-(\d+)$'){
  $n=[int]$Matches[1];$v=$div | Where-Object {$_.reference_number -eq $n};$canonical='doi:'+$v.candidate_doi;$status='RESOLVED_BIBLIOGRAPHIC';$basis='Ordered author tuple plus journal, citation year, volume/page range or distinctive article identifier compared with primary Crossref metadata; documented source defects retained.'
  if($notesByRef.ContainsKey($n)){$notes=$notesByRef[$n]}
  $divReview.Add([pscustomobject][ordered]@{reference_number=$n;source_identity=$key;canonical_identity=$canonical;source_occurrence_id=$group.Group[0].occurrence_id;source_path=$group.Group[0].source_path;source_sha256=$group.Group[0].source_sha256;line_start=$group.Group[0].line_start;line_end=$group.Group[0].line_end;reference_role=$group.Group[0].discovery_role;identity_status=$status;match_basis=$basis;notes=$notes;metadata_evidence=$books[$canonical].metadata_evidence;inclusion_status='NOT_SCREENED';method_coding_status='NOT_CODED'})
 }
 elseif($key.StartsWith('unresolved:arxiv:')){
  $canonical=$key.Substring('unresolved:'.Length);$rel=$relations | Where-Object {$_.from_identity -eq $canonical -and $_.relation -eq 'PREPRINT_JOURNAL_SAME_WORK'}
  if($rel){$canonical=$rel.to_identity;$basis=$rel.basis;$notes=$rel.note}else{$basis='Exact arXiv identifier/title/complete author list and primary submission history. No journal version inferred.'}
  $status='RESOLVED_IDENTIFIER'
 }
 elseif($aliases.ContainsKey($key)){
  $canonical=$aliases[$key];$status='RESOLVED_NAMED_STUDY';$basis='Named-study subject/context linked to explicit article/arXiv citation in the fixed source set, with primary author/title metadata checked. Study lead only; scientific attribution unverified.'
  if($canonical.StartsWith('url:')){$status='RESOLVED_RESOURCE';$basis='Named documentation title/variable matches primary project documentation.'}
  if($key -like '*named-5e3c224d680664a3412f'){$notes='Xu mentions cover study and associated calculation corpus. Study-level alias does not merge separate Zenodo dataset/GitHub repository with article; original contexts retain resource-specific scope.'}
  if($key -like '*named-3e018d49ed36f278e938'){$notes='Wander mentions cover study/associated data; repository has separate resource identity.'}
  if($key -like '*named-698b2a528635e2658c36'){$basis='Primary article PDF page 2 introduces ESSI; title/all four authors/DOI match existing ESSI-origin lead.'}
  if($key -like '*named-c23fb82148d66c871688'){$basis='Paired Razzaq/Exner authors and Gmax subject match primary publisher article title/full author tuple; no equation verification.'}
  if($key -like '*named-9aa6a5424705ccc44899'){$basis='Exact Berlijn PRL 118, 077201 (2017) tuple matches primary APS DOI/title/author list.'}
 }
 elseif($key -like 'unresolved:url:github.com/*'){$canonical='url:https://'+$key.Substring('unresolved:url:'.Length);$status='RESOLVED_RESOURCE';$basis='Exact repository owner/name URL and primary description.'}
 elseif($key -eq 'unresolved:repository:zhongnanxu/rutile-OER'){$canonical='url:https://github.com/zhongnanxu/rutile-OER';$status='RESOLVED_RESOURCE';$basis='Exact repository alias joins explicit GitHub URL; remains separate from article/Zenodo.'}
 else{
  if($unresolvedNotes.ContainsKey($key)){$notes=$unresolvedNotes[$key]}elseif($key.StartsWith('unresolved:data-source:')){$notes='Generic dataset/database family without exact cited article/release/version/URL. Familiar project name cannot select one paper or release.'}else{throw ('Unhandled identity '+$key)}
  $basis='Insufficient exact bibliography; no forced merge.'
  if($key -like '*named-70de0b7df16a77028a0f'){$status='PARTIALLY_RESOLVED';$candidates=@('doi:10.1021/acs.jpcc.7b03481')}
 }
 if($canonical -and -not $books.ContainsKey($canonical)){throw ('Missing canonical record '+$canonical)}
 $links.Add([pscustomobject][ordered]@{source_identity=$key;source_occurrence_ids=@($group.Group.occurrence_id);source_occurrence_count=$group.Count;source_labels=@($group.Group.verbatim_identity | Sort-Object -Unique);canonical_identity=$canonical;identity_status=$status;match_basis=$basis;notes=$notes;candidate_identities=$candidates;evidence=@(if($canonical){$books[$canonical].metadata_evidence});inclusion_status='NOT_SCREENED';method_coding_status='NOT_CODED';methods_bundle_complete=$null})
}
$byKey=@{};foreach($l in $links){$byKey[$l.source_identity]=$l}
$occHash=Hash $occPath
$edges=@($occ | ForEach-Object {$l=$byKey[$_.normalized_identity];[pscustomobject][ordered]@{occurrence_id=$_.occurrence_id;source_identity=$_.normalized_identity;canonical_identity=$l.canonical_identity;identity_status=$l.identity_status;source_id=$_.source_id;source_path=$_.source_path;source_sha256=$_.source_sha256;line_start=$_.line_start;line_end=$_.line_end;page=$_.page;reference_number=$_.reference_number;original_occurrence_file=$occPath;original_occurrence_file_sha256=$occHash;inclusion_status='NOT_SCREENED';method_coding_status='NOT_CODED'}})
SaveLines 'bibliographic_records.jsonl' @($books.Values | Sort-Object canonical_identity)
SaveLines 'identity_links.jsonl' $links
SaveLines 'citation_identity_links.jsonl' $edges
SaveLines 'divanis_identity_review.jsonl' @($divReview | Sort-Object reference_number)
SaveLines 'bibliographic_relations.jsonl' $relations
SaveLines 'unresolved_identities.jsonl' @($links | Where-Object {-not $_.canonical_identity})
$sourceChecks=@($inventory.registered_sources | ForEach-Object {[pscustomobject]@{path=$_.path;expected=$_.sha256;actual=(Hash $_.path);matches=((Hash $_.path) -eq $_.sha256)}})
$pdfChecks=@($prior.files | ForEach-Object {[pscustomobject]@{path=$_.source_pdf;expected=$_.pdf_sha256;actual=(Hash $_.source_pdf);matches=((Hash $_.source_pdf) -eq $_.pdf_sha256)}})
if(@($sourceChecks | Where-Object {-not $_.matches}).Count -or @($pdfChecks | Where-Object {-not $_.matches}).Count){throw 'Prior source/PDF hash mismatch'}
if($links.Count -ne 120 -or $edges.Count -ne 271 -or @($edges.occurrence_id | Sort-Object -Unique).Count -ne 271 -or $divReview.Count -ne 25){throw 'Coverage invariant failed'}
$resolved=@($links | Where-Object {$_.canonical_identity});$unresolved=@($links | Where-Object {-not $_.canonical_identity})
$verification=[ordered]@{reviewed_utc=[DateTime]::UtcNow.ToString('o');status='PASS_FILE_IDENTITY_ACCOUNTING';scope='Identity only; no inclusion/method coding, exhaustive-discovery verdict or fulltext-completeness claim';original_identity_keys=120;original_occurrences=271;identity_links=$links.Count;occurrence_links=$edges.Count;resolved_identity_keys=$resolved.Count;resolved_occurrences=($resolved | Measure-Object -Property source_occurrence_count -Sum).Sum;unresolved_or_partial_identity_keys=$unresolved.Count;unresolved_or_partial_occurrences=($unresolved | Measure-Object -Property source_occurrence_count -Sum).Sum;canonical_identities_reached=@($resolved.canonical_identity | Sort-Object -Unique).Count;primary_metadata_records=$books.Count;crossref_requests=$receipts.Count;crossref_resolved_or_reused=@($receipts | Where-Object {$_.status -in @('DOI_RESOLVED','CACHE_REUSED')}).Count;crossref_unresolved=@($receipts | Where-Object {$_.status -notin @('DOI_RESOLVED','CACHE_REUSED')});divanis_references_exactly_1_to_25=((@($divReview.reference_number | Sort-Object) -join ',') -eq ((1..25) -join ','));preprint_journal_relations=@($relations | Where-Object {$_.relation -eq 'PREPRINT_JOURNAL_SAME_WORK'}).Count;source_hash_checks=$sourceChecks;prior_pdf_hash_checks=$pdfChecks;prior_review_path=$priorPath;prior_review_sha256=(Hash $priorPath);original_inventory_hashes=@('results/s2_2026-09-19/literature_complementary/sources.json',$occPath,'results/s2_2026-09-19/literature_complementary/access_inventory.jsonl','results/s2_2026-09-19/literature_complementary/README.md' | ForEach-Object {[pscustomobject]@{path=$_;sha256=(Hash $_)}});all_not_screened=(@($links | Where-Object {$_.inclusion_status -ne 'NOT_SCREENED'}).Count -eq 0);all_not_coded=(@($links | Where-Object {$_.method_coding_status -ne 'NOT_CODED'}).Count -eq 0);no_openalex_requests=$true;no_scientific_processes=$true;reconciliation_script_sha256=(Hash $PSCommandPath)}
SaveJson 'verification.json' $verification
[pscustomobject]$verification | Select-Object original_identity_keys,original_occurrences,resolved_identity_keys,resolved_occurrences,unresolved_or_partial_identity_keys,unresolved_or_partial_occurrences,canonical_identities_reached,primary_metadata_records,preprint_journal_relations | ConvertTo-Json
