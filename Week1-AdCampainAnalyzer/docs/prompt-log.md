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

## Post-implementation prompts and iterations

| Prompt or issue reported | How it influenced the project |
|---|---|
| While trying to run the application, `pip` reports: `ERROR: No matching distribution found for pandas==2.2.3`. | Identified that the active Python environment was too old for the pinned dependencies. The setup guidance now requires Python 3.11 or later and directs the user to create a fresh virtual environment before installing `requirements.txt`. The dependency versions remained pinned for reproducibility. |
| The date range goes back to January 1 after selecting a different start date. | Revealed that Streamlit temporarily returns a one-date tuple while a range selection is in progress. Filter-state reconciliation was updated to preserve that intermediate date, and regression tests were added at both the filter and Streamlit AppTest layers. |
| Generate another campaign CSV for testing, with six months of data. | Added `data/test_campaigns_april_september.csv`, a deterministic upload-ready dataset with 1,464 daily rows from April 1 through September 30, 2026, eight campaigns, and equal coverage across the four platforms. |
| Merge the completed work back to `main` locally. | Fast-forwarded the completed feature branch into local `main`, verified the merged history, and removed the no-longer-needed isolated worktree. |
| Rename the project directory to `Week1-AdCampainAnalyzer`. | Renamed the tracked project directory and updated repository documentation, mockup instructions, the implementation plan, and path references to use the requested name. |
| Loading an uploaded campaign CSV produces `[Errno 2] No such file or directory`. | The error was traced to a Streamlit process that was still running from the removed worktree after the directory rename. Restarting Streamlit from `Week1-AdCampainAnalyzer` restored uploads without requiring an application-code change. |
| Upload the project to GitHub and publish it as-is. | Created the public `melepatt/Week1-AdCampainAnalyzer` repository, completed GitHub's device authorization flow, configured `origin`, pushed the full commit history to `main`, and verified that the local and remote branch tips matched. |
| Update the project documentation to reflect everything that changed after it was generated. | Updated `project-documentation.md` with the six-month dataset, final validation and filter fixes, merge and rename steps, stale-server diagnosis, verification evidence, and GitHub links. Setup commands in the project README were also corrected for the renamed directory. |
| Update `prompt-log.md` with details added since it was originally generated. | Triggered this reconciliation of the prompt history with the final repository history and submission documentation so the class deliverable records the complete AI-assisted workflow. |

Short confirmation prompts such as “generate it,” “authorized,” and “go for it” are consolidated into the related workflow entries above rather than recorded as separate decisions.
