# Architecture Design for GCP and RAG Corpus

## Overview

This document describes the architecture for organizing educational content (Grades 1-12) by education board, grade level, and subject using **Option 1: One Bucket Per Board** approach. It covers both Google Cloud Platform (GCP) storage structure and Vertex AI RAG corpus organization.

## Architecture Principles

1. **One GCS bucket per education board** - Each board has its own dedicated storage bucket
2. **Folder structure in GCS** - Files organized by `grade-{N}/{subject}/` paths
3. **One RAG corpus per board-grade-subject combination** - Granular corpus structure for precise search
4. **Flat corpus structure** - RAG corpora don't have folders, but preserve source paths via `source_uri`

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface (ADK)                     │
│              Natural Language Commands & Queries            │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              Agent Development Kit (ADK)                     │
│         Orchestrates tools and user interactions            │
└──────────────┬───────────────────────────┬──────────────────┘
               │                           │
               ▼                           ▼
    ┌──────────────────────┐    ┌──────────────────────┐
    │   Storage Tools      │    │   Corpus Tools        │
    │  (GCS Management)    │    │  (RAG Management)     │
    └──────────┬───────────┘    └──────────┬───────────┘
               │                           │
               ▼                           ▼
┌──────────────────────────────┐  ┌──────────────────────────────┐
│   Google Cloud Storage       │  │   Vertex AI RAG Engine        │
│   (File Storage)             │  │   (Semantic Search)           │
│                              │  │                              │
│  Bucket Structure:           │  │  Corpus Structure:           │
│  ┌─────────────────────┐    │  │  ┌─────────────────────┐    │
│  │ adk-cbse-education  │    │  │  │ cbse-grade-1-math   │    │
│  │ adk-icse-education  │    │  │  │ cbse-grade-1-science│    │
│  │ adk-state-education │    │  │  │ cbse-grade-5-math   │    │
│  └─────────────────────┘    │  │  │ ... (one per combo) │    │
│                              │  │  └─────────────────────┘    │
└──────────────────────────────┘  └──────────────────────────────┘
```

## GCS Bucket Structure

### Bucket Naming Convention

```
Format: adk-{board}-education

Examples:
- adk-cbse-education
- adk-icse-education
- adk-state-education
- adk-igcse-education
- adk-ib-education
```

### File Organization Within Buckets

```
gs://adk-cbse-education/
├── grade-1/
│   ├── mathematics/
│   │   ├── chapter-1.pdf
│   │   ├── chapter-2.pdf
│   │   └── workbook.pdf
│   ├── science/
│   │   ├── unit-1.pdf
│   │   └── unit-2.pdf
│   ├── english/
│   │   ├── lesson-1.pdf
│   │   └── lesson-2.pdf
│   ├── social-studies/
│   │   └── chapter-1.pdf
│   ├── hindi/
│   │   └── lesson-1.pdf
│   └── evs/
│       └── unit-1.pdf
├── grade-2/
│   ├── mathematics/
│   ├── science/
│   └── ...
├── grade-5/
│   ├── mathematics/
│   │   ├── chapter-1.pdf
│   │   ├── chapter-2.pdf
│   │   └── chapter-3.pdf
│   └── science/
│       └── unit-1.pdf
├── ...
└── grade-12/
    ├── mathematics/
    ├── physics/
    ├── chemistry/
    ├── biology/
    └── computer-science/
```

### Path Format

```
gs://{bucket-name}/grade-{N}/{subject}/{filename}

Examples:
- gs://adk-cbse-education/grade-1/mathematics/chapter-1.pdf
- gs://adk-cbse-education/grade-5/science/unit-3.pdf
- gs://adk-icse-education/grade-10/english/lesson-5.pdf
```

## RAG Corpus Structure

### Corpus Naming Convention

```
Format: {board}-grade-{N}-{subject}

