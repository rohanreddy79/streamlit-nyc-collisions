"""Headless smoke test: run app.py on a synthetic CSV with Streamlit's AppTest
and exercise every branch of the "dangerous streets" select box."""
import os
import subprocess
import sys

import pytest
from streamlit.testing.v1 import AppTest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture(scope="module")
def sample_csv(tmp_path_factory):
    path = str(tmp_path_factory.mktemp("data") / "sample.csv")
    subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "make_sample_csv.py"), path, "500"], check=True)
    os.environ["DATA_URL"] = path
    return path


@pytest.mark.parametrize("affected", ["Pedestrians", "Cyclists", "Motorists"])
def test_app_runs_for_every_affected_type(sample_csv, affected):
    at = AppTest.from_file(os.path.join(ROOT, "app.py"), default_timeout=60).run()
    assert not at.exception, at.exception
    at.selectbox[0].set_value(affected).run()
    assert not at.exception, at.exception
    # the top-5 table is the last dataframe on the page and must not be empty
    assert len(at.dataframe[-1].value) > 0
