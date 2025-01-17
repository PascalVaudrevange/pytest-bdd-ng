Feature: Scenario Outline examples could be tagged
  Rule:
    Background:
      Given File "steps.feature" with content:
        """gherkin
        Feature: Steps are executed by corresponding step keyword decorator

          Scenario Outline:
              Given I produce <outcome> test

              @passed
              Examples:
              |outcome|
              |passed |

              @failed
              Examples:
              |outcome|
              |failed |

              @both
              Examples:
              |outcome|
              |passed |
              |failed |
        """
      Given File "pytest.ini" with content:
        """ini
        [pytest]
        markers =
          passed
          failed
          both
        """
      And File "conftest.py" with content:
        """python
        from pytest_bdd.compatibility.pytest import fail
        from pytest_bdd import given

        @given('I produce passed test')
        def passing_step():
          ...

        @given('I produce failed test')
        def failing_step():
          fail('Enforce fail')
        """
    Example:
      When run pytest
        |cli_args|-m|passed|
      Then pytest outcome must contain tests with statuses:
        |passed|failed|
        |     1|     0|

    Example:
      When run pytest
        |cli_args|-m|failed|
      Then pytest outcome must contain tests with statuses:
        |passed|failed|
        |     0|     1|

    Example:
      When run pytest
        |cli_args|-m|passed or failed|
      Then pytest outcome must contain tests with statuses:
        |passed|failed|
        |     1|     1|

    Example:
      When run pytest
        |cli_args|-m|not both|
      Then pytest outcome must contain tests with statuses:
        |passed|failed|
        |     1|     1|

    Example:
      When run pytest
        |cli_args|-m|both|
      Then pytest outcome must contain tests with statuses:
        |passed|failed|
        |     1|     1|

    Example:
      When run pytest
      Then pytest outcome must contain tests with statuses:
        |passed|failed|
        |     2|     2|
