# Aetheria Education — Learning Assistant Knowledge Graph

An offline-first education knowledge graph with concept dependency mapping, learning path generation, quiz generation, and multi-language support.

## Features

- **Entity Extraction**: Extract educational concepts from text
- **Relation Extraction**: Identify relationships between concepts
- **Knowledge Graph**: Store and query concept relationships
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

## License

MIT
