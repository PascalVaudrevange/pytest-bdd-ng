Scenario decorator
------------------

Feature files auto-collection could be disabled by use `--disable-feature-autoload` cli option
or `disable_feature_autoload` `pytest.ini` option. In this case there mechanism to use features from
`test_*.py` pytest files: functions decorated with the `scenario` decorator behave like a normal test function,
and they will be executed after all scenario steps.

.. code-block:: python

    from pytest_bdd import scenario, given, when, then

    @scenario('publish_article.feature', 'Publishing the article')
    def test_publish(browser):
        assert article.title in browser.html


.. NOTE:: It is however encouraged to try as much as possible to have your logic only inside the Given, When, Then steps.

Step parameters
---------------

Often it's possible to reuse steps giving them a parameter(s).
This allows to have single implementation and multiple use, so less code.
Also opens the possibility to use same step twice in single scenario and with different arguments!
And even more, there are several types of step parameter parsers at your disposal
(idea taken from behave_ implementation):

.. _pypi_parse: http://pypi.python.org/pypi/parse
.. _pypi_parse_type: http://pypi.python.org/pypi/parse_type
.. _pypi_cucumber_expressions: http://pypi.python.org/pypi/cucumber-expressions

**heuristic** (default)
    Tries to select right parser between string, cucumber_expression, cfparse and re. Any object that supports `__str__`
    interface and does not support parser interface will be wrapped with this parser
**parse** (based on: pypi_parse_)
    Provides a simple parser that replaces regular expressions for
    step parameters with a readable syntax like ``{param:Type}``.
    The syntax is inspired by the Python builtin ``string.format()``
    function.
    Step parameters must use the named fields syntax of pypi_parse_
    in step definitions. The named fields are extracted,
    optionally type converted and then used as step function arguments.
    Supports type conversions by using type converters passed via `extra_types`
**cfparse** (extends: pypi_parse_, based on: pypi_parse_type_)
    Provides an extended parser with "Cardinality Field" (CF) support.
    Automatically creates missing type converters for related cardinality
    as long as a type converter for cardinality=1 is provided.
    Supports parse expressions like:
    * ``{values:Type+}`` (cardinality=1..N, many)
    * ``{values:Type*}`` (cardinality=0..N, many0)
    * ``{value:Type?}``  (cardinality=0..1, optional)
    Supports type conversions (as above).
**re**
    This uses full regular expressions to parse the clause text. You will
    need to use named groups "(?P<name>...)" to define the variables pulled
    from the text and passed to your ``step()`` function.
    Type conversion can only be done via `converters` step decorator argument (see example below).
**string**
    This can be considered as a `null` or `exact` parser. It parses no parameters
    and matches the step name by equality of strings.
**cucumber_expression** (based on: pypi_cucumber_expressions_)
    `Cucumber Expressions <https://github.com/cucumber/cucumber-expressions>`_ is an alternative to Regular Expressions with a more intuitive syntax.
**cucumber_regular_expression** (based on: pypi_cucumber_expressions_)
    Alternative regular expression step parser

Parsers except `string`, as well as their optional arguments are specified like:

for `cfparse` parser:

.. code-block:: python

    from pytest_bdd import parsers

    @given(
        parsers.cfparse(
            "there are {start:Number} cucumbers",
            extra_types=dict(Number=int)
        ),
        target_fixture="start_cucumbers",
    )
    def start_cucumbers(start):
        return dict(start=start, eat=0)

or using `cfparse` Parser (or `parse`) directly:

.. code-block:: python

    from parse_type.cfparse import Parser as cfparse

    @given(
        cfparse(
            "there are {start:Number} cucumbers",
            extra_types=dict(Number=int)
        ),
        target_fixture="start_cucumbers",
    )
    def start_cucumbers(start):
        return dict(start=start, eat=0)

for `re` parser

.. code-block:: python

    from pytest_bdd import parsers

    @given(
        parsers.re(r"there are (?P<start>\d+) cucumbers"),
        converters=dict(start=int),
        target_fixture="start_cucumbers",
    )
    def start_cucumbers(start):
        return dict(start=start, eat=0)

or using compiled regular expression directly:

