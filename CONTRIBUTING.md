# Contributing

Contributions are welcome, and they are greatly appreciated! Every
little helps, and credit will always be given. 

You can contribute in many ways:

## Types of Contributions

### Report Bugs

Report bugs at https://github.com/thorgate/tg-react/issues.

If you are reporting a bug, please include:

* Your operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

### Fix Bugs

Look through the GitHub issues for bugs. Anything tagged with "bug"
is open to whoever wants to implement it.

### Implement Features

Look through the GitHub issues for features. Anything tagged with "feature"
is open to whoever wants to implement it.

### Write Documentation

tg-react could always use more documentation, whether as part of the 
official tg-react docs, in docstrings, or even on the web in blog posts,
articles, and such.

### Submit Feedback

The best way to send feedback is to file an issue at https://github.com/thorgate/tg-react/issues.

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that this is a volunteer-driven project, and that contributions
  are welcome :)

### Translate

Add a new locale using::

```shell
LOCALE='<locale>' poetry run make add-locale
```

This will create a new directory under `tg_react/locale/<locale>` and a django.po file inside it. First edit the comments and the PO file
header of the generated file (use tg_react/locale/en/LC_MESSAGES/django.po for refrence) and then use tools like Poedit
to add translations.

After you are done, update compiled translations via::

```shell
poetry run make update-messages
```

## Get Started!

Ready to contribute? Here's how to set up `tg-react` for local development.

1. Fork the `tg-react` repo on GitHub.

2. Clone your fork locally::
    ```shell
    git clone git@github.com:your_name_here/tg-react.git
    ```

3. [Install poetry](https://python-poetry.org/docs/#installation)

4. Install dependencies:
    ```shell
    poetry install
    ```

4. Create a branch for local development::
    ```shell
    git checkout -b name-of-your-bugfix-or-feature
    ```
   Now you can make your changes locally.

5. When you're done making changes, check that your changes pass linters and the tests, including testing other Python versions with tox:
    ```shell
    poetry run lint
    poetry run test
    poetry run test-all
    ```

6. Commit your changes and push your branch to GitHub::
    ```shell
    git add .
    git commit -m "Your detailed description of your changes."
    git push origin name-of-your-bugfix-or-feature
    ```

7. Submit a pull request through the GitHub website.

## Pull Request Guidelines

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.
2. If the pull request adds functionality, the docs should be updated. Put
   your new functionality into a function with a docstring, and add the
   feature to the list in README.rst. You should also update the documentation
   source files via::
    ```shell
    poetry run make docs
    ```

3. If the pull request modifies/adds translations don't forget to run::
    ```shell
    poetry run make update-messages
    ```

4. The pull request should work for Python 3.6, 3.7, 3.8 and 3.9. Check
   https://travis-ci.org/thorgate/tg-react/pull_requests
   and make sure that the tests pass for all supported Python versions.

Tips
----

Run full test suite via tox (all python and django version combinations):

```shell
poetry run make test-all
```

To run a subset of tests:

```shell
poetry run py.test tests.test_tg_react
```

Update documentation source files and generate it:

```shell
poetry run make docs
```

To see all make commands:

```shell
poetry run make help
```