Examples:
- cbse-grade-1-mathematics
- cbse-grade-5-science
- icse-grade-10-english
- state-grade-12-physics
```

### Corpus Organization

```
RAG Corpora (Flat Structure - No Folders)
├── cbse-grade-1-mathematics
│   ├── File: chapter-1.pdf
│   │   └── source_uri: gs://adk-cbse-education/grade-1/mathematics/chapter-1.pdf
│   ├── File: chapter-2.pdf
│   │   └── source_uri: gs://adk-cbse-education/grade-1/mathematics/chapter-2.pdf
│   └── File: workbook.pdf
│       └── source_uri: gs://adk-cbse-education/grade-1/mathematics/workbook.pdf
│
├── cbse-grade-1-science
│   ├── File: unit-1.pdf
│   │   └── source_uri: gs://adk-cbse-education/grade-1/science/unit-1.pdf
│   └── File: unit-2.pdf
│       └── source_uri: gs://adk-cbse-education/grade-1/science/unit-2.pdf
│
├── cbse-grade-5-mathematics
│   ├── File: chapter-1.pdf
│   ├── File: chapter-2.pdf
│   └── File: chapter-3.pdf
│
└── ... (one corpus per board-grade-subject combination)
```

### Important Notes

1. **No Folder Structure in Corpora**: RAG corpora are flat collections of files
2. **Source URI Preservation**: Each file maintains its original GCS path in the `source_uri` field
3. **One Corpus Per Combination**: Each board-grade-subject has its own corpus
4. **All Files from GCS Path**: All files from `gs://{bucket}/grade-{N}/{subject}/` go into `{board}-grade-{N}-{subject}` corpus

## Mapping: GCS → RAG Corpus

### One-to-One Mapping

```
GCS Path Pattern:                    RAG Corpus:
─────────────────────────────────────────────────────────────
gs://adk-cbse-education/              cbse-grade-1-mathematics
  grade-1/mathematics/*.pdf

gs://adk-cbse-education/              cbse-grade-1-science
  grade-1/science/*.pdf

gs://adk-cbse-education/               cbse-grade-5-mathematics
  grade-5/mathematics/*.pdf

gs://adk-icse-education/              icse-grade-10-english
  grade-10/english/*.pdf
```

### Complete Example: CBSE Grade 5 Mathematics

```
┌─────────────────────────────────────────────────────────────┐
│ GCS Bucket: adk-cbse-education                               │
│                                                              │
│ Path: grade-5/mathematics/                                  │
│ ├── chapter-1-addition.pdf                                  │
│ ├── chapter-2-subtraction.pdf                               │
│ ├── chapter-3-multiplication.pdf                            │
│ └── workbook.pdf                                            │
└─────────────────────────────────────────────────────────────┘
                        │
                        │ Import all files
                        ▼
┌─────────────────────────────────────────────────────────────┐
│ RAG Corpus: cbse-grade-5-mathematics                        │
│                                                              │
│ Files (Flat List):                                           │
│ ├── chapter-1-addition.pdf                                  │
│ │   source_uri: gs://adk-cbse-education/grade-5/            │
│ │              mathematics/chapter-1-addition.pdf             │
│ ├── chapter-2-subtraction.pdf                                │
│ │   source_uri: gs://adk-cbse-education/grade-5/            │
│ │              mathematics/chapter-2-subtraction.pdf        │
│ ├── chapter-3-multiplication.pdf                            │
│ │   source_uri: gs://adk-cbse-education/grade-5/            │
│ │              mathematics/chapter-3-multiplication.pdf       │
│ └── workbook.pdf                                             │
│     source_uri: gs://adk-cbse-education/grade-5/            │
│                mathematics/workbook.pdf                      │
└─────────────────────────────────────────────────────────────┘
```

## Complete Architecture by Board

### CBSE Board Structure