.. code-block:: python

    import re

    @given(
        re.compile(r"there are (?P<start>\d+) cucumbers"),
        converters=dict(start=int),
        target_fixture="start_cucumbers",
    )
    def start_cucumbers(start):
        return dict(start=start, eat=0)

for `cucumber_expression`:

.. code-block:: python

    from pytest_bdd import parsers

    @given(
        parsers.cucumber_expression("there are {int} cucumbers"),
        anonymous_group_names=('start',),
        target_fixture="start_cucumbers",
    )
    def start_cucumbers(start):
        return dict(start=start, eat=0)

or using CucumberExpression directly:

.. code-block:: python

    from cucumber_expressions.expression import CucumberExpression
    from cucumber_expressions.parameter_type_registry import ParameterTypeRegistry

    @given(
        CucumberExpression("there are {int} cucumbers", parameter_type_registry=ParameterTypeRegistry()),
        anonymous_group_names=('start',),
        target_fixture="start_cucumbers",
    )
    def start_cucumbers(start):
        return dict(start=start, eat=0)

.. NOTE:: `anonymous_group_names` step parameter is used to give names for non-named cucumber/regular expression groups.

Example:

.. code-block:: gherkin

    Feature: Step arguments
        Scenario: Arguments for given, when, then
            Given there are 5 cucumbers

            When I eat 3 cucumbers
            And I eat 2 cucumbers

            Then I should have 0 cucumbers


The code will look like:

.. code-block:: python

    import re
    from parse import Parser as parse
    from pytest_bdd import scenario, given, when, then


    @scenario("arguments.feature", "Arguments for given, when, then")
    def test_arguments():
        pass


    @given(parse("there are {start:d} cucumbers"), target_fixture="start_cucumbers")
    def start_cucumbers(start):
        return dict(start=start, eat=0)


    @when(parse("I eat {eat:d} cucumbers"))
    def eat_cucumbers(start_cucumbers, eat):
        start_cucumbers["eat"] += eat


    @then(parse("I should have {left:d} cucumbers"))
    def should_have_left_cucumbers(start_cucumbers, start, left):
        assert start_cucumbers['start'] == start
        assert start - start_cucumbers['eat'] == left

Example code also shows possibility to pass argument converters which may be useful if you need to postprocess step
arguments after the parser.

You can implement your own step parser. It's interface is quite simple. The code can looks like:

.. code-block:: python

    import re
    from pytest_bdd import given, parsers


    class MyParser(parsers.StepParser):
        """Custom parser."""

        def __init__(self, name, **kwargs):
            """Compile regex."""
            super().__init__(name)
            self.regex = re.compile(re.sub("%(.+)%", "(?P<\1>.+)", self.name), **kwargs)

        def parse_arguments(self, name):
            """Get step arguments.

            :return: `dict` of step arguments
            """
            return self.regex.match(name).groupdict()

        def is_matching(self, name):
            """Match given name with the step name."""
            return bool(self.regex.match(name))


    @given(parsers.parse("there are %start% cucumbers"), target_fixture="start_cucumbers")
    def start_cucumbers(start):
        return dict(start=start, eat=0)

Step arguments could be defined without parsing
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
If you want specify some default values for parameters without parsing them (useful for step aliases), you could do:

.. code-block:: python

    @given("I have default defined param", param_defaults={'default_param': 'foo'}, target_fixture='foo_fixture')
    def save_fixture(default_param):
        return default_param


Step arguments are injected into step context
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Step arguments are injected into step context and could be used as normal fixtures with the names equal to the names of the arguments by default. This opens a number of possibilities:

* you can access step's argument as a fixture in other step function just by mentioning it as an argument (just like any other pytest fixture)

* if the name of the step argument clashes with existing fixture, it will be overridden by step's argument value; this way you can set/override the value for some fixture deeply inside of the fixture tree in a ad-hoc way by just choosing the proper name for the step argument.

This behavior is same to:

.. code-block:: python

    @given(
        'I have a "{foo}", "{bar}", "{fizz}", "{buzz}" parameters few of which are accepted by wild pattern',
        params_fixtures_mapping={...: ...}
    )
    def step(foo, bar, fizz, buzz):
        ...

