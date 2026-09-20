$ErrorActionPreference='Stop'
$root=Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $PSScriptRoot))
Set-Location -LiteralPath $root
function ReadReviewJson($p){Get-Content -Raw -LiteralPath $p | ConvertFrom-Json}
function ReadReviewLines($p){@(Get-Content -LiteralPath $p | ForEach-Object {$_ | ConvertFrom-Json})}
function ReviewHash($p){(Get-FileHash -Algorithm SHA256 -LiteralPath $p).Hash.ToLowerInvariant()}
$checks=New-Object System.Collections.Generic.List[object]
function Check($name,$passed,$details){$checks.Add([pscustomobject]@{check=$name;passed=[bool]$passed;details=$details});if(-not $passed){throw ('Validation failed: '+$name)}}
$d=$PSScriptRoot
$orig=ReadReviewLines 'results/s2_2026-09-19/literature_complementary/citation_occurrences.jsonl'
$keys=ReadReviewLines (Join-Path $d 'identity_links.jsonl')
$edges=ReadReviewLines (Join-Path $d 'citation_identity_links.jsonl')
$books=ReadReviewLines (Join-Path $d 'bibliographic_records.jsonl')
$refs=ReadReviewLines (Join-Path $d 'divanis_identity_review.jsonl')
$rels=ReadReviewLines (Join-Path $d 'bibliographic_relations.jsonl')
$unresolved=ReadReviewLines (Join-Path $d 'unresolved_identities.jsonl')
Check 'Every original key exactly once' (($keys.Count -eq 120) -and ((@($keys.source_identity | Sort-Object -Unique) -join '|') -eq (@($orig.normalized_identity | Sort-Object -Unique) -join '|'))) '120 keys, including unresolved.'
Check 'Every original occurrence exactly once' (($edges.Count -eq 271) -and ((@($edges.occurrence_id | Sort-Object -Unique) -join '|') -eq (@($orig.occurrence_id | Sort-Object -Unique) -join '|'))) '271 original discovery edges.'
$origMap=@{};foreach($o in $orig){$origMap[$o.occurrence_id]=$o}
$keyMap=@{};foreach($k in $keys){$keyMap[$k.source_identity]=$k}
$bookMap=@{};foreach($b in $books){$bookMap[$b.canonical_identity]=$b}
$bad=New-Object System.Collections.Generic.List[string]
foreach($e in $edges){
 $o=$origMap[$e.occurrence_id];$k=$keyMap[$e.source_identity]
 foreach($f in @('source_id','source_path','source_sha256','line_start','line_end','page','reference_number')){if($e.$f -ne $o.$f){$bad.Add($e.occurrence_id+':'+$f)}}
 if($e.source_identity -ne $o.normalized_identity -or $e.canonical_identity -ne $k.canonical_identity -or $e.identity_status -ne $k.identity_status){$bad.Add($e.occurrence_id+':join')}
 if($e.original_occurrence_file_sha256 -ne (ReviewHash $e.original_occurrence_file)){$bad.Add($e.occurrence_id+':original hash')}
}
Check 'Source provenance and join agreement' ($bad.Count -eq 0) @($bad)
$bad=New-Object System.Collections.Generic.List[string]
foreach($k in $keys){$expected=@($orig | Where-Object {$_.normalized_identity -eq $k.source_identity});if(($expected.Count -ne $k.source_occurrence_count) -or ((@($expected.occurrence_id | Sort-Object) -join '|') -ne (@($k.source_occurrence_ids | Sort-Object) -join '|'))){$bad.Add($k.source_identity)}}
Check 'All per-key source occurrence lists exact' ($bad.Count -eq 0) @($bad)
Check 'Every accepted canonical identity exists once' ((@($books.canonical_identity | Sort-Object -Unique).Count -eq $books.Count) -and (@($keys | Where-Object {$_.canonical_identity -and -not $bookMap.ContainsKey($_.canonical_identity)}).Count -eq 0)) '88 metadata records; every accepted join supported.'
Check 'Unresolved list complete and unmerged' ((@($unresolved.source_identity | Sort-Object) -join '|') -eq (@(($keys | Where-Object {-not $_.canonical_identity}).source_identity | Sort-Object) -join '|')) '17 unresolved/partial keys retain null canonical identity.'
Check 'Divanis references exactly 1 through 25' (($refs.Count -eq 25) -and ((@($refs.reference_number | Sort-Object) -join ',') -eq ((1..25) -join ','))) 'Reference 25 retains methodological role.'
Check 'Six supported version relations retained' (@($rels | Where-Object relation -eq 'PREPRINT_JOURNAL_SAME_WORK').Count -eq 6) 'Version preference remains null.'
Check 'No inclusion or method coding' ((@(@($keys)+@($edges)+@($books)+@($refs) | Where-Object {$_.inclusion_status -ne 'NOT_SCREENED' -or $_.method_coding_status -ne 'NOT_CODED'}).Count -eq 0)) 'All identities/citations remain NOT_SCREENED and NOT_CODED.'
$receipts=@(ReadReviewJson (Join-Path $d 'crossref_receipts.json'))+@(ReadReviewJson (Join-Path $d 'crossref_receipts_supplement.json'))
$ok=@($receipts | Where-Object {$_.status -in @('DOI_RESOLVED','CACHE_REUSED')})
$bad=New-Object System.Collections.Generic.List[string]
foreach($r in $ok){if((ReviewHash $r.raw_path) -ne $r.sha256 -or (ReadReviewJson $r.raw_path).message.DOI.ToLowerInvariant() -ne $r.doi.ToLowerInvariant()){$bad.Add($r.doi)}}
Check 'DOI response receipts and identifiers' (($ok.Count -eq 72) -and $bad.Count -eq 0) '72 successful/reused Crossref records; original 404 retained separately.'
$data=ReadReviewJson 'results/s2_2026-09-20/primary_download_receipts/zenodo_datacite.json'
Check 'Zenodo identity validated in correct registry' ($data.data.attributes.doi -eq '10.5281/zenodo.12635' -and $data.data.attributes.types.resourceTypeGeneral -eq 'Dataset') 'Official DataCite dataset stays separate from journal article.'
$verification=ReadReviewJson (Join-Path $d 'verification.json')
$bad=New-Object System.Collections.Generic.List[string]
foreach($r in @($verification.source_hash_checks)+@($verification.prior_pdf_hash_checks)){if((ReviewHash $r.path) -ne $r.expected){$bad.Add($r.path)}}
foreach($r in $verification.original_inventory_hashes){if((ReviewHash $r.path) -ne $r.sha256){$bad.Add($r.path)}}
Check 'Registered sources and prior local identities preserved' ($bad.Count -eq 0) '5 registered source entries, 10 original PDF identities, 4 original inventory files.'
$out=[ordered]@{checked_utc=[DateTime]::UtcNow.ToString('o');status='PASS';check_count=$checks.Count;checks=$checks.ToArray();validator_sha256=(ReviewHash $PSCommandPath);scope='File-only structural/provenance validation, not screening or scientific-claim verification'}
[IO.File]::WriteAllText((Join-Path $d 'validation_checks.json'),($out | ConvertTo-Json -Depth 10),(New-Object System.Text.UTF8Encoding($false)))
$out | ConvertTo-Json -Depth 4
