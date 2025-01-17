import json
from pathlib import Path

from pytest import mark, param

from pytest_bdd.model.messages import Pickle

test_data = Path(__file__).parent.parent.parent / "testdata"


@mark.parametrize(
    "pickle_path",
    map(
        lambda file: param(file, id=file.name),  # type: ignore[no-any-return]
        (test_data / "good").glob("*.pickles.ndjson"),
    ),
)
def test_simple_load_pickle(pickle_path: Path):
    with pickle_path.open(mode="r") as pickle_file:
        for pickle_line in pickle_file:
            pickle_data = json.loads(pickle_line)["pickle"]
            pickle = Pickle.parse_obj(pickle_data)
            assert isinstance(pickle, Pickle)

            dumped_pickle_data = json.loads(pickle.json(by_alias=True, exclude_none=True))

            assert pickle_data == dumped_pickle_data