```
GCS Bucket: adk-cbse-education
│
├── grade-1/
│   ├── mathematics/ → Corpus: cbse-grade-1-mathematics
│   ├── science/ → Corpus: cbse-grade-1-science
│   ├── english/ → Corpus: cbse-grade-1-english
│   ├── social-studies/ → Corpus: cbse-grade-1-social-studies
│   ├── hindi/ → Corpus: cbse-grade-1-hindi
│   └── evs/ → Corpus: cbse-grade-1-evs
│
├── grade-2/
│   └── ... (same subjects)
│
├── grade-5/
│   ├── mathematics/ → Corpus: cbse-grade-5-mathematics
│   ├── science/ → Corpus: cbse-grade-5-science
│   └── ... (same subjects)
│
├── grade-10/
│   ├── mathematics/ → Corpus: cbse-grade-10-mathematics
│   ├── science/ → Corpus: cbse-grade-10-science
│   └── ... (same subjects)
│
└── grade-12/
    ├── mathematics/ → Corpus: cbse-grade-12-mathematics
    ├── physics/ → Corpus: cbse-grade-12-physics
    ├── chemistry/ → Corpus: cbse-grade-12-chemistry
    └── biology/ → Corpus: cbse-grade-12-biology
```

### Multiple Boards Structure

```
┌─────────────────────────────────────────────────────────────┐
│                    Education System                           │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│ CBSE Board    │    │ ICSE Board    │    │ State Board   │
│               │    │               │    │               │
│ Bucket:       │    │ Bucket:       │    │ Bucket:       │
│ adk-cbse-     │    │ adk-icse-     │    │ adk-state-    │
│ education     │    │ education     │    │ education     │
│               │    │               │    │               │
│ Corpora:      │    │ Corpora:      │    │ Corpora:      │
│ cbse-grade-*  │    │ icse-grade-*  │    │ state-grade-* │
└───────────────┘    └───────────────┘    └───────────────┘
```

## Data Flow

### Setup Flow

```
1. Create GCS Bucket
   └─> "Create bucket adk-cbse-education"
       └─> Bucket created: gs://adk-cbse-education/

2. Upload Files to GCS
   └─> "Upload chapter-1.pdf to gs://adk-cbse-education/ 
        with destination grade-5/mathematics/chapter-1.pdf"
       └─> File stored: gs://adk-cbse-education/grade-5/mathematics/chapter-1.pdf

3. Create RAG Corpus
   └─> "Create corpus cbse-grade-5-mathematics"
       └─> Corpus created: cbse-grade-5-mathematics

4. Import Files to Corpus
   └─> "Import gs://adk-cbse-education/grade-5/mathematics/chapter-1.pdf 
        into corpus cbse-grade-5-mathematics"
       └─> File imported with source_uri preserved
```

### Query Flow

```
1. User Query
   └─> "What is photosynthesis?"
       │
       ▼
2. Agent Decision
   └─> Use search_all_corpora tool
       │
       ▼
3. Search All Corpora
   └─> Query each corpus:
       ├─> cbse-grade-5-science
       ├─> cbse-grade-6-science
       ├─> icse-grade-7-science
       └─> ... (all science corpora)
       │
       ▼
4. Aggregate Results
   └─> Combine results from all relevant corpora
       │
       ▼
5. Return with Citations
   └─> Results with citations:
       "[Source: CBSE Grade 5 Science (cbse-grade-5-science)]"
```

## Search Behavior

### 1. Search All Corpora (Default)

```
Query: "What is multiplication?"
Action: search_all_corpora(query_text="What is multiplication?")
Result: Searches ALL corpora across all boards, grades, subjects
Output: Results from relevant corpora with citations
```

### 2. Search Specific Corpus

```
Query: "Explain fractions" in corpus cbse-grade-5-mathematics
Action: query_rag_corpus(corpus_id="cbse-grade-5-mathematics", 
                          query_text="Explain fractions")
Result: Searches only cbse-grade-5-mathematics corpus
Output: Results from that specific corpus only
```

### 3. Search Pattern (Conceptual - Future Enhancement)

```
Query: "Math question for grade 5"
Action: Filter corpora matching pattern: *-grade-5-mathematics
Result: Searches all grade 5 math corpora across all boards
Output: Results from cbse-grade-5-mathematics, icse-grade-5-mathematics, etc.
```

## Corpus Count Estimation

### Example Calculation

For **CBSE board** with:
- 12 grades (1-12)
- Average 6 subjects per grade
- **Total: 12 × 6 = 72 corpora**

