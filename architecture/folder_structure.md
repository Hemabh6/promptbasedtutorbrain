# Folder Structure

| Path | Owns | Must not contain |
| --- | --- | --- |
| `docs/` | product rules and service contracts | provider SDK instructions |
| `prompts/` | portable reasoning contracts | secrets or durable state |
| `schemas/` | machine-validated data shapes | business logic hidden in prose |
| `architecture/` | boundaries and engineering constraints | feature-specific tutorial text |
| `workflows/` | trigger-to-outcome operational flows | undocumented data fields |
| `adr/` | accepted architectural decisions | transient implementation notes |

File names are stable public references. Numbered documents express reading order, not runtime dependency. Add a folder only when it owns a distinct artifact type with a documented lifecycle; otherwise extend the closest existing area.
