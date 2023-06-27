"""Test scenario decorator."""

from tests.utils import assert_outcomes


def test_scenario_not_found(testdir, pytest_params):
    """Test the situation when scenario is not found."""
    testdir.makefile(
        ".feature",
        not_found="""\
            Feature: Scenario is not found
            """,
    )
    testdir.makepyfile(
        """\
        import re
        import pytest
        from pytest_bdd import parsers, given, then, scenario

        @scenario("not_found.feature", "NOT FOUND")
        def test_not_found():
            pass
        """
    )
    result = testdir.runpytest_subprocess(*pytest_params)

    assert_outcomes(result, skipped=1)


def test_scenario_comments(testdir):
    """Test comments inside scenario."""
    testdir.makefile(
        ".feature",
        comments="""\
            Feature: Comments
                Scenario: Comments
                    # Comment
                    Given I have a bar

                Scenario: Strings that are not comments
                    Given comments should be at the start of words
                    Then this is not a#comment
                    And this is not "#acomment"

            """,
    )

    testdir.makepyfile(
        """\
        import re
        import pytest
        from pytest_bdd import parsers, given, then, scenario

        @scenario("comments.feature", "Comments")
        def test_1():
            pass

        @scenario("comments.feature", "Strings that are not comments")
        def test_2():
            pass


        @given("I have a bar")
        def bar():
            return "bar"


        @given("comments should be at the start of words")
        def comments():
            pass


        @then(parsers.parse("this is not {acomment}"))
        def a_comment(acomment):
            assert re.search("a.*comment", acomment)
        """
    )

    result = testdir.runpytest()

    result.assert_outcomes(passed=2)


def test_simple(testdir, pytest_params):
    """Test scenario decorator with a standard usage."""
    testdir.makefile(
        ".feature",
        simple="""
        Feature: Simple feature
            Scenario: Simple scenario
                Given I have a bar
        """,
    )
    testdir.makepyfile(
        """
        from pytest_bdd import scenario, given, then

        @scenario("simple.feature", "Simple scenario")
        def test_simple():
            pass

        @given("I have a bar")
        def bar():
            return "bar"

        @then("pass")
        def bar():
            pass
        """
    )
    result = testdir.runpytest_subprocess(*pytest_params)
    result.assert_outcomes(passed=1)


def test_datatable_to_list_of_dicts(testdir, pytest_params):
    """Tests that datatables can be covnerted to lists of dicts
    """

    testdir.makefile(
        ".feature",
        simple="""
        Feature: Datatables can be converted to lists of strings
            Scenario: Scenario with a datatable
                Given I have a datatable with 3 rows
                | Header1 | Header2 |
                | r1c1    | r2c2    |
                | 1       | 2       |
                Then it is parsed into a list with 2 entries

            Scenario: Scenario with an emtpy datatable
                Given I have a datatable with 1 rows
                | Header1 | Header2 |
                Then it is parsed into an empty list
    """)
    testdir.makepyfile(
        """
        from pytest_bdd import scenario, given, then, parsers

        @scenario("datatable_to_list_of_dicts")

        @given(
            parsers.parse("I have a datatable with {n_row} rows"),
            target_fixture="data_table"
        )
        def dt_with_3_rows(step):
            result = steps.data_table
            return result

        @then("it is parsed into a list with 2 entries")
        def parsed_3_entries(data_table):
            actual = list(data_table.to_records())
            expected = [
                {"Header1": "r1c1", "Header2": "r1c2"},
                {"Header1": "1", "Header2": "2"}
            ]
            assert actual == expected

        @then("it is parsed into an empty list")
        def parsed_empty_list(data_table):
            actual = list(data_table.to_records())
            expected = []
            assert actual == expected
        """
    )
    result = testdir.runpytest_subprocess(*pytest_params)
    result.assert_outcomes(passed=2)
