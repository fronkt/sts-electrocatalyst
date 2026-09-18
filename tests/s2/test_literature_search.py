"""P-LIT pagination, completeness, immutable cache and candidate identity contracts."""
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from s2.literature import search


def oa(rows, count, cursor):
    return json.dumps(dict(results=rows, meta=dict(count=count, next_cursor=cursor))).encode(), {}


def item(i, doi=None, title=None):
    return dict(id=f"https://openalex.org/W{i}", doi=doi, display_name=title or f"Record {i}",
                publication_year=2020, publication_date="2020-01-02", type="article",
                authorships=[dict(author=dict(display_name="A Scientist"))])


def test_literal_query_and_date_window_preserved():
    for database in search.DATABASES:
        for q in search.QUERIES:
            params = search.params_for(database, q, "next+/=")
            assert params["search" if database == "openalex" else "query.bibliographic"] == q
            assert search.START in params["filter"] and search.END in params["filter"]
            assert params["cursor"] == "next+/="


def test_resumed_pagination_and_doi_dedup_preserve_conflicts(tmp_path):
    calls = []
    pages = {"*": oa([item(1, "https://doi.org/10.123/x", "First title")], 2, "next"),
             "next": oa([item(2, "10.123/X", "Second title")], 2, None)}

    def fetch(database, params):
        calls.append(params["cursor"])
        return pages[params["cursor"]]

    db = search.connect_index(tmp_path / "index.sqlite")
    first = search.walk("openalex", 1, tmp_path, db, discover=True, fetch=fetch, sleep=lambda _: None)
    assert first["status"] == "INCOMPLETE" and first["returned_records"] == 1
    final = search.walk("openalex", 1, tmp_path, db, fetch=fetch, sleep=lambda _: None)
    assert final["status"] == "COMPLETE_API_ENUMERATION" and calls == ["*", "next"]
    exported = search.export_candidates(db, tmp_path)
    assert exported["candidates"] == 1 and exported["source_occurrences"] == 2
    record = json.loads((tmp_path / "candidates.jsonl").read_text(encoding="utf-8"))
    assert record["conflicting_metadata"]["title"] == ["First title", "Second title"]
    assert len(record["source_occurrences"]) == 2
    assert record["method_coding_status"] == "NOT_CODED" and record["inclusion_status"] == "NOT_SCREENED"
    db.close()


def test_repeated_page_and_count_drift_stay_unresolved(tmp_path):
    db = search.connect_index(tmp_path / "index.sqlite")
    repeated = lambda database, params: oa([item(1)], 3, "same-token")
    status = search.walk("openalex", 1, tmp_path, db, fetch=repeated, sleep=lambda _: None)
    assert status["status"] == "INCOMPLETE" and status["termination"] == "REPEATED_PAGE_WITHOUT_PROGRESS"
    assert status["returned_records"] == status["indexed_source_records"] == 2
    assert status["unique_provider_identifiers"] == 1 and status["duplicate_source_records"] == 1
    drift = search.walk("openalex", 2, tmp_path, db, fetch=lambda d, p: oa([item(1)], 3, None), sleep=lambda _: None)
    assert drift["status"] == "ENUMERATED_WITH_COUNT_DRIFT"
    db.close()


def test_same_cursor_with_progress_is_allowed(tmp_path):
    db = search.connect_index(tmp_path / "index.sqlite")
    pages = iter([oa([item(1)], 3, "token"), oa([item(2)], 3, "token"), oa([item(3)], 3, None)])
    status = search.walk("openalex", 1, tmp_path, db, fetch=lambda d, p: next(pages), sleep=lambda _: None)
    assert status["status"] == "COMPLETE_API_ENUMERATION" and status["returned_records"] == 3
    db.close()


def test_cached_page_mutation_fails_without_redownload(tmp_path):
    params = search.params_for("openalex", search.QUERIES[0], "*")
    record = search.fetch_page("openalex", params, tmp_path, 1, fetch=lambda d, p: oa([item(1)], 1, None))
    record["raw_path"].write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError, match="hash mismatch"):
        search.fetch_page("openalex", params, tmp_path, 1, fetch=lambda *_: pytest.fail("cache must not be replaced"))


def test_crossref_last_page_and_exact_full_terminal_page():
    short = dict(message={"items": [{"DOI": "10.123/x"}], "total-results": 1, "next-cursor": "still-returned"})
    assert search.unpack("crossref", short)[3]
    full = dict(message={"items": [{}] * 1000, "total-results": 1000})
    assert search.unpack("crossref", full)[3]