But this behavior could be changed; For example you want to rename some parameters and left other as-is.
`Ellipsis <https://docs.python.org/dev/library/constants.html#Ellipsis>`_ instance means all present attributes, but not listed directly.

.. code-block:: python

    @given(
        'I have a "{foo}", "{bar}", "{fizz}", "{buzz}" parameters few of which are accepted by wild pattern',
        params_fixtures_mapping={'foo': 'cool_foo', 'bar': 'nice_bar', ...: ...}
    )
    def step(cool_foo, nice_bar, fizz, buzz):
        ...

Or don't inject parameters as fixtures at all:

.. code-block:: python

    @given('I have a "{foo}", "{bar}", "{fizz}", "{buzz}" parameters few of which are accepted by wild pattern',
               params_fixtures_mapping={...: None})
    def step(foo, bar, fizz, buzz):
        ...

Parameters still could be used in steps, but they are not injected!
If you would like to inject just some subset of parameters - set of parameters could be used:

.. code-block:: python

    @given('I have a "{foo}", "{bar}", "{fizz}", "{buzz}" parameters few of which are accepted by wild pattern',
               params_fixtures_mapping={'fizz', 'buzz'})
    def step(foo, bar, fizz, buzz):
        ...

Override fixtures by outgoing step results
------------------------------------------

Dependency injection is not a panacea if you have complex structure of your test setup data. Sometimes there's a need
such a given step which would imperatively change the fixture only for certain test (scenario), while for other tests
it will stay untouched. To allow this, special parameter `target_fixture` exists in the decorator:

.. code-block:: python

    from pytest_bdd import given

    @pytest.fixture
    def foo():
        return "foo"


    @given("I have injecting given", target_fixture="foo")
    def injecting_given():
        return "injected foo"


    @then('foo should be "injected foo"')
    def foo_is_foo(foo):
        assert foo == 'injected foo'


.. code-block:: gherkin

    Feature: Target fixture
        Scenario: Test given fixture injection
            Given I have injecting given
            Then foo should be "injected foo"


In this example existing fixture `foo` will be overridden by given step `I have injecting given` only for scenario it's
used in.

Sometimes it is also useful to let `when` and `then` steps to provide a fixture as well.
A common use case is when we have to assert the outcome of an HTTP request:

.. code-block:: python

    # test_blog.py

    from pytest_bdd import scenarios, given, when, then

    from my_app.models import Article

    test_cukes = scenarios("blog.feature")


    @given("there is an article", target_fixture="article")
    def there_is_an_article():
        return Article()


    @when("I request the deletion of the article", target_fixture="request_result")
    def there_should_be_a_new_article(article, http_client):
        return http_client.delete(f"/articles/{article.uid}")


    @then("the request should be successful")
    def article_is_published(request_result):
        assert request_result.status_code == 200


.. code-block:: gherkin

    # blog.feature

    Feature: Blog
        Scenario: Deleting the article
            Given there is an article

            When I request the deletion of the article

            Then the request should be successful

Also it's possible to override multiple fixtures in one step using `target_fixtures` parameter:

.. code-block:: python

    @given("some compound fixture", target_fixtures=["fixture_a","fixture_b"])
    def __():
        return "fixture_a_value", "fixture_b_value"


Loading whole feature files
---------------------------

