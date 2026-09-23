"""Seed dataset: a Computer Science curriculum knowledge graph.

Provides a ready-to-use KnowledgeGraph covering a full CS curriculum —
mathematical foundations, programming, systems, and AI — with concepts,
prerequisite relations, cross-links, and attached learning resources.

Usage:
    from education_kg.seed_data import build_curriculum_graph
    graph = build_curriculum_graph()
"""

from __future__ import annotations

from education_kg.graph import KnowledgeGraph
from education_kg.models import (
    Concept,
    ConceptDifficulty,
    Relation,
    RelationType,
    Resource,
    ResourceType,
)

# (id, name, difficulty, subject, tags, description)
_CONCEPTS: list[tuple[str, str, ConceptDifficulty, str, list[str], str]] = [
    # ── Mathematical foundations ─────────────────────────────────────
    ("math.logic", "Propositional Logic", ConceptDifficulty.BEGINNER, "mathematics",
     ["logic", "proofs"], "Truth tables, logical connectives, and boolean algebra."),
    ("math.sets", "Set Theory", ConceptDifficulty.BEGINNER, "mathematics",
     ["sets", "functions"], "Sets, relations, functions, and cardinality."),
    ("math.proofs", "Proof Techniques", ConceptDifficulty.INTERMEDIATE, "mathematics",
     ["proofs", "induction"], "Direct proof, contradiction, and mathematical induction."),
    ("math.combinatorics", "Combinatorics", ConceptDifficulty.INTERMEDIATE, "mathematics",
     ["counting", "probability"], "Permutations, combinations, and counting principles."),
    ("math.graphtheory", "Graph Theory", ConceptDifficulty.INTERMEDIATE, "mathematics",
     ["graphs", "networks"], "Vertices, edges, paths, trees, and graph coloring."),
    ("math.probability", "Probability Theory", ConceptDifficulty.INTERMEDIATE, "mathematics",
     ["probability", "statistics"], "Sample spaces, conditional probability, Bayes' rule."),
    ("math.linear", "Linear Algebra", ConceptDifficulty.INTERMEDIATE, "mathematics",
     ["vectors", "matrices"], "Vector spaces, matrices, eigenvalues, and decomposition."),
    ("math.calculus", "Calculus", ConceptDifficulty.INTERMEDIATE, "mathematics",
     ["derivatives", "integrals"], "Limits, derivatives, integrals, and series."),
    # ── Programming foundations ─────────────────────────────────────
    ("prog.basics", "Programming Fundamentals", ConceptDifficulty.BEGINNER, "programming",
     ["variables", "control-flow"], "Variables, conditionals, loops, and functions."),
    ("prog.oop", "Object-Oriented Programming", ConceptDifficulty.INTERMEDIATE, "programming",
     ["classes", "inheritance"], "Encapsulation, inheritance, polymorphism, and design."),
    ("prog.recursion", "Recursion", ConceptDifficulty.INTERMEDIATE, "programming",
     ["recursion", "stacks"], "Recursive decomposition and base cases."),
    ("prog.dsa", "Data Structures & Algorithms", ConceptDifficulty.ADVANCED, "programming",
     ["algorithms", "complexity"], "Lists, trees, hash maps, sorting, and searching."),
    ("prog.complexity", "Algorithmic Complexity", ConceptDifficulty.INTERMEDIATE, "programming",
     ["big-o", "analysis"], "Asymptotic analysis, Big-O, and amortized cost."),
    # ── Systems ─────────────────────────────────────────────────────
    ("sys.architecture", "Computer Architecture", ConceptDifficulty.INTERMEDIATE, "systems",
     ["cpu", "memory"], "CPU design, instruction sets, caches, and memory hierarchy."),
    ("sys.os", "Operating Systems", ConceptDifficulty.ADVANCED, "systems",
     ["processes", "scheduling"], "Processes, threads, virtual memory, and file systems."),
    ("sys.networks", "Computer Networks", ConceptDifficulty.ADVANCED, "systems",
     ["tcp-ip", "protocols"], "Layered protocols, TCP/IP, routing, and the web stack."),
    ("sys.databases", "Databases", ConceptDifficulty.ADVANCED, "systems",
     ["sql", "transactions"], "Relational model, SQL, normalization, and ACID."),
    # ── AI / ML ─────────────────────────────────────────────────────
    ("ai.ml", "Machine Learning", ConceptDifficulty.ADVANCED, "artificial-intelligence",
     ["ml", "regression"], "Supervised and unsupervised learning, model evaluation."),
    ("ai.dl", "Deep Learning", ConceptDifficulty.ADVANCED, "artificial-intelligence",
     ["neural-networks", "backpropagation"], "Neural networks, backpropagation, and training."),
    ("ai.nlp", "Natural Language Processing", ConceptDifficulty.ADVANCED, "artificial-intelligence",
     ["nlp", "transformers"], "Tokenization, embeddings, attention, and transformers."),
]