For **5 education boards**:
- CBSE: 72 corpora
- ICSE: 72 corpora
- State: 72 corpora
- IGCSE: 72 corpora
- IB: 72 corpora
- **Total: 5 × 72 = 360 corpora**

### Subject Variation by Grade

```
Primary (1-5):     6 subjects × 5 grades = 30 corpora per board
Middle (6-8):      6 subjects × 3 grades = 18 corpora per board
Secondary (9-10):  7 subjects × 2 grades = 14 corpora per board
Higher (11-12):    6 subjects × 2 grades = 12 corpora per board
─────────────────────────────────────────────────────────────
Total:             74 corpora per board (varies by subject count)
```

## Benefits of This Architecture

### 1. **Clear Organization**
- Each board has its own bucket
- Files organized by grade and subject in GCS
- Corpora organized by board-grade-subject

### 2. **Granular Search**
- Can search specific grade/subject
- Can search across all content
- Can filter by board if needed

### 3. **Scalability**
- Easy to add new boards (new bucket)
- Easy to add new grades (new folders)
- Easy to add new subjects (new folders/corpora)

### 4. **Maintainability**
- Update one corpus without affecting others
- Clear mapping between GCS and RAG
- Source paths preserved for reference

### 5. **Clear Citations**
- Results show board, grade, and subject
- Easy to identify source of information
- Helps students understand context

## File Naming Best Practices

### GCS File Paths

```
✅ Good:
grade-5/mathematics/chapter-1.pdf
grade-5/mathematics/chapter-2.pdf
grade-5/mathematics/workbook.pdf

❌ Avoid:
grade-5/math/ch1.pdf (inconsistent naming)
grade5/mathematics/chapter1.pdf (missing hyphen)
```

### Corpus Names

```
✅ Good:
cbse-grade-5-mathematics
icse-grade-10-science
state-grade-12-physics

❌ Avoid:
cbse_grade_5_math (use hyphens, not underscores)
CBSE-Grade-5-Math (use lowercase)
cbse-5-math (include "grade" for clarity)
```

## Workflow Examples

### Complete Setup for One Subject

```
1. Create Bucket:
   → "Create GCS bucket adk-cbse-education"

2. Upload Files:
   → "Upload chapter-1.pdf to gs://adk-cbse-education/ 
      with destination grade-5/mathematics/chapter-1.pdf"
   → "Upload chapter-2.pdf to gs://adk-cbse-education/ 
      with destination grade-5/mathematics/chapter-2.pdf"

3. Create Corpus:
   → "Create RAG corpus cbse-grade-5-mathematics 
      with description 'CBSE - Grade 5 - Mathematics'"

4. Import Files:
   → "Import gs://adk-cbse-education/grade-5/mathematics/chapter-1.pdf 
      into corpus cbse-grade-5-mathematics"
   → "Import gs://adk-cbse-education/grade-5/mathematics/chapter-2.pdf 
      into corpus cbse-grade-5-mathematics"
```

### Query Examples

```
Query 1: "What is photosynthesis?"
→ Searches all corpora
→ Returns results from science corpora across all grades
→ Citations: [Source: CBSE Grade 5 Science (cbse-grade-5-science)]

Query 2: "Explain fractions for grade 5"
→ Searches all corpora (or can filter to grade-5 math corpora)
→ Returns results from grade 5 mathematics corpora
→ Citations: [Source: CBSE Grade 5 Mathematics (cbse-grade-5-mathematics)]

Query 3: "What is the water cycle?" in cbse-grade-5-science
→ Searches only cbse-grade-5-science corpus
→ Returns results from that specific corpus
```

## Summary

**Option 1: One Bucket Per Board** provides:

- ✅ **Organized Storage**: One bucket per education board
- ✅ **Clear Structure**: Grade and subject folders in GCS
- ✅ **Granular Corpora**: One corpus per board-grade-subject
- ✅ **Preserved Paths**: Source URIs maintain GCS structure
- ✅ **Flexible Search**: Search all or filter by corpus
- ✅ **Scalable Design**: Easy to expand with new content

This architecture balances organization, searchability, and maintainability for educational content across multiple boards, grades, and subjects.

