# Journal Catalog Record Schema

Each record in `journal-catalog.json` is a JSON object with the following fields.

## Required fields

| Field             | Type           | Description |
|-------------------|----------------|-------------|
| `id`              | string         | Unique slug, e.g. `"smith-2023-cpv-vaccination"` |
| `title`           | string         | Full article title |
| `authors`         | string         | Author list, e.g. `"Smith J, Jones A"` |
| `journal`         | string         | Journal name |
| `year`            | integer        | Publication year; must be 2021–2026 |
| `citation`        | string         | Full citation string |
| `doi`             | string         | DOI (may be empty string `""` if unavailable) |
| `source`          | string         | How the article was found: `"folder"` or `"discovered"` |
| `abstract`        | string         | Full abstract text (non-empty) |
| `abstract_origin` | string         | Where the abstract text came from, e.g. `"pubmed"`, `"pdf"`, `"manual"` |
| `domain`          | string         | ABVP exam domain name, e.g. `"Physical Health of Animal"` |
| `subdomain_page`  | string         | Relative path to the hub page this article belongs to, e.g. `"physical-health/surgery_anesthesia_hub.html"`. Must exist under the repo root. |
| `mcqs`            | array of MCQs  | List of multiple-choice questions (may be `[]` while MCQs are pending) |

## MCQ object

Each element of `mcqs` is a JSON object:

| Field | Type    | Description |
|-------|---------|-------------|
| `q`   | string  | Question stem (non-empty) |
| `o`   | array   | Exactly 4 option strings |
| `a`   | integer | Index of the correct option (0–3) |
| `e`   | string  | Explanation / rationale (non-empty) |

## Validation rules (enforced by `lib_catalog.validate_record`)

- All fields listed above must be present.
- `year` must be an integer in the range 2021–2026 (inclusive).
- `source` must be exactly `"folder"` or `"discovered"`.
- `subdomain_page` must resolve to an existing file under the repo root.
- `abstract` must be a non-empty string.
- Each MCQ must have `q`, `o`, `a`, `e`; `len(o) == 4`; `0 <= a <= 3`; `q` and `e` non-empty.
- `doi` may be an empty string — it is not validated further.
- An empty `mcqs` list (`[]`) is valid.
