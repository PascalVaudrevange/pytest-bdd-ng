"""Test feature base dir."""
import pytest

NOT_EXISTING_FEATURE_PATHS = [".", "/does/not/exist/"]


def test_feature_path_ok(testdir):
    base_dir = "features"
    prepare_testdir(testdir, base_dir)

    result = testdir.runpytest("-k", "test_ok_by_ini")
    result.assert_outcomes(passed=2)


@pytest.mark.parametrize("base_dir", NOT_EXISTING_FEATURE_PATHS)
def test_feature_path_by_param_ok(testdir, base_dir):
    """If ini config is incorrect but param path is fine it should be able
    to find features"""
    prepare_testdir(testdir, base_dir)

    result = testdir.runpytest("-k", "test_ok_by_param")
    result.assert_outcomes(passed=2)


def prepare_testdir(testdir, ini_base_dir):
    testdir.makeini(
        f"""
        [pytest]
        bdd_features_base_dir={ini_base_dir}
        """
    )

    feature_file = testdir.mkdir("features").join("steps.feature")
    feature_file.write(
        # language=gherkin
        """
        Feature: Feature path
            Scenario: When scenario found
                Given found
        """
    )

    testdir.makepyfile(
        # language=python
        f"""\
        import pytest
        from pathlib import Path
        from pytest_bdd.parser import GherkinParser

        from pytest_bdd import scenario, scenarios

        FEATURE = 'steps.feature'


        @pytest.fixture(params=[
            'When scenario found',
        ])
        def scenario_name(request):
            return request.param

        @pytest.mark.parametrize(
            'multiple', [True, False]
        )
        def test_not_found_by_ini(scenario_name, multiple):
            with pytest.raises(IOError) as exc:
                if multiple:
                    scenarios(FEATURE, parser_type=GherkinParser)
                else:
                    scenario(FEATURE, scenario_name, parser_type=GherkinParser)
            assert str((Path('{ini_base_dir}') / FEATURE).resolve().as_posix()) in str(Path(str(exc.value.filename)).as_posix())


        @pytest.mark.parametrize(
            'multiple', [True, False]
        )
        def test_ok_by_ini(scenario_name, multiple):
            # Shouldn't raise any exception
            if multiple:
                scenarios(FEATURE, parser_type=GherkinParser)
            else:
                scenario(FEATURE, scenario_name, parser_type=GherkinParser)

        @pytest.mark.parametrize(
            'multiple', [True, False]
        )
        @pytest.mark.parametrize(
            'param_base_dir', [
                '.',
                '/does/not/exist/',
            ]
        )
        def test_not_found_by_param(scenario_name, param_base_dir, multiple):
            with pytest.raises(IOError) as exc:
                if multiple:
                    scenarios(FEATURE, features_base_dir=param_base_dir)
                else:
                    scenario(FEATURE, scenario_name, features_base_dir=param_base_dir)
            assert str((Path(param_base_dir) / FEATURE).resolve().as_posix()) in str(Path(str(exc.value.filename)).as_posix())

        @pytest.mark.parametrize(
            'multiple', [True, False]
        )
        def test_ok_by_param(scenario_name, multiple):
            # Shouldn't raise any exception no matter of bdd_features_base_dir in ini
            if multiple:
                scenarios(FEATURE, features_base_dir='features')
            else:
                scenario(FEATURE, scenario_name, features_base_dir='features')
        """
    )
