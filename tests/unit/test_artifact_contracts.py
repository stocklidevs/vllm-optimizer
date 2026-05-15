from vllm_optimizer.artifact_contracts import build_artifact_contract_catalog, render_contract_markdown


def test_artifact_contract_catalog_lists_release_facing_contracts() -> None:
    catalog = build_artifact_contract_catalog()

    assert catalog["schema_version"] == "1.0"
    assert catalog["tool_version"]
    contracts = {contract["artifact_type"]: contract for contract in catalog["contracts"]}
    assert {"canonical-report", "execution-status", "knob-group-catalog", "pipeline-control-manifest"} <= set(
        contracts
    )

    canonical = contracts["canonical-report"]
    assert canonical["artifact_schema_version"] == "1.0"
    assert canonical["producer_command"] == "canonical-report"
    assert {"schema_version", "recommendation", "objectives", "candidates", "provenance"} <= set(
        canonical["required_fields"]
    )
    assert "report-viewer" in canonical["consumers"]


def test_contract_markdown_contains_one_section_per_contract() -> None:
    catalog = build_artifact_contract_catalog()
    markdown = render_contract_markdown(catalog)

    assert markdown.startswith("# vLLM Optimizer Artifact Contracts")
    for contract in catalog["contracts"]:
        assert f"## {contract['artifact_type']}" in markdown
        assert f"- Producer: `{contract['producer_command']}`" in markdown
