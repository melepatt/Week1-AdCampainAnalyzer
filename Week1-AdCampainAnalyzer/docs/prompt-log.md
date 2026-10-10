# Prompt Log

Date: October 10, 2026

| Prompt or decision | How it influenced the project |
|---|---|
| Build an Ad Campaign Performance Analyzer for a class using Streamlit, pandas, and Plotly, with Overview, Platform Comparison, Campaign Details, and Time Series views. | Established the product goal, required stack, views, filters, validation, and documentation deliverables. |
| Use Superpowers to elaborate the assignment into a detailed specification for later implementation. | Produced the architecture, data contract, formulas, UI behavior, testing strategy, and acceptance checklist. |
| Define a recommended schema. | Established the 11-column daily campaign schema and explicit types and validation rules. |
| Support `revenue` and optionally accept `conversion_value` as a fallback. | Prompted a schema discussion about attributed value. |
| What is `conversion_value`? | Clarified that it can mean attributed monetary value but varies by source. |
| Remove `conversion_value` to simplify things. | Finalized `revenue` as required and removed fallback behavior from the spec and implementation. |
| Share the updated design and plan. | Consolidated the approved design, global constraints, task sequence, and test expectations. |
| Develop and save GUI mockups for project documentation. | Created the reusable HTML mockup, capture script, images, and mockup README under `docs/mockups/`. |
| Start building and validate the full application; generate appropriate tests. | Expanded the implementation plan around testable modules and release checks. |
| Commit the design and mockups to Git. | Preserved approved project artifacts in separate documentation commits. |
| The plan looks good. Start execution following the Native approach. | Triggered task-by-task execution in an isolated feature worktree with RED–GREEN tests, task commits, and fresh verification. |

Implementation prompts were intentionally based on the approved specification and plan rather than generated ad hoc. Test failures caused by not-yet-created modules were expected RED steps, not production bugs.
