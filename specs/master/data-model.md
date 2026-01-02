# Data Model for Docusaurus Book Architecture

## Documentation Entity Model

### Book (Root Entity)
- **name**: String - Title of the book ("Physical AI & Humanoid Robotics: AI Systems in the Physical World")
- **version**: String - Current version of the book
- **modules**: Array<BookModule> - The four core modules of the book
- **metadata**: Object - Additional book-level metadata (author, date, etc.)
- **navigation**: NavigationTree - Hierarchical navigation structure

### BookModule
- **id**: String - Unique identifier for the module (e.g., "ros2-humanoid", "digital-twin")
- **title**: String - Display title of the module
- **description**: String - Brief description of the module content
- **chapters**: Array<Chapter> - Chapters within this module
- **prerequisites**: Array<String> - Other modules/chapters that should be read first
- **learningObjectives**: Array<String> - What readers will learn from this module
- **duration**: Number - Estimated time to complete the module (in minutes)

### Chapter
- **id**: String - Unique identifier for the chapter
- **title**: String - Display title of the chapter
- **position**: Number - Sequential position within the module (1-3)
- **type**: ChapterType - Enum: "introduction", "advanced-concepts", "practical-implementation"
- **content**: String - Path to the content file (MD/MDX)
- **learningObjectives**: Array<String> - Specific learning objectives for the chapter
- **prerequisites**: Array<String> - Prerequisite knowledge or chapters
- **examples**: Array<Example> - Code examples or practical demonstrations
- **diagrams**: Array<Diagram> - Visual representations and system architectures
- **exercises**: Array<Exercise> - Practice problems or implementation tasks

### ChapterType (Enum)
- **introduction**: Foundational concepts and basic understanding
- **advanced-concepts**: Deeper technical details and complex topics
- **practical-implementation**: Hands-on examples and real-world applications

### Example
- **id**: String - Unique identifier for the example
- **title**: String - Brief description of the example
- **type**: ExampleType - Enum: "code-snippet", "configuration", "implementation"
- **content**: String - The actual example content (code or configuration)
- **language**: String - Programming language or configuration format
- **explanation**: String - Explanation of the example's purpose and functionality
- **relatedConcepts**: Array<String> - Concepts this example demonstrates

### ExampleType (Enum)
- **code-snippet**: Code example in a specific programming language
- **configuration**: Configuration file or settings example
- **implementation**: Complete implementation example

### Diagram
- **id**: String - Unique identifier for the diagram
- **title**: String - Brief description of the diagram
- **type**: DiagramType - Enum: "architecture", "workflow", "component", "process"
- **source**: String - Path to diagram file or description
- **description**: String - Explanation of what the diagram represents
- **relatedConcepts**: Array<String> - Concepts this diagram illustrates

### DiagramType (Enum)
- **architecture**: System architecture or component relationships
- **workflow**: Process flow or sequence of operations
- **component**: Internal structure of a component or system
- **process**: Step-by-step process or algorithm

### Exercise
- **id**: String - Unique identifier for the exercise
- **title**: String - Brief description of the exercise
- **difficulty**: DifficultyLevel - Enum: "beginner", "intermediate", "advanced"
- **instructions**: String - What the reader needs to do
- **expectedOutcome**: String - What the reader should achieve
- **hints**: Array<String> - Optional hints for completing the exercise
- **solution**: String - Reference solution (optional, may be hidden)

### DifficultyLevel (Enum)
- **beginner**: Basic understanding, minimal prerequisites
- **intermediate**: Moderate complexity, some prerequisites
- **advanced**: Complex concepts, multiple prerequisites

### GlossaryTerm
- **term**: String - The term being defined
- **definition**: String - Clear, concise definition
- **module**: String - Module where this term is most relevant
- **relatedTerms**: Array<String> - Other terms related to this concept
- **examples**: Array<String> - Examples of how the term is used

### NavigationItem
- **id**: String - Unique identifier for the navigation item
- **title**: String - Display text for the navigation item
- **path**: String - URL path to the content
- **children**: Array<NavigationItem> - Sub-items under this navigation item
- **sidebarPosition**: Number - Position in sidebar ordering
- **type**: NavigationType - Enum: "module", "chapter", "section", "reference"

### NavigationType (Enum)
- **module**: Top-level module in the book
- **chapter**: Chapter within a module
- **section**: Section within a chapter
- **reference**: Reference material (glossary, FAQ, etc.)

## Relationships

### Book contains Modules
- **Cardinality**: One-to-Many (1 Book contains 4 Modules)
- **Relationship**: Book "modules" → Module
- **Description**: Each book contains multiple modules that form the core content structure

### Module contains Chapters
- **Cardinality**: One-to-Many (1 Module contains 3 Chapters)
- **Relationship**: Module "chapters" → Chapter
- **Description**: Each module is divided into three chapters with progressive complexity

### Chapter contains Examples, Diagrams, and Exercises
- **Cardinality**: One-to-Many (1 Chapter contains multiple Examples/Diagrams/Exercises)
- **Relationship**: Chapter "examples/diagrams/exercises" → Example/Diagram/Exercise
- **Description**: Each chapter includes supporting materials for enhanced learning

### Cross-references
- **Related Concepts**: Chapters and modules reference related concepts across the book
- **Prerequisites**: Establish dependency relationships between content pieces
- **Navigation**: Connect related content through sidebar and internal linking

## Validation Rules

### Content Validation
- Each module must have exactly 3 chapters (introduction, advanced, practical)
- Each chapter must have a unique position within its module (1-3)
- All paths in navigation must correspond to actual content files
- Glossary terms must be referenced in at least one chapter

### Structural Validation
- Navigation hierarchy must match content hierarchy
- Module prerequisites must form an acyclic dependency graph
- All cross-references must point to valid content
- Content files must follow MD/MDX format with proper frontmatter

### Quality Validation
- All examples must be syntactically correct
- Diagram descriptions must be comprehensive
- Exercises must have achievable expected outcomes
- Learning objectives must be measurable and specific

## State Transitions (Documentation Lifecycle)

### Draft → Review → Approved → Published
- **Draft**: Initial content creation stage
- **Review**: Peer review and validation stage
- **Approved**: Content meets all standards and requirements
- **Published**: Content is available in the live documentation

## Implementation Notes

### Docusaurus-Specific Considerations
- Frontmatter in MD/MDX files will include metadata for the data model
- Sidebar configuration will reflect the navigation structure
- Component integration will support interactive examples
- Search indexing will include all content entities