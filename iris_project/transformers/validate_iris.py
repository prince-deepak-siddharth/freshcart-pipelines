import pandas as pd

if 'transformer' not in globals() or 'test' not in globals():
    try:
        from mage_ai.data_preparation.decorators import test, transformer
    except ImportError:
        def transformer(func):
            return func

        def test(func):
            return func


@transformer
def validate(df: pd.DataFrame, *args, **kwargs) -> pd.DataFrame:
    """Pass the data through unchanged; the @test below is the actual check."""
    print(f'validate_iris: {len(df)} rows, {df["target"].nunique()} classes, '
          f'{int(df.isna().sum().sum())} missing values')
    return df


@test
def test_no_missing_and_three_classes(output, *args) -> None:
    assert output is not None, 'The output is undefined'
    assert output.isna().sum().sum() == 0, 'The data contains missing values'
    assert output['target'].nunique() == 3, f'Expected 3 classes, found {output["target"].nunique()}'
