# Aetheria Education — Learning Assistant Knowledge Graph

An offline-first education knowledge graph with concept dependency mapping, learning path generation, quiz generation, and multi-language support.

## Features

- **Entity Extraction**: Extract educational concepts from text
- **Relation Extraction**: Identify relationships between concepts
- **Knowledge Graph**: Store and query concept relationships
- **Cycle Detection**: Detect and locate prerequisite cycles in the graph
- **Learning Resources**: Attach books, videos, and exercises to concepts
- **Seed Curriculum**: Built-in 20-concept CS curriculum graph (`build_curriculum_graph()`)
- **Reasoning Engine**: Answer questions using graph traversal
- **Learning Path Generation**: Create personalized learning paths
- **Quiz Generation**: Auto-generate quizzes from knowledge graph
- **Multi-Language Support**: 10+ languages
- **Offline-First**: No internet required
- **CLI + API**: Command-line and REST API interfaces

## Quick Start

```bash
pip install -r requirements.txt
python -m education_kg cli
```

## API

```bash
python -m education_kg api --port 8000
```

## Tests

```bash
pytest tests/ -v
```

193 tests across 17 test files.

## Architecture

See [docs/architecture.md](docs/architecture.md) for the full system design,
data model, algorithms, and extension points.

## Quick example

```python
from education_kg import build_curriculum_graph, LearningPathGenerator

graph = build_curriculum_graph()
print(graph.get_statistics())

# Check curriculum integrity
assert not graph.has_prerequisite_cycle()

# Plan a study route: propositional logic → NLP
path = LearningPathGenerator(graph).generate("math.logic", "ai.nlp")
print(path.concepts, path.estimated_hours)
```

## License

MIT