If you have relatively large set of feature files, it's boring to manually bind scenarios to the tests using the
scenario decorator(in case if you don't want use feature auto-load). Of course with the manual approach you get all
the power to be able to additionally parametrize the test, give the test function a nice name, document it, etc,
but in the majority of the cases you don't need that. Instead you want to bind `all` scenarios found in the
`feature` folder(s) recursively automatically.

Scenarios shortcut
^^^^^^^^^^^^^^^^^^

First option is `scenarios` helper.

.. code-block:: python

    from pytest_bdd import scenarios

    # assume 'features' subfolder is in this file's directory
    test_cukes = scenarios('features')

That's all you need to do to bind all scenarios found in the `features` folder!
Note that you can pass multiple paths, and those paths can be either feature files or feature folders.


.. code-block:: python

    from pytest_bdd import scenarios

    # pass multiple paths/files
    test_cukes = scenarios('features', 'other_features/some.feature', 'some_other_features')

But what if you need to manually bind certain scenario, leaving others to be automatically bound?
Just write your scenario in a `normal` way, but filter out scenario, and bind it manually:


.. code-block:: python

    from pytest_bdd import scenario, scenarios

    # assume 'features' subfolder is in this file's directory
    test_cukes = scenarios('features', filter_ = lambda: config, feature, scenario: scenario.name != 'Test something')

    @scenario('features/some.feature', 'Test something')
    def test_something():
        pass

In the example above `test_something` scenario binding will be kept manual, other scenarios found in the `features`
folder will be bound automatically.

Both `scenario` or `scenarios` could be used as decorators or as operator calls. Also they could be inlined:

.. code-block:: python

    from pytest_bdd import scenario, scenarios

    test_features = scenarios('features', return_test_decorator=False)

    test_specific_scenario = scenario('features/some.feature', 'Test something', return_test_decorator=False)

Both `scenario` and `scenarios` functions could use http/https URIs to get features from remote servers
(and be integrated with tools like Hiptest)

Feature tags
------------

For picking up tests to run we can use
`tests selection <http://pytest.org/latest/usage.html#specifying-tests-selecting-tests>`_ technique. The problem is that
you have to know how your tests are organized, knowing only the feature files organization is not enough.
`cucumber tags <https://github.com/cucumber/cucumber/wiki/Tags>`_ introduce standard way of categorizing your features
and scenarios, which pytest-bdd-ng supports. For example, we could have:

.. code-block:: gherkin

    @login @backend
    Feature: Login

      @successful
      Scenario: Successful login


pytest-bdd-ng uses `pytest markers <http://pytest.org/latest/mark.html#mark>`_ as a `storage` of the tags for the given
scenario test, so we can use standard test selection:

.. code-block:: bash

    pytest -m "backend and login and successful"

The feature and scenario markers are not different from standard pytest markers, and the ``@`` symbol is stripped out
automatically to allow test selector expressions. If you want to have bdd-related tags to be distinguishable from the
other test markers, use prefix like `bdd`.
Note that if you use pytest `--strict` option, all bdd tags mentioned in the feature files should be also in the
`markers` setting of the `pytest.ini` config. Also for tags please use names which are python-compatible variable
names, eg starts with a non-number, underscore alphanumeric, etc. That way you can safely use tags for tests filtering.

You can customize how tags are converted to pytest marks by implementing the
``pytest_bdd_convert_tag_to_marks`` hook and returning list of resulting marks from it:

.. code-block:: python

   def pytest_bdd_convert_tag_to_marks(feature, scenario, tag):
       if tag == 'todo':
           marker = pytest.mark.skip(reason="Not implemented yet")
           return [marker]


Test setup
----------

Test setup is implemented within the Given section. Even though these steps
are executed imperatively to apply possible side-effects, pytest-bdd-ng is trying
to benefit of the PyTest fixtures which is based on the dependency injection
and makes the setup more declarative style.

.. code-block:: python

    @given("I have a beautiful article", target_fixture="article")
    def article():
        return Article(is_beautiful=True)

The target PyTest fixture "article" gets the return value and any other step can depend on it.

.. code-block:: gherkin

    Feature: The power of PyTest
        Scenario: Symbolic name across steps
            Given I have a beautiful article
            When I publish this article

When step is referring the article to publish it.

.. code-block:: python

    @when("I publish this article")
    def publish_article(article):
        article.publish()


Many other BDD toolkits operate a global context and put the side effects there.
This makes it very difficult to implement the steps, because the dependencies
appear only as the side-effects in the run-time and not declared in the code.
The publish article step has to trust that the article is already in the context,
has to know the name of the attribute it is stored there, the type etc.

In pytest-bdd-ng you just declare an argument of the step function that it depends on
and the PyTest will make sure to provide it.

Still side effects can be applied in the imperative style by design of the BDD.

.. code-block:: gherkin

    Feature: News website
        Scenario: Publishing an article
            Given I have a beautiful article
            And my article is published

Functional tests can reuse your fixture libraries created for the unit-tests and upgrade
them by applying the side effects.

.. code-block:: python

    @pytest.fixture
    def article():
        return Article(is_beautiful=True)


    @given("I have a beautiful article")
    def i_have_a_beautiful_article(article):
        pass


    @given("my article is published")
    def published_article(article):
        article.publish()
        return article


This way side-effects were applied to our article and PyTest makes sure that all
steps that require the "article" fixture will receive the same object. The value
of the "published_article" and the "article" fixtures is the same object.

Fixtures are evaluated only once within the PyTest scope and their values are cached.

Reusing steps
-------------

It is possible to define some common steps in the parent conftest.py and
simply expect them in the child test file.

common_steps.feature:

.. code-block:: gherkin

    Scenario: All steps are declared in the conftest
        Given I have a bar
        Then bar should have value "bar"

conftest.py:

.. code-block:: python

    from pytest_bdd import given, then


    @given("I have a bar", target_fixture="bar")
    def bar():
        return "bar"


    @then('bar should have value "bar"')
    def bar_is_bar(bar):
        assert bar == "bar"

test_common.py:

.. code-block:: python

    @scenario("common_steps.feature", "All steps are declared in the conftest")
    def test_conftest():
        pass

There are no definitions of the steps in the test file. They were
collected from the parent conftest.py.


Default steps
-------------

Here is the list of steps that are implemented inside of the pytest-bdd:

given
    * trace - enters the `pdb` debugger via `pytest.set_trace()`
when
    * trace - enters the `pdb` debugger via `pytest.set_trace()`
then
    * trace - enters the `pdb` debugger via `pytest.set_trace()`


Feature file paths
------------------

By default, pytest-bdd-ng will use current module's path as base path for finding feature files, but this behaviour can
be changed in the pytest configuration file (i.e. `pytest.ini`, `tox.ini` or `setup.cfg`) by declaring the new base
path in the `bdd_features_base_dir` key. The path is interpreted as relative to the pytest root directory.
You can also override features base path on a per-scenario basis, in order to override the path for specific tests.

pytest.ini:

.. code-block:: ini

    [pytest]
    bdd_features_base_dir = features/

tests/test_publish_article.py:

.. code-block:: python

    from pytest_bdd import scenario


    @scenario("foo.feature", "Foo feature in features/foo.feature")
    def test_foo():
        pass


    @scenario(
        "foo.feature",
        "Foo feature in tests/local-features/foo.feature",
        features_base_dir="./local-features/",
    )
    def test_foo_local():
        pass


The `features_base_dir` parameter can also be passed to the `@scenario` decorator.


Localization
------------

pytest-bdd-ng supports all localizations which Gherkin `does <https://cucumber.io/docs/gherkin/languages/>`_


Hooks
-----

pytest-bdd-ng exposes several `pytest hooks <http://pytest.org/latest/plugins.html#well-specified-hooks>`_
which might be helpful building useful reporting, visualization, etc on top of it:

* pytest_bdd_before_scenario(request, feature, scenario) - Called before scenario is executed
* pytest_bdd_run_scenario(request, feature, scenario) - Execution scenario protocol
* pytest_bdd_after_scenario(request, feature, scenario) - Called after scenario is executed
  (even if one of steps has failed)
* pytest_bdd_before_step(request, feature, scenario, step, step_func) - Called before step function
  is executed and it's arguments evaluated
* pytest_bdd_run_step(request, feature, scenario, step, previous_step) - Execution step protocol
* pytest_bdd_before_step_call(request, feature, scenario, step, step_func, step_func_args) - Called before step
  function is executed with evaluated arguments
* pytest_bdd_after_step(request, feature, scenario, step, step_func, step_func_args) - Called after step function
  is successfully executed
* pytest_bdd_step_error(request, feature, scenario, step, step_func, step_func_args, exception) - Called when step
  function failed to execute
* pytest_bdd_step_func_lookup_error(request, feature, scenario, step, exception) - Called when step lookup failed
* pytest_bdd_match_step_definition_to_step(request, feature, scenario, step, previous_step) - Called to match step to step definition
* pytest_bdd_get_step_caller(request, feature, scenario, step, step_func, step_func_args, step_definition) - Called to get step caller. For example could be used to make steps async
* pytest_bdd_get_step_dispatcher(request, feature, scenario) - Provide alternative approach to execute scenario steps

Fixtures
--------

pytest-bdd-ng exposes several plugin fixtures to give more testing flexibility

* bdd_example - The current scenario outline parametrization.
* step_registry - Contains registry of all user-defined steps
* step_matcher- Contains matcher to help find step definition for selected step of scenario
* steps_left - Current scenario steps left to execute; Allow inject steps to execute:

.. code-block:: python

    from collections import deque

    from pytest_bdd.model import UserStep
    from pytest_bdd import when

    @when('I inject step "{keyword}" "{step_text}')
    def inject_step(steps_left: deque, keyword, step_text, scenario):
        steps_left.appendleft(UserStep(text=step_text, keyword=keyword, scenario=scenario))

StructBDD
---------
Gherkin itself isn't a perfect tool to describe complex Data Driven Scenarios with alternative paths to execute test.
For example it doesn't support next things:

* Few backgrounds per scenario
* Alternative flows for scenario to setup same state
* Alternative flows to describe same behavior defined by different steps
* Usage of parameters inside Backgrounds
* Joining of parameter tables, so full Cartesian product of parameters has to be listed in Examples
* Example tables on different scenario levels

For such scenarios StructBDD DSL was developed. It independent on underlying data format, but supports most common
formats for DSL development: YAML, Hocon, TOML, JSON5, HJSON out the box.

Steps could be defined as usual, and scenarios have different options. Let see.

steps.bdd.yaml

.. code-block:: yaml

    Name: Steps are executed one by one
    Description: |
        Steps are executed one by one. Given and When sections
        are not mandatory in some cases.
    Steps:
        - Step:
            Name: Executed step by step
            Description: Scenario description
            Steps:
                - I have a foo fixture with value "foo"
                - And: there is a list
                - When: I append 1 to the list
                - Step:
                    Action: I append 2 to the list
                    Type: And
                - Alternative:
                    - Step:
                        Steps:
                            - And: I append 3 to the list
                            - Then: foo should have value "foo"
                            - But: the list should be [1, 2, 3]
                    - Step:
                        Steps:
                            - And: I append 4 to the list
                            - Then: foo should have value "foo"
                            - But: the list should be [1, 2, 4]


Alternative steps produce separate test launches for every of flows. If alternative steps are defined on different
levels - there would be Cartesian product of tests for every alternative step.

Scenario could be imported as usual, but with specified parser:

.. code-block:: python

    from textwrap import dedent
    from pytest_bdd import given, when, then, scenario
    from pytest_bdd.parser import StructBDDParser
    from functools import partial

    kind = StructBDDParser.KIND.YAML

    @scenario(f"steps.bdd.{kind}", "Executed step by step", parser=partial(StructBDDParser, kind=kind)
    def test_steps(feature):
        pass


Another option is to inject built scenario directly:

.. code-block:: python

    from pytest_bdd.struct_bdd.model import Step, Table

    test_cukes = Step(
        name="Examples are substituted",
        steps=[
            Step(type='Given', action='I have <have> cucumbers'),
            Step(type='And', action='I eat <eat> cucumbers'),
            Step(type='Then', action='I have <left> cucumbers')
        ],
        examples=[
            Table(
                parameters=['have', 'eat', 'left'],
                values=[
                    ['12', 5, 7.0],
                    ["8.0", 3.0, "5"]
                ]
            )
        ]
    )


There is also an option to build Step from dict(and use your own file format/preprocessor)

.. code-block:: python

    from pytest_bdd.struct_bdd.model import Step

    cukes = Step.parse_obj(
            dict(
                Name="Examples are substituted",
                Steps=[
                    dict(Given='I have <have> cucumbers'),
                    dict(And='I eat <eat> cucumbers'),
                    dict(Then='I have <left> cucumbers')
                ],
                Examples=[
                    dict(
                        Table=dict(
                            Parameters=['have', 'eat', 'left'],
                            Values=[
                                ['12', 5, 7.0],
                                ["8.0", 3.0, "5"]
                            ]
                        )
                    )
                ]
            )
        )

    @cukes
    def test(feature:Feature, scenario):
        assert feature.name == "Examples are substituted"


Example tables could be joined:

.. code-block:: yaml

    Tags:
      - TopTag
    Name: StepName
    Action: "Do first <HeaderA>, <HeaderB>, <HeaderC>"
    Examples:
      - Join:
        - Table:
            Tags:
              - ExampleTagA
            Parameters:
              [ HeaderA, HeaderB ]
            Values:
              - [ A1, B1]
              - [ A2, B2]
        - Table:
            Tags:
              - ExampleTagB
            Parameters:
              [ HeaderB, HeaderC ]
            Values:
              - [ B1, C1 ]
              - [ B2, C2 ]
              - [ B3, C3 ]
    Steps: []

Install StructBDD:

::

    pip install pytest-bdd-ng[struct_bdd]

Reporting
---------

It's important to have nice reporting out of your bdd tests. Cucumber introduced some kind of standard for
`json format <https://www.relishapp.com/cucumber/cucumber/docs/json-output-formatter>`_
which can be used for, for example, by `this <https://plugins.jenkins.io/cucumber-testresult-plugin/>`_ Jenkins
plugin.

To have an output in json format:

::

    pytest --cucumberjson=<path to json report>

This will output an expanded (meaning scenario outlines will be expanded to several scenarios) cucumber format.

To enable gherkin-formatted output on terminal, use

::

    pytest --gherkin-terminal-reporter

Allure reporting is also in place https://docs.qameta.io/allure and based on
`allure-pytest` https://pypi.org/project/allure-pytest/ plugin. Usage is same
To install plugin

::

    pip install pytest-bdd-ng[allure]


Test code generation helpers
----------------------------

For newcomers it's sometimes hard to write all needed test code without being frustrated.
To simplify their life, simple code generator was implemented. It allows to create fully functional
but of course empty tests and step definitions for given a feature file.
It's done as a separate console script provided by pytest-bdd package:

::

    pytest --generate --feature <feature file name> .. <feature file nameN>

It will print the generated code to the standard output so you can easily redirect it to the file:

::

    pytest --generate --feature features/some.feature > tests/functional/test_some.py


Advanced code generation
------------------------

For more experienced users, there's smart code generation/suggestion feature. It will only generate the
test code which is not yet there, checking existing tests and step definitions the same way it's done during the
test execution. The code suggestion tool is called via passing additional pytest arguments:

::

    pytest --generate-missing --feature features tests/functional

The output will be like:

::

    ============================= test session starts ==============================
    platform linux2 -- Python 2.7.6 -- py-1.4.24 -- pytest-2.6.2
    plugins: xdist, pep8, cov, cache, bdd, bdd, bdd
    collected 2 items

    Scenario is not bound to any test: "Code is generated for scenarios which are not bound to any tests" in feature "Missing code generation" in /tmp/pytest-552/testdir/test_generate_missing0/tests/generation.feature
    --------------------------------------------------------------------------------

    Step is not defined: "I have a custom bar" in scenario: "Code is generated for scenario steps which are not yet defined(implemented)" in feature "Missing code generation" in /tmp/pytest-552/testdir/test_generate_missing0/tests/generation.feature
    --------------------------------------------------------------------------------
    Please place the code above to the test file(s):

    @scenario('tests/generation.feature', 'Code is generated for scenarios which are not bound to any tests')
    def test_Code_is_generated_for_scenarios_which_are_not_bound_to_any_tests():
        """Code is generated for scenarios which are not bound to any tests."""


    @given("I have a custom bar")
    def I_have_a_custom_bar():
        """I have a custom bar."""

As as side effect, the tool will validate the files for format errors, also some of the logic bugs, for example the
ordering of the types of the steps.


License
-------

This software is licensed under the `MIT license <http://en.wikipedia.org/wiki/MIT_License>`_.

© 2013-2022 Oleg Pidsadnyi, Anatoly Bubenkov, Konstantin Goloveshko and others
