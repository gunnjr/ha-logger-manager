### Purpose
This issue contains a comprehensive guide on how to automate release management and documentation, using GitHub Actions, milestones, issues, and VS Code extensions. It serves as a living document to onboard developers or contributors to best practices.

---

### Release Management Guide

#### Steps to Automate Releases with GitHub Actions:
1. **Create a Workflow File**:
   - Path: `.github/workflows/release.yml`
   - Example Workflow:
     ```yaml
     name: Release Management

     on:
       push:
         branches:
           - main  # Trigger on changes to the main branch

     jobs:
       release:
         runs-on: ubuntu-latest

         steps:
           - name: Checkout Code
             uses: actions/checkout@v3

           - name: Set up Node.js
             uses: actions/setup-node@v3
             with:
               node-version: '18'

           - name: Create a Release Draft
             uses: release-drafter/release-drafter@v5
     ```

2. **Customize Release Drafter Config**:
   - Path: `.github/release-drafter.yml`
   - Example Config:
     ```yaml
     name-template: 'v$NEXT_PATCH_VERSION'
     tag-template: 'v$NEXT_PATCH_VERSION'
     categories:
       - title: 🚀 Features
         labels:
           - enhancement
           - feature
       - title: 🐛 Bug Fixes
         labels:
           - bug
     ```
   - This config organizes release notes by categories like features and bug fixes.

#### Drafting Release Notes
- Tools like `release-drafter` or GitHub's native release notes generator can automatically summarize changes.
- Write clear PR titles and descriptions.
- Use meaningful commit messages (`feat:`, `fix:`, `chore:`).

---

### Issues and Milestones for Release Planning

#### Issues
1. **Labels**:
   - Use descriptive labels like:
     - `bug`
     - `feature`
     - `documentation`
     - `chore`

2. **Descriptive Issues**:
   - Example:
     ```markdown
     Title: Add user authentication
     Description:
     Implement OAuth2.0 for secure user login.

     **Acceptance Criteria**
     - User can log in using Google.
     - Session expiration is handled gracefully.
     ```

3. **Linking Issues to PRs**:
   - Use keywords in PR descriptions (e.g., `Fixes #<issue-number>` or `Closes #<issue-number>`).

#### Milestones
1. **Create Milestones**:
   - From the **Issues** tab, go to **Milestones** → **New Milestone**.
   - Example: `v1.0`
   - Description: `Focus on core features like authentication and profile management.`
2. **Organize Issues by Milestone**:
   - Open an issue → Select milestone in the right sidebar.
3. **Track Progress**:
   - View open/closed issues and overall milestone progress.

---

### Helpful Extensions and Tools

#### VS Code Extensions
1. **GitLens**:
   - Track commits, authors, and changes.
   - Install: [GitLens Extension](https://marketplace.visualstudio.com/items?itemName=eamodio.gitlens).

2. **Markdown All in One**:
   - Simplify editing README files and changelogs.
   - Install: [Markdown All in One](https://marketplace.visualstudio.com/items?itemName=yzhang.markdown-all-in-one).

3. **REST Client** (Optional):
   - Test GitHub API calls directly in VS Code.
   - Install: [REST Client](https://marketplace.visualstudio.com/items?itemName=humao.rest-client).

#### CLI Tools
1. **GitHub CLI (`gh`)**:
   - Install: [GitHub CLI](https://github.com/cli/cli).
   - Example Commands:
     ```bash
     gh release view
     gh release create v1.0.0 --title "Version 1.0.0" --notes "Initial release with authentication and profiles."
     ```

2. **npm & `semantic-release`** (Optional):
   - Use for managing changelogs and automating versioning.
   - Install:
     ```bash
     npm install --save-dev semantic-release @semantic-release/changelog @semantic-release/github
     ```

---

### References
- [GitHub Releases Guide](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases)
- [Release Drafter GitHub Action](https://github.com/release-drafter/release-drafter)
- [Semantic Versioning](https://semver.org/)
- [GitHub CLI Documentation](https://cli.github.com/manual/)