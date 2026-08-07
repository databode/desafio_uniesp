# 001 — Source / Ingestion

Status: Implemented

## Context
Fonte oficial: `servidores-2026.csv`, `utf-8-sig`, delimitador `;`, 267.189 linhas, duas competências (`202601`, `202602`).

## Objective
Preservar a fonte em Raw sem transformação de conteúdo e registrar metadados.

## Requirements
- Receber caminho via `SOURCE_FILE_PATH`.
- Copiar para `data/raw/servidores/servidores-2026.csv`, preservando o arquivo físico recebido.
- Não particionar Raw por `ano_mes`; particionamento pode aparecer depois em Bronze/Silver/Gold se houver regra analítica.
- Capturar filename, size, checksum, timestamp e row count.
- Ser reexecutável de forma determinística.

## Non-goals
API pública, autenticação, particionamento físico por mês antes de preservar a fonte.

## Inputs
CSV fonte configurado.

## Outputs
Raw CSV copiado e `data/metadata/raw_servidores.json`.

## Processing rules
Não alterar conteúdo do CSV.

## Acceptance criteria
Raw existe, checksum registrado, row count registrado.

## Tests
Integration pipeline fixture and real smoke test.

## Assumptions
A fonte usa header esperado.

## Open questions
Origem/proveniência oficial do arquivo.

## Implementation
- `src/uniesp_data_platform/pipeline.py::materialize_raw`
- `src/uniesp_data_platform/assets/ingestion.py`
