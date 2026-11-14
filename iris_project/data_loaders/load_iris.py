import pandas as pd
from sklearn.datasets import load_iris as _sk_load_iris

# Inside Mage the decorators are already injected; outside Mage (pytest, CI)
# they are missing, so fall back to the real ones or to harmless no-ops.
if 'data_loader' not in globals() or 'test' not in globals():
    try:
        from mage_ai.data_preparation.decorators import data_loader, test
    except ImportError:  # Mage not installed: make the decorators no-ops
        def data_loader(func):
            return func

        def test(func):
            return func


@data_loader
def load_data(*args, **kwargs) -> pd.DataFrame:
    """Load the Iris dataset (150 rows, 4 features + target) as a DataFrame."""
    return _sk_load_iris(as_frame=True).frame


@test
def test_output(output, *args) -> None:
    assert output is not None, 'The output is undefined'
    assert len(output) == 150, f'Expected 150 rows, got {len(output)}'
    assert 'target' in output.columns, 'Missing target column'
