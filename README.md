# markdown-link-validator

This GitHub custom action, written in Python, allows users to validate the contents of a Markdown file in their repository during a pull request. It verifies the links within the file to ensure they are still working.

This action focus on accuracy and reliability, sacrificing speed for the sake of thoroughness. Instead of using regex it uses markdown parsing libraries to ensure that the links are valid. This avoid edge cases where a regex approach could struggle where links are not formatted as expected.

## Usage

To use the markdown-link-validator action, follow these steps:

1. Create a `.github/workflows/markdown-link-validator.yml` file in your repository.
2. Add the following code to the `markdown-link-validator.yml` file:

```yaml
name: Validate Markdown Links

on:
  pull_request:
    types: [opened, synchronize]

permissions:
  contents: read
  issues: write
  pull-requests: write

jobs:
  link-check:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v2

      # verify broken links in markdown files
      - name: Run Markdown Link Validator
        uses: rcbop/markdown-link-validator-action@v1

  check-style:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v2

      # verify markdown style
      - name: Run Mardown Lint and style check
        uses: markdownlint/markdown-lint-stylecheck@v1
        with:
          glob_pattern: '**/*.md' # default value
```

3. Commit and push the changes to your repository.

Now, whenever a pull request is opened or synchronized, the markdown-link-validator action will be triggered. It will validate the contents of the Markdown file and check the links for any errors. A comment will be added to the pull request with the results of the validation. The second step will verify the markdown style and structure.
