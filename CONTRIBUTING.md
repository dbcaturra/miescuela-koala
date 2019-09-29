# Introduction

## Hey there, feel welcome!

We’re very happy to see you here, with the wish to **contribute to ~~our~~ your project**, **Koala LMS**. Please, read the following sections in order to know how to **ask questions**, **report bugs** or **contribute** to the code of **Koala LMS** and its applications.

Those guidelines are meant to give you answers about the contribution process. Having something formalized helps us to manage contributions and gives you a guide to do so.


**Koala LMS** would like to be an **open community** where everyone has something to give. We are looking for translators, documentation writers, communication specialists, developers and **everyone that wishes to contribute** using its own abilities.

Please, don't use the issue tracker for support questions. We plan to add things like mailling lists or IRC channels in case some help is required.

## Responsibilities

* Assume people mean well: when you’re discussing or debatting with others, please assume they mean well. We’re here to cooperate 🙃.
* Ensure your changes run on Firefox, Google Chrome (and Edge, even if few people care!).
* Ensure your code respects the Python PEP8 standards (we’ve got a pipeline to check that).
* Ensure your strings are written in a proper english.
* Ensure the strings you changed are also present in the Gettext PO files.
* If you wish to make major changes or enhancements, open an issue to let us discuss about it. Discuss things transparently and get community feedback.
* Be welcoming to newcomers and encourage diverse new contributors from all backgrounds. See the [Python Community Code of Conduct](https://www.python.org/psf/codeofconduct/).

## Your First Contribution

If you’re not sure on where to start, we tagged some issues with the ~newcommer flag. You can pick this issue and start working on it. We supposed those issues could be fixed with only a few lines, and tests. The ~"help wanted" tagged issues are a bit more complicated, it’s the next step for you 😉.

If you don’t know which one you should take, watch the votes or issues to see the impact the change may have for the developers and users.

# Getting started

### Submit a patch or an enhancement

Everything starts with a Gitlab issue. If you think something does not work properly, [open a new issue](https://gitlab.com/koala-lms/lms/issues/new). If you do not know which component you want to fix or enhance, just open an issue for the [Koala LMS project](https://gitlab.com/koala-lms/lms). We will sort issues after and move them to the appropriate project.

By contributing, you agree that your code will be published under the [GPLv3 licence](https://www.gnu.org/licenses/quick-guide-gplv3.html) and that you own what you write. Your other contributions (images, etc.) may be published under the [Creative Common Zero licence](https://creativecommons.org/publicdomain/zero/1.0/deed).

The process you should follow is :
1. Create **your own fork** of the code
2. Do the changes **in your fork**
3. If you like the change and think the project could use it:
    * Be sure you have followed the code style for the project.
    * Sign-off your commits
    * **Open a merge request** to include your changes into the `develop` branch of the application or project.

## How to report a bug

**If you find a security vulnerability, *SET the issue as confidential***. Please be as more precise as possible, and, if possible provide a fix for that vulnerability.

For any other case, please choose the appropriate issue template. Give us the following information:
* Which version of Django are you using? Which version of Python? On which OS?
* What did you do?
* What do you expect to see?
* What did you see instead?

## Code review process

If you implement a change (bugfix or enhancement) in Koala or any application, you should ensure to follow the following rules:
* Your code must respect the PEP 8 standards (with specific changes set in `.editorconfig`). You can use `prospector` to check that it’s done properly.
* Check for basic security issues using `bandit`.
* Write some tests to validate your changes.

A pipeline check all those things, but it’s better if you do it on your own.

## Commit message conventions

For the moment, we have few commit message requirements, but it’s better if your copy the following template and set Git accordingly:

    # <type>: (If applied, this commit will...) <subject> (Max 50 char)
    # |<----  Using a Maximum Of 50 Characters  ---->|
    
    
    # Explain why this change is being made
    # |<----   Try To Limit Each Line to a Maximum Of 72 Characters   ---->|
    
    # Provide links or keys to any relevant tickets, articles or other resources
    # Example: Github issue #23
    
    # --- COMMIT END ---
    # Type can be 
    #    feat     (new feature)
    #    fix      (bug fix)
    #    refactor (refactoring production code)
    #    style    (formatting, missing semi colons, etc; no code change)
    #    docs     (changes to documentation)
    #    test     (adding or refactoring tests; no production code change)
    #    chore    (updating grunt tasks etc; no production code change)
    #    l10n     (localization)
    #    i18n     (internationalization)
    # --------------------
    # Remember to
    #    Capitalize the subject line
    #    Use the imperative mood in the subject line
    #    Do not end the subject line with a period
    #    Separate subject from body with a blank line
    #    Use the body to explain what and why vs. how
    #    Can use multiple lines with "-" for bullet points in body
    # --------------------
    # For more information about this template, check out
    # https://gist.github.com/adeekshith/cd4c95a064977cdc6c50

