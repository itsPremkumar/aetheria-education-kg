# Architecture — Aetheria Education Knowledge Graph

Offline-first education knowledge graph: concept extraction, relation mapping,
learning-path planning, quiz generation, and persistence — no network required.

## 1. System overview

```
                    ┌──────────────────────────────────────────┐
                    │              Interfaces                  │
                    │   cli.py        api.py        __main__.py│
                    └───────┬──────────────────────────────────┘
                            │
                    ┌───────▼──────────────────────────────────┐
                    │               Pipeline                    │
                    │  text → entities → relations → graph     │
                    └───────┬──────────────────────────────────┘
                            │
   ┌────────────────────────▼───────────────────────────────┐
   │                    Core graph layer                    │
   │                                                        │
   │   graph.KnowledgeGraph  ── in-memory graph + queries   │
   │   models.*              ── Concept / Relation /       │
   │                           LearningPath / Quiz /        │
   │                           Resource                     │
   │   seed_data             ── CS-curriculum starter KG     │
   └───────┬───────────────────────────────┬───────────────┘
           │                               │
┌──────────▼──────────┐        ┌──────────▼───────────────┐
│  Extraction layer    │        │   Consumer layer          │
│  entity_extractor    │        │  learning_path           │
│  relation_extractor  │        │  quiz_generator           │
│  multilang           │        │  reasoning / reasoning_   │
└──────────────────────┘        │  engine                  │
                                └──────────┬───────────────┘
                                           │
                                ┌──────────▼───────────────┐
                                │    storage.GraphStorage   │
                                │    SQLite + JSON import/ │
                                │    export                │
                                └──────────────────────────┘
```

## 2. Module responsibilities

| Module | Responsibility |
|---|---|
| `education_kg/models.py` | Dataclass domain model + enums (`ConceptDifficulty`, `RelationType`, `ResourceType`). Single source of truth for every persisted shape. |
| `education_kg/graph.py` | `KnowledgeGraph`: concept/relation/resource registry, BFS path finding, prerequisite queries, topological sort (Kahn), cycle detection. |
| `education_kg/entity_extractor.py` | Rule-based concept extraction from raw educational text. |
| `education_kg/relation_extractor.py` | Infers relations between extracted concepts. |
| `education_kg/learning_path.py` | `LearningPathGenerator`: start→goal paths, prerequisite closure, time estimation. |
| `education_kg/quiz_generator.py` | Auto-generates multiple-choice quizzes from graph concepts. |
| `education_kg/reasoning.py`, `reasoning_engine.py` | Graph-traversal question answering. |
| `education_kg/multilang.py` | Multi-language label support (10+ languages). |
| `education_kg/storage.py` | SQLite persistence (`concepts`, `relations`, `learning_paths`) + JSON import/export. |
| `education_kg/pipeline.py` | Orchestrates extraction → graph construction → downstream products. |
| `education_kg/seed_data.py` | `build_curriculum_graph()`: 20-concept CS-curriculum KG (32 relations, 15 resources) usable as a demo or fixture. |
| `education_kg/cli.py` / `api.py` | CLI and REST surfaces. |

## 3. Data model

### Concept
```
id (PK) · name · description · difficulty ∈ {beginner, intermediate, advanced}
subject · tags[] · metadata{} · created_at
```

### Relation
```
source_id → target_id · relation_type · weight · metadata{}
```

Relation types:
- **prerequisite** — target cannot be learned before source (drives learning paths)
- **builds_on** — softer dependency (affects ordering weight)
- **related_to** — topical cross-link (no ordering constraint)
- **part_of** — containment (course → module → concept)
- **leads_to** — outcome/progression link
- **same_as** — alias/equivalence between concepts
- **example_of** — instance → general concept
- **assessed_by** — concept → quiz/assessment artifact

### Resource
```
id (PK) · title · url · resource_type ∈ {video, article, book, exercise, course, interactive}
concepts[] · estimated_minutes · metadata{}
```
Resources attach to concepts by id reference; the graph exposes
`get_resources_for_concept()` for material recommendations.

### LearningPath / Quiz
Ordered concept id lists with metadata (hours, difficulty); Quiz adds
generated `QuizQuestion`s with options, answer index, and explanation.

## 4. Key algorithms

- **Path finding** — BFS over directed relation edges (`find_path`), bounded by depth.
- **Topological sort** — Kahn's algorithm over the `prerequisite` subgraph only.
  If the prerequisite subgraph is cyclic, cyclic nodes are omitted so the
  acyclic remainder still orders; callers can check `has_prerequisite_cycle()`
  or retrieve the offending loops with `find_prerequisite_cycles()` (DFS,
  gray/black coloring).
- **Learning path generation** — direct BFS path, then indirect path search
  via intermediate hubs; prerequisite closure via recursive expansion; time
  estimated at 2h per concept.
- **Search** — weighted scoring: phrase-in-name (10) > phrase-in-description (5)
  > word-level hits, with subject/difficulty filters, capped by `limit`.

## 5. Persistence flow

```
KnowledgeGraph ──save──▶ SQLite (GraphStorage) ──load──▶ KnowledgeGraph
      │
      └──export_json / import_json──▶ JSON (portable snapshots)
```

`GraphStorage` is the only module that touches disk state; everything above it
is pure in-memory, which keeps the core testable and the storage swappable.

## 6. Testing strategy

- `tests/` mirrors the module layout one-to-one (`test_graph.py` ↔ `graph.py`).
- New behavioral suites:
  - `test_seed_data.py` — dataset integrity (counts, no orphans, no self-loops,
    topo order validity, end-to-end path generation)
  - `test_cycles.py` — cycle detection + topological-sort robustness (the
    unhappy path: self-loops, disjoint cycles, dangling relation targets)
  - `test_resources.py` — resource model + registry semantics
- Run: `pytest tests/ -v` — 193 tests (145 pre-existing + 48 added).

## 7. Design decisions

| Decision | Rationale |
|---|---|
| Enum-driven relation vocabulary | Validates relation types at the boundary; new types (e.g. `same_as`, `assessed_by`) extend the enum without breaking stored data (values are strings). |
| Prerequisite-only topological sort | `related_to`/`same_as` links are non-semantic for ordering; sorting over all edges would produce false ordering constraints. |
| Cycle detection as first-class API | Learning-path generation silently degrades on cyclic prerequisites; exposing `has_prerequisite_cycle()` lets callers (CLI, API, importers) reject bad graphs early instead of shipping broken paths. |
| In-memory core + optional SQLite | Fast graph algorithms with zero disk dependency (offline-first); persistence is a bolt-on, so the core stays testable and embeddable. |
| Seed dataset as code | A checked-in curriculum KG doubles as documentation, demo material, and a realistic test fixture — no external data dependency. |
| Resources keyed by concept reference lists | Many-to-many without a join table in memory; SQLite persistence remains unchanged. |

## 8. Extension points

- **More relation types** — add to `RelationType`; existing values persist fine.
- **Resource persistence** — `GraphStorage` has no `resources` table yet; add
  `CREATE TABLE resources` + save/load mirroring the concepts pattern.
- **Extraction quality** — `entity_extractor` is rule-based; a statistical or
  embedding-based extractor can slot behind the same `extract()` interface.
- **API surface** — `api.py` can expose `/resources`, `/cycles`, and
  `/curriculum` (seed) endpoints using the new graph methods.