def test_missing_doi_fallback_does_not_collapse_missing_identity():
    a = item(1, title="Rutile: OER")
    b = item(2, title="RUTILE OER")
    ka = search.candidate_key(search.metadata("openalex", a), "openalex", a)
    kb = search.candidate_key(search.metadata("openalex", b), "openalex", b)
    assert ka == kb
    a["authorships"] = b["authorships"] = []
    assert search.candidate_key(search.metadata("openalex", a), "openalex", a)[0] != \
        search.candidate_key(search.metadata("openalex", b), "openalex", b)[0]


def test_crossref_online_and_print_dates_both_preserved():
    row = dict(DOI="10.123/X", title=["Study"], author=[dict(given="Ada", family="Scientist")],
               **{"published-online": {"date-parts": [[2010, 12, 30]]}, "published-print": {"date-parts": [[2011, 3]]}})
    meta = search.metadata("crossref", row)
    assert meta["publication_year"] == 2010
    assert meta["publication_dates"] == {"published-online": [[2010, 12, 30]], "published-print": [[2011, 3]]}


def test_malformed_response_bodies_and_failure_status_are_preserved(tmp_path):
    db = search.connect_index(tmp_path / "index.sqlite")
    status = search.walk("openalex", 1, tmp_path, db, fetch=lambda d, p: (b'{"invalid": true}', {}), sleep=lambda _: None)
    assert status["status"] == "INCOMPLETE" and status["termination"] == "REQUEST_OR_CACHE_FAILURE"
    directory = tmp_path / "raw/openalex/q01"
    assert len(list(directory.glob("*.error.txt"))) == 6
    assert len((directory / "failures.jsonl").read_text(encoding="utf-8").splitlines()) == 6
    db.close()


def test_duplicate_provider_id_is_not_hidden_by_total_count_agreement(tmp_path):
    db = search.connect_index(tmp_path / "index.sqlite")
    pages = iter([oa([item(1, title="Before metadata update")], 2, "next"),
                  oa([item(1, title="After metadata update")], 2, None)])
    status = search.walk("openalex", 1, tmp_path, db, fetch=lambda d, p: next(pages), sleep=lambda _: None)
    assert status["returned_records"] == 2 and status["reported_totals"] == [2]
    assert status["unique_provider_identifiers"] == 1 and status["duplicate_source_records"] == 1
    assert status["duplicate_provider_identifiers"] == [dict(identity="https://openalex.org/W1", occurrences=2)]
    assert status["status"] == "ENUMERATED_WITH_DUPLICATES"
    db.close()


def test_resume_refuses_changed_query_parameters(tmp_path):
    params = search.params_for("openalex", search.QUERIES[0], "*")
    search.fetch_page("openalex", params, tmp_path, 1, fetch=lambda d, p: oa([item(1)], 1, None))
    changed = dict(params, search="a different query")
    with pytest.raises(ValueError, match="request or byte hash mismatch"):
        search.fetch_page("openalex", changed, tmp_path, 1, fetch=lambda *_: pytest.fail("must not redownload"))


def test_amended_cache_copy_preserves_original_and_rejects_tampering(tmp_path):
    source, out = tmp_path / "original", tmp_path / "amended"
    source.mkdir()
    search.write_json(source / "search_spec.json", dict(queries=list(search.QUERIES), date_window=[search.START, search.END]))
    params = search.params_for("openalex", search.QUERIES[0], "*")
    search.fetch_page("openalex", params, source / "raw/openalex/q01", 1, fetch=lambda d, p: oa([item(1)], 1, None))
    before = {p.relative_to(source).as_posix(): p.read_bytes() for p in source.rglob("*") if p.is_file()}
    proof = search.reuse_openalex_cache(source, out)
    assert len(proof["copied_pages"]) == 1
    assert before == {p.relative_to(source).as_posix(): p.read_bytes() for p in source.rglob("*") if p.is_file()}
    assert (out / "raw/openalex/q01/page_000001.json").read_bytes() == before["raw/openalex/q01/page_000001.json"]
    (source / "raw/openalex/q01/page_000001.json").write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError, match="byte hash mismatch"):
        search.reuse_openalex_cache(source, tmp_path / "rejected")


def test_amended_run_completeness_uses_four_openalex_streams(tmp_path, monkeypatch):
    def fake_walk(database, index, out, db, discover, delay):
        assert database == "openalex"
        state = dict(database=database, query_index=index, status="COMPLETE_API_ENUMERATION")
        search.write_json(out / "raw" / database / f"q{index:02d}" / "status.json", state)
        return state

    monkeypatch.setattr(search, "walk", fake_walk)
    result = search.run(tmp_path, databases=("openalex",), amended=True)
    assert result["database_search_complete"] and len(result["streams"]) == 4
    assert not result["inclusion_list_frozen"] and result["methods_coded"] == 0
    assert result["amended_protocol"] and result["discovery_databases"] == ["openalex"]
    assert result["pipeline_status"] == "SOURCE_UNCHANGED"
    assert result["pipeline_sha256"] == result["pipeline_end_sha256"] == search.LOADED_SOURCE_SHA256
    with pytest.raises(ValueError, match="reserved for DOI validation"):
        search.run(tmp_path / "invalid", databases=("crossref",), amended=True)


