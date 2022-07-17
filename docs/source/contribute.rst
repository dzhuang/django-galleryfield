Contributing to django-galleryfield
====================================

We want to make contributing to this project as approachable and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

Our Development Process
*************************

We use github to host code, to track issues and feature requests, as well as accept pull requests.

Pull requests
***************

Pull requests are the best way to propose changes to the codebase (we use `Github Flow <https://docs.github.com/en/get-started/quickstart/github-flow>`__ ). We actively welcome your pull requests:

1. Fork the repo and create your branch from ``main``.
2. If you've added code that should be tested, add tests.
3. If you've changed APIs, update the documentation.
4. Ensure the test suite passes.
5. Make sure your code lints.
6. Issue that pull request!

Specifically, if you were testing locally, run::

    git clone https://github.com/dzhuang/django-galleryfield.git
    cd django-galleryfield
    pip install -r requirements.txt
    pip install isort flake8

    # Your modification to the code

    # tests
    pytest .

    # Sorting imports
    isort galleryfield dem demo_custom tests

    # Python code styling check
    flake8

Notice that we are using ``rollup.js`` to bundle assets (except ``Bootstrap`` and ``jQuery``) into ``galleryfield-ui.js``,
if you want to contribute to JavaScript and CSS code, the files you need to consider to modify includes (but not limit to):

- ``./rollup.config.js``: the rollup run script
- ``./galleryfield/static/js/bundle-source.js``
- ``./galleryfield/static/js/jquery.fileupload-ui-gallery-widget.js``: the major scripts file
- ``./galleryfield/static/css/bundle.css``
- ``./galleryfield/static/css/gallery-widget.css``

The process follows::

   npm install

   # Your modification to the code

   npm run build


Issues
*******

We use GitHub issues to track public bugs. Report a bug by `opening a new issue <https://github.com/dzhuang/django-galleryfield/issues/new/choose>`__ ; it's that easy!

**Great Bug Reports** tend to have:

- A quick summary and/or background
- Steps to reproduce

  - Be specific!
  - Give sample code if you can. Includes sample code that *anyone* with a base setup can run to reproduce what you were seeing
- What you expected would happen
- What actually happens
- Notes (possibly including why you think this might be happening, or stuff you tried that didn't work)


License agreements
******************
By contributing, you agree that your contributions will be licensed under its MIT License.

References
************

This document was adapted from the open-source contribution guidelines for `Facebook's Draft <https://github.com/facebook/draft-js/blob/main/CONTRIBUTING.md>`__ .
