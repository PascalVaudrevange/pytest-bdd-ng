Feature: Gherkin steps are executed by pytest
  Scenario: Steps are executed by corresponding step keyword decorator
    Given File "steps.feature" with content:
      """gherkin
      Feature: Steps are executed by corresponding step keyword decorator

        Scenario:
            Given Step counter

            * Step is executed by plain step decorator
            And Step is executed by plain step decorator
            But Step is executed by plain step decorator

            Given Step is executed by given step decorator
            And Step is executed by given step decorator
            But Step is executed by given step decorator

            When Step is executed by when step decorator
            And Step is executed by when step decorator
            But Step is executed by when step decorator

            Then Step is executed by then step decorator
            And Step is executed by then step decorator
            But Step is executed by then step decorator

            Then there are passed steps by kind:
              |step|given|when|then|
              |   3|    3|   3|   3|
      """
    And File "conftest.py" with content:
        """python
        from operator import attrgetter
        from pytest_bdd import given, when, then, step
        from pytest_bdd.utils import compose

        @given('Step counter', target_fixture='step_counter')
        def step_counter():
          yield {'step': 0, 'given': 0,'when': 0,'then': 0,}


        @step('Step is executed by plain step decorator')
        def plain_step(step_counter):
          step_counter['step'] += 1

        @given('Step is executed by given step decorator')
        def given_step(step_counter):
          step_counter['given'] += 1

        @when('Step is executed by when step decorator')
        def when_step(step_counter):
          step_counter['when'] += 1

        @then('Step is executed by then step decorator')
        def then_step(step_counter):
          step_counter['then'] += 1

        @then('there are passed steps by kind:')
        def check_step_counter(step, step_counter):
          oracle_results_kwargs = map(attrgetter("value"), step.data_table.rows[0].cells)
          oracle_results_kwargs_values = map(compose(int, attrgetter("value")), step.data_table.rows[1].cells)
          oracle_result = dict(zip(oracle_results_kwargs, oracle_results_kwargs_values))

          assert oracle_result == step_counter

        """

    When run pytest
    Then pytest outcome must contain tests with statuses:
      |passed|
      |     1|

  Scenario: Steps could be executed by aliased step keyword decorator
    Could be useful to declare the same fixtures or steps with
    different names for better readability. In order to use the same step
    function with multiple step names simply decorate it multiple times.

    Given File "steps.feature" with content:
      """gherkin
      Feature: Steps could be executed by aliased step keyword decorator

        Scenario:
            Given Step counter

            * Step is executed by aliased step decorator
            Given Step is executed by aliased step decorator
            When Step is executed by aliased step decorator
            Then Step is executed by aliased step decorator

            Then there are "4" passed aliased steps
      """

    And File "conftest.py" with content:
        """python
        from pytest_bdd import given, when, then, step

        @given('Step counter', target_fixture='step_counter')
        def step_counter():
          yield {'steps_count': 0}

        @step('Step is executed by aliased step decorator')
        @given('Step is executed by aliased step decorator')
        @when('Step is executed by aliased step decorator')
        @then('Step is executed by aliased step decorator')
        def aliased_step(step_counter):
          step_counter['steps_count'] += 1

        @then(
          'there are "{int}" passed aliased steps',
          anonymous_group_names=('oracle_steps',),
        )
        def then_step(step_counter, oracle_steps):
          assert step_counter['steps_count'] == oracle_steps
        """

    When run pytest
    Then pytest outcome must contain tests with statuses:
      |passed|
      |     1|

  Rule:  Steps could be executed by liberal step keyword decorator
    Background:
      Given File "steps.feature" with content:
        """gherkin
        Feature: Steps could be executed by liberal step keyword decorator

          Scenario:
            Given Step counter

            * Step is executed by liberal step decorator
            Given Step is executed by liberal step decorator
            When Step is executed by liberal step decorator
            Then Step is executed by liberal step decorator

            * Step is executed by liberal given decorator
            Given Step is executed by liberal given decorator
            When Step is executed by liberal given decorator
            Then Step is executed by liberal given decorator

            * Step is executed by liberal when decorator
            Given Step is executed by liberal when decorator
            When Step is executed by liberal when decorator
            Then Step is executed by liberal when decorator

            * Step is executed by liberal then decorator
            Given Step is executed by liberal then decorator
            When Step is executed by liberal then decorator
            Then Step is executed by liberal then decorator

            Then there are "16" passed liberal steps
        """
    Scenario: Same step is used with different keywords
      Given File "conftest.py" with content:
        """python
        from pytest_bdd import given, when, then, step

        @given('Step counter', target_fixture='step_counter')
        def step_counter():
          yield {'steps_count': 0}

        @step('Step is executed by liberal step decorator', liberal=True)
        @given('Step is executed by liberal given decorator', liberal=True)
        @when('Step is executed by liberal when decorator', liberal=True)
        @then('Step is executed by liberal then decorator', liberal=True)
        def liberal_step(step_counter):
          step_counter['steps_count'] += 1

        @then(
          'there are "{int}" passed liberal steps',
          anonymous_group_names=('oracle_steps',),
        )
        def then_step(step_counter, oracle_steps):
          assert step_counter['steps_count'] == oracle_steps
        """

      When run pytest
      Then pytest outcome must contain tests with statuses:
        |passed|
        |     1|

    Scenario: Keyworded steps could be treated as liberal by pytest command line option
      Given File "conftest.py" with content:
        """python
        from pytest_bdd import given, when, then, step

        @given('Step counter', target_fixture='step_counter')
        def step_counter():
          yield {'steps_count': 0}

        @step('Step is executed by liberal step decorator')
        @given('Step is executed by liberal given decorator')
        @when('Step is executed by liberal when decorator')
        @then('Step is executed by liberal then decorator')
        def liberal_step(step_counter):
          step_counter['steps_count'] += 1

        @then(
          'there are "{int}" passed liberal steps',
          anonymous_group_names=('oracle_steps',),
        )
        def then_step(step_counter, oracle_steps):
          assert step_counter['steps_count'] == oracle_steps
        """

      When run pytest
        |cli_args| --liberal-steps|
      Then pytest outcome must contain tests with statuses:
        |passed|failed|
        |     1|     0|
