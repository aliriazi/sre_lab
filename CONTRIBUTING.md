Contributing
============

Thanks for your interest in contributing to this lab repository. The goal is to keep the project small, well-documented, and reproducible.

How to contribute
-----------------
- Fork the repository and create a feature branch: `git checkout -b feat/my-change`
- Make small, focused commits with clear messages.
- Run linters/tests locally before opening a PR.
- Open a pull request describing the change and why it's needed.

Branching & PRs
----------------
- Use descriptive branch names: `feat/`, `fix/`, `docs/`.
- Target the `main` branch unless the PR is for a long-lived topic branch.
- Add reviewers and link related issues in the PR description.

Coding style
------------
- Keep YAML tidy and consistent (2-space indentation).
- Prefer declarative Helm values or kustomize overlays for environment differences.
- Include small README updates for new features or changes to workflow.

Tests & CI
----------
- CI may run YAML linting, `helm template`, and optional `kind` smoke tests.
- Add tests or smoke scripts under `scripts/` when appropriate.

Issues
------
- Use Issues for bugs, feature requests, or questions.
- Tag issues with `bug`, `enhancement`, or `question`.

License & Code of Conduct
-------------------------
- By contributing, you agree that your contributions will be licensed under the project's `LICENSE`.

Contact
-------
- For questions, open an issue or add a comment on an existing PR.
