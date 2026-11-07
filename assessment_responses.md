# Assessment Responses
## Task 2: Agentic AI / Workflow AI

### Agentic AI

I think of agentic AI as a system that can work toward a goal over several steps. It can interpret the request, decide what action to take, use an approved tool, check the result, and decide whether it needs another step or a person’s input. The important part is not simply that it uses a language model; it is that it can take actions. In an engineering setting, those actions should have clear limits, traceable inputs, and a human review point before anything safety-critical is accepted.

### Workflow AI

Workflow AI applies AI within a defined process rather than leaving it as a separate chat experience. A workflow might collect design inputs, check required fields, run a calculation, summarize the result, and route an exception to an engineer. Some steps can be ordinary software rules and some can use AI. I would keep deterministic checks and engineering calculations in conventional code wherever possible, and use AI for tasks such as interpreting a request or explaining results.

### AI copilots / assistants

A copilot helps a person do their work by answering questions, drafting content, or suggesting next steps in the context of a task. The user remains in control and decides what to accept. That is different from an agent that may carry out a sequence of actions on its own. For engineering work, I would want the copilot to show where its answer came from and make it easy to check or correct.

### Standalone model vs. AI integrated into a product workflow

A standalone model takes an input and returns an output. A product integration also has to fit the user's actual process: it needs the right project data, permissions, units, validation, error handling, history, and a clear way to review or undo actions. The model's score matters, but so do latency, reliability, traceability, and what happens when the model is uncertain. In a thermal product, the AI should support the engineering calculation rather than quietly replace it.

### Relevant experience or learning approach

My experience with GenAI and AI workflows is developing, and I would describe myself as having deployed a production RAG system or autonomous agent. I understand the basic and Advance pieces: a language model, retrieved source material when answers need grounding, tools or APIs for actions, and workflow controls around permissions and review. This assessment has been a useful way to connect a thermal calculation with a parameter sweep, a surrogate model, and checks on its results. To build further experience, I would start with a small, measurable use case, use approved data, compare against a non-AI baseline, test failure cases, and ask domain experts to review the results before expanding it.


## Task 3: AI Use Case Evaluation

### 1. AI-assisted input validation and missing-parameter detection

- **Problem solved:** Catch unit errors, implausible values, and missing required inputs before running a thermal calculation.
- **Data required:** Input schemas, units, engineering limits, dependency rules, and reviewed examples of valid and invalid configurations.
- **Approach:** Deterministic validation rules for known constraints, with workflow AI to request missing information; ML only if historical data supports anomaly ranking.
- **Validation:** Unit tests for boundaries and units, a reviewed set of invalid cases, and checks that uncertain inputs are flagged for user confirmation rather than silently changed.

### 2. ML surrogate for rapid thermal prediction

- **Problem solved:** Provide fast approximate results during design exploration when repeated high-fidelity simulations are expensive.
- **Data required:** Inputs paired with trusted simulation or measured outputs, including geometry, materials, loads, boundary conditions, and solver metadata.
- **Approach:** Supervised ML with explicit applicability-range and uncertainty checks, combined with the existing solver for final verification.
- **Validation:** Grouped holdouts by geometry or operating condition, MAE/RMSE/R², physical trend checks, uncertainty calibration, and comparison against the trusted solver on new cases.

### 3. Grounded result explanation and report generation

- **Problem solved:** Reduce time spent interpreting results and assembling design-review reports.
- **Data required:** Validated solver outputs, input assumptions, units, approved report templates, and traceable engineering references.
- **Approach:** GenAI workflow that summarizes structured results and cites the calculation inputs and retrieved source passages; calculations remain in deterministic engineering code.
- **Validation:** Verify generated numbers against solver outputs, require citations for factual claims, test with edge cases, and require engineer approval before release.

### 4. Engineering knowledge retrieval

- **Problem solved:** Help engineers locate relevant equations, material properties, design rules, and prior decisions across technical documents.
- **Data required:** Versioned engineering manuals, datasheets, internal standards, metadata, access permissions, and source provenance.
- **Approach:** Retrieval-augmented generation with document indexing, permission-aware retrieval, and answers linked to source pages; use workflow AI to route unresolved questions to an engineer.
- **Validation:** Curated question/answer set, source attribution and retrieval-recall checks, permission tests, freshness/version checks, and expert review of high-impact answers.

## Task 4: Motivation and Ownership

### Why Expert Thermal / XThermal?

I am interested in Expert Thermal / XThermal because the work connects thermal engineering with software and AI in a practical way. I find that combination compelling: the product has to respect the underlying physics, but it can also make analysis faster and easier to use. I would like to contribute to tools where engineers can understand and verify what the software is telling them, rather than receiving a prediction without context.

### What are you most interested in building in AI/ML?

I am most interested in useful engineering tools: surrogate models that make design exploration faster, and assistants that help engineers work with inputs, calculations, and technical references. I would measure success by whether the feature saves time without making the result harder to trust. That means testing it against the existing calculation process and being clear about where it should not be used.

### Preferred focus: ML, GenAI workflows, physics-aware AI, or product AI integration

My strongest interest is product AI integration, especially physics-aware ML within an engineering workflow. A model is valuable only if it fits the way engineers work and has sensible checks around its output. I would like to build a mix of ML and workflow features, while keeping established physics calculations as the reference for verification.

### Handling ambiguous requirements

I first separate what is known from what is assumed, then identify which uncertainty could change the result or create the greatest risk. I would clarify those points with the relevant stakeholder, document any temporary assumptions, and build the smallest testable version before expanding scope. In this assessment, the starter script and reference PDF differ on some thermal assumptions. The responsible approach is to expose that difference, preserve a clear source of truth for the calculation, and avoid presenting the result as more certain than the inputs support.

### Comfort with a fast-moving startup

I am comfortable with a fast-moving environment when priorities and risks are discussed openly. I can adapt as a team learns more, and I would aim to keep progress visible through small deliverables, clear notes, and early communication when a decision or dependency is blocking the work. Moving quickly should still include enough testing for the impact of the feature.

### How you expect to grow on the team

I would like to deepen my understanding of thermal engineering workflows while becoming more effective at building reliable ML and AI features. I would start by learning the existing models, data, and customer use cases from the people closest to them. Over time, I would aim to own a feature from problem definition through validation, release, and follow-up improvements.

### Ownership, initiative, and increasing responsibility

I would look for recurring friction in the engineering workflow, check that it is a real problem with users, and propose a small solution that can be tested. I would define how we will measure whether it helped, share progress and risks early, and take responsibility for documentation and follow-up as well as implementation. As I build trust and context, I would take on broader pieces of work and help improve the team's standards for testing and reviewing AI-assisted results.