def test_missing_provider_identity_preserves_rows_without_claiming_completeness(tmp_path):
    db = search.connect_index(tmp_path / "index.sqlite")
    first, second = item(1, title="Before metadata update"), item(1, title="After metadata update")
    first.pop("id")
    second["id"] = "not-an-openalex-work-id"
    status = search.walk("openalex", 1, tmp_path, db,
                         fetch=lambda d, p: oa([first, second], 2, None), sleep=lambda _: None)
    assert status["returned_records"] == status["indexed_source_records"] == 2
    assert status["unique_provider_identifiers"] == status["duplicate_source_records"] == 0
    assert status["unresolved_provider_identity_records"] == 2
    assert status["status"] == "ENUMERATED_WITH_UNRESOLVED_IDENTITIES"
    assert search.export_candidates(db, tmp_path)["source_occurrences"] == 2
    db.close()


def test_output_lock_refuses_concurrent_writer_and_releases_after_failure(tmp_path):
    with pytest.raises(ValueError, match="worker failed"):
        with search.output_lock(tmp_path):
            owner = (tmp_path / ".search.lock").read_bytes()
            with pytest.raises(RuntimeError, match="search output is locked"):
                search.run(tmp_path, databases=(), query_indices=())
            assert (tmp_path / ".search.lock").read_bytes() == owner
            raise ValueError("worker failed")
    assert not (tmp_path / ".search.lock").exists()
    with search.output_lock(tmp_path):
        assert (tmp_path / ".search.lock").exists()


def test_pipeline_source_change_since_import_refuses_start(tmp_path, monkeypatch):
    original = search.file_sha
    monkeypatch.setattr(search, "file_sha", lambda path: "changed" if path == search.SOURCE_PATH else original(path))
    with pytest.raises(RuntimeError, match="source changed since import"):
        search.run(tmp_path, databases=(), query_indices=())
    assert not (tmp_path / "search_spec.json").exists()
    assert not (tmp_path / ".search.lock").exists()


def test_pipeline_source_change_during_run_keeps_start_hash_and_blocks_complete(tmp_path, monkeypatch):
    changed = False
    original = search.file_sha

    def file_sha(path):
        return "changed" if changed and path == search.SOURCE_PATH else original(path)

    def fake_walk(database, index, out, db, discover, delay):
        nonlocal changed
        changed = True
        state = dict(database=database, query_index=index, status="COMPLETE_API_ENUMERATION")
        search.write_json(out / "raw" / database / f"q{index:02d}" / "status.json", state)
        return state

    monkeypatch.setattr(search, "file_sha", file_sha)
    monkeypatch.setattr(search, "walk", fake_walk)
    with pytest.raises(RuntimeError, match="source changed during retrieval"):
        search.run(tmp_path, databases=("openalex",), amended=True)
    result = json.loads((tmp_path / "search_readout.json").read_text(encoding="utf-8"))
    spec = json.loads((tmp_path / "search_spec.json").read_text(encoding="utf-8"))
    assert not result["database_search_complete"]
    assert result["pipeline_status"] == "SOURCE_CHANGED_DURING_RUN"
    assert result["pipeline_sha256"] == spec["pipeline_sha256"] == search.LOADED_SOURCE_SHA256
    assert result["pipeline_end_sha256"] == "changed"
    assert not (tmp_path / ".search.lock").exists()


def test_resume_refuses_changed_pipeline_revision(tmp_path):
    search.run(tmp_path, databases=(), query_indices=())
    spec_path = tmp_path / "search_spec.json"
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    spec["pipeline_sha256"] = "a different source revision"
    search.write_json(spec_path, spec)
    with pytest.raises(ValueError, match="specification differs"):
        search.run(tmp_path, databases=(), query_indices=())
    assert not (tmp_path / ".search.lock").exists()


def test_missing_openalex_continuation_key_is_preserved_as_failure(tmp_path):
    db = search.connect_index(tmp_path / "index.sqlite")
    raw = json.dumps(dict(results=[item(1)], meta=dict(count=1))).encode()
    status = search.walk("openalex", 1, tmp_path, db, fetch=lambda d, p: (raw, {}), sleep=lambda _: None)
    assert status["status"] == "INCOMPLETE" and status["termination"] == "REQUEST_OR_CACHE_FAILURE"
    evidence = list((tmp_path / "raw/openalex/q01").glob("*.error.txt"))
    assert len(evidence) == 6 and all(path.read_bytes() == raw for path in evidence)
    db.close()
