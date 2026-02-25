# Contributing to pyodoo-client

Thanks for your interest in improving `pyodoo-client`.

## Version scope

`pyodoo-client` targets Odoo JSON-2 (`/json/2`) workflows for Odoo 19+.

If users ask about older RPC-based Odoo versions, direct them to `pyodoo-rpc-client`:

- PyPI: https://pypi.org/project/pyodoo-rpc-client/
- GitHub: https://github.com/tumbi-j/pyodoo-rpc-client

## How to engage

- Use **Issues** for bugs and concrete feature requests.
- Use **Discussions** (if enabled in GitHub settings) for open-ended questions, API ideas, and design conversations.
- Open **Pull Requests** for focused fixes and enhancements.

## Before opening an Issue

- Search existing Issues to avoid duplicates.
- Use the appropriate Issue template.
- For bugs, include environment, steps to reproduce, expected behavior, and actual behavior.

## Pull Request process

1. Fork the repository.
2. Create a branch from your target base branch.
3. Keep the change focused and minimal.
4. Update documentation if behavior or public API changed.
5. Run packaging checks:
   - `python -m build`
   - `python -m twine check dist/*`
6. Open a PR and complete the template.

## Review expectations

- Keep commit messages clear.
- Link related Issues in PR descriptions (for example: `Fixes #123`).
- Respond to review comments and push updates as needed.