# (source, target, type, weight)
_RELATIONS: list[tuple[str, str, RelationType, float]] = [
    # prerequisites
    ("math.logic", "math.sets", RelationType.PREREQUISITE, 1.0),
    ("math.logic", "math.proofs", RelationType.PREREQUISITE, 1.0),
    ("math.sets", "math.proofs", RelationType.PREREQUISITE, 0.8),
    ("math.sets", "math.combinatorics", RelationType.PREREQUISITE, 1.0),
    ("math.sets", "math.graphtheory", RelationType.PREREQUISITE, 0.8),
    ("math.combinatorics", "math.probability", RelationType.PREREQUISITE, 1.0),
    ("math.linear", "ai.ml", RelationType.PREREQUISITE, 1.0),
    ("math.probability", "ai.ml", RelationType.PREREQUISITE, 1.0),
    ("math.calculus", "ai.dl", RelationType.PREREQUISITE, 0.8),
    ("math.linear", "ai.dl", RelationType.PREREQUISITE, 1.0),
    ("ai.ml", "ai.dl", RelationType.PREREQUISITE, 1.0),
    ("ai.dl", "ai.nlp", RelationType.PREREQUISITE, 1.0),
    ("prog.basics", "prog.oop", RelationType.PREREQUISITE, 1.0),
    ("prog.basics", "prog.recursion", RelationType.PREREQUISITE, 1.0),
    ("prog.recursion", "prog.dsa", RelationType.PREREQUISITE, 1.0),
    ("prog.oop", "prog.dsa", RelationType.PREREQUISITE, 0.7),
    ("prog.dsa", "prog.complexity", RelationType.PREREQUISITE, 0.9),
    ("math.proofs", "prog.complexity", RelationType.PREREQUISITE, 0.8),
    ("prog.complexity", "sys.databases", RelationType.PREREQUISITE, 0.5),
    ("prog.dsa", "sys.os", RelationType.PREREQUISITE, 0.6),
    ("prog.basics", "sys.architecture", RelationType.PREREQUISITE, 0.7),
    ("sys.architecture", "sys.os", RelationType.PREREQUISITE, 1.0),
    ("sys.os", "sys.networks", RelationType.PREREQUISITE, 0.6),
    ("prog.dsa", "ai.ml", RelationType.PREREQUISITE, 0.7),
    ("math.graphtheory", "ai.nlp", RelationType.PREREQUISITE, 0.4),
    # cross-links
    ("math.graphtheory", "sys.networks", RelationType.RELATEDTO, 0.6),
    ("prog.dsa", "ai.dl", RelationType.RELATEDTO, 0.5),
    ("math.linear", "math.probability", RelationType.RELATEDTO, 0.5),
    ("prog.oop", "sys.databases", RelationType.BUILDSON, 0.6),
    ("math.sets", "sys.databases", RelationType.RELATEDTO, 0.5),
    # part-of structure
    ("prog.basics", "prog.oop", RelationType.PARTOF, 0.3),
    ("ai.ml", "ai.dl", RelationType.PARTOF, 0.3),
]

# (id, title, type, minutes, concepts)
_RESOURCES: list[tuple[str, str, ResourceType, float, list[str]]] = [
    ("res.logic.intro", "Intro to Logic — interactive truth tables", ResourceType.INTERACTIVE, 45,
     ["math.logic"]),
    ("res.proofs.book", "How to Prove It (Velleman)", ResourceType.BOOK, 600,
     ["math.proofs", "math.sets"]),
    ("res.graphs.video", "Graph Theory — visual crash course", ResourceType.VIDEO, 90,
     ["math.graphtheory"]),
    ("res.probability.course", "Probability Fundamentals", ResourceType.COURSE, 480,
     ["math.probability", "math.combinatorics"]),
    ("res.linear.khan", "Linear Algebra (Khan Academy)", ResourceType.COURSE, 600,
     ["math.linear"]),
    ("res.prog.python", "Python for Everybody", ResourceType.COURSE, 720,
     ["prog.basics", "prog.oop"]),
    ("res.recursion.video", "Recursion explained visually", ResourceType.VIDEO, 30,
     ["prog.recursion"]),
    ("res.dsa.book", "Grokking Data Structures", ResourceType.BOOK, 900,
     ["prog.dsa"]),
    ("res.dsa.exercise", "Big-O practice problems", ResourceType.EXERCISE, 120,
     ["prog.complexity", "prog.dsa"]),
    ("res.os.book", "Operating Systems: Three Easy Pieces", ResourceType.BOOK, 1200,
     ["sys.os"]),
    ("res.net.course", "Computer Networking course", ResourceType.COURSE, 540,
     ["sys.networks"]),
    ("res.db.exercise", "SQL practice workbook", ResourceType.EXERCISE, 180,
     ["sys.databases"]),
    ("res.ml.course", "Machine Learning crash course", ResourceType.COURSE, 900,
     ["ai.ml"]),
    ("res.dl.video", "Neural networks — 3Blue1Brown series", ResourceType.VIDEO, 120,
     ["ai.dl", "ai.ml"]),
    ("res.nlp.article", "Transformers: an illustrated guide", ResourceType.ARTICLE, 60,
     ["ai.nlp"]),
]


def build_curriculum_graph() -> KnowledgeGraph:
    """Build the seeded CS-curriculum KnowledgeGraph (20 concepts,
    30 relations, 15 resources)."""
    graph = KnowledgeGraph()

    for cid, name, difficulty, subject, tags, description in _CONCEPTS:
        graph.add_concept(Concept(
            id=cid,
            name=name,
            description=description,
            difficulty=difficulty,
            subject=subject,
            tags=tags,
        ))

    for source, target, rel_type, weight in _RELATIONS:
        graph.add_relation(Relation(
            source_id=source,
            target_id=target,
            relation_type=rel_type,
            weight=weight,
        ))

    for rid, title, rtype, minutes, concepts in _RESOURCES:
        graph.add_resource(Resource(
            id=rid,
            title=title,
            resource_type=rtype,
            estimated_minutes=minutes,
            concepts=concepts,
        ))

    return graph


SEED_CONCEPT_COUNT = len(_CONCEPTS)
SEED_RELATION_COUNT = len(_RELATIONS)
SEED_RESOURCE_COUNT = len(_RESOURCES)
