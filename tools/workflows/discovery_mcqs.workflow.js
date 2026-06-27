export const meta = {
  name: 'discovery-mcqs',
  description: 'Domain-assign + write & verify 2-3 MCQs for each approved 2025-2026 discovered article',
  phases: [{ title: 'Write' }, { title: 'Verify' }],
}
// Constants baked in (args proved unreliable). Shards live in tools/shards/discovery/.
const SHARDS = 11
const SHARDDIR = 'tools/shards/discovery'
const OUTPREFIX = 'disc_batch'

const LEAN_SCHEMA = {
  type: 'object',
  required: ['records'],
  properties: {
    records: {
      type: 'array',
      items: {
        type: 'object',
        required: ['idx', 'domain', 'subdomain_page', 'authors', 'journal', 'mcqs'],
        properties: {
          idx: { type: 'integer' },
          domain: { type: 'string' },
          subdomain_page: { type: 'string' },
          authors: { type: 'string' },
          journal: { type: 'string' },
          mcqs: {
            type: 'array',
            items: {
              type: 'object', required: ['q', 'o', 'a', 'e'],
              properties: { q: { type: 'string' }, o: { type: 'array', items: { type: 'string' } }, a: { type: 'integer' }, e: { type: 'string' } }
            }
          }
        }
      }
    }
  }
}

const ids = []
for (let i = 0; i < SHARDS; i++) ids.push(i)
log(`${SHARDS} shards from ${SHARDDIR}`)

const results = await pipeline(
  ids,
  (i) => agent(
    `Read \`${SHARDDIR}/shard_${i}.json\` — a JSON array of shelter-medicine journal articles, each with idx, title, authors, journal, year, abstract, key_points, suggested_domain, suggested_page.
For EACH article emit one object:
- idx: copy the article's idx UNCHANGED.
- domain + subdomain_page: START from suggested_domain/suggested_page, but CORRECT from the abstract if clearly mis-routed. subdomain_page MUST be an existing file under /Users/jxue/abvp-study (the valid pages are the *.html files in physical-health/, shelter-management/, behavioral-health/, companion-animal-homelessness/, community-public-health/, animals-public-policy/, research-biostats/ — ls if unsure).
- authors: clean the author list. If the source 'authors' looks like "Lastname, Journalname" (journal is empty), separate the people from the journal — put the journal name in 'journal'.
- journal: the journal name (from source, or recovered from a combined authors field).
- mcqs: write 2-3 CLOSED-BOOK, conclusion-focused MCQs answerable from the ABSTRACT ALONE. Each: stem 'q', exactly 4 options 'o', integer answer index 'a' (0-3), one-sentence rationale 'e'. Terse exam-prep style. Vary the correct-answer position.
Do NOT echo the abstract or title back. Return {records:[...]} with exactly one object per source article.`,
    { label: `write:shard${i}`, phase: 'Write', schema: LEAN_SCHEMA }
  ),
  (written, i) => agent(
    `Adversarially verify these ${written?.records?.length || 0} lean MCQ records (JSON below) for shard ${i}. The source articles are in \`${SHARDDIR}/shard_${i}.json\` (match by idx to read each abstract). For EACH MCQ confirm: (1) answer index 'a' is correct, (2) answerable from THAT article's abstract alone, (3) exactly 4 options, none ambiguous or duplicated, (4) rationale 'e' matches the keyed answer. FIX problems in place. Confirm every 'subdomain_page' is an existing file under /Users/jxue/abvp-study. Keep each 'idx' unchanged. Then WRITE the corrected JSON array to \`tools/qa_fixes/${OUTPREFIX}_${i}.json\` using your Write tool, and return {written:<count>, file:"tools/qa_fixes/${OUTPREFIX}_${i}.json"}.\n\nRECORDS:\n${JSON.stringify(written?.records || [])}`,
    {
      label: `verify:shard${i}`, phase: 'Verify',
      schema: { type: 'object', required: ['written', 'file'], properties: { written: { type: 'integer' }, file: { type: 'string' } } }
    }
  )
)

const ok = results.filter(Boolean)
log(`discovery MCQ workflow: ${ok.length}/${SHARDS} shards wrote partials`)
return { shards: SHARDS, partials: ok }
