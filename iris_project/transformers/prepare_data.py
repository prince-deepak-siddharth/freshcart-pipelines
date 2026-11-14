import pandas as pd
from sklearn.model_selection import train_test_split

if 'transformer' not in globals() or 'test' not in globals():
    try:
        from mage_ai.data_preparation.decorators import test, transformer
    except ImportError:
        def transformer(func):
            return func

        def test(func):
            return func

TEST_SIZE = 0.2
RANDOM_STATE = 42


@transformer
def transform(df: pd.DataFrame, *args, **kwargs) -> pd.DataFrame:
    """Add a 'split' column that marks every row as 'train' or 'test' (80/20, stratified)."""
    train_idx, test_idx = train_test_split(
        df.index, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=df['target']
    )
    out = df.copy()
    out['split'] = 'train'
    out.loc[test_idx, 'split'] = 'test'
    return out


@test
def test_split(output, *args) -> None:
    assert output is not None, 'The output is undefined'
    n_train = int((output['split'] == 'train').sum())
    n_test = int((output['split'] == 'test').sum())
    assert n_train == 120, f'Expected 120 training rows, got {n_train}'
    assert n_test == 30, f'Expected 30 test rows, got {n_test}'
