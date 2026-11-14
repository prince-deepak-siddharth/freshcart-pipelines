from pathlib import Path

if 'data_exporter' not in globals() or 'test' not in globals():
    try:
        from mage_ai.data_preparation.decorators import data_exporter, test
    except ImportError:
        def data_exporter(func):
            return func

        def test(func):
            return func

OUTPUT_FILE = 'iris_predictions.csv'


@data_exporter
def export_data(result: dict, *args, **kwargs) -> None:
    """Write the test-set predictions to iris_predictions.csv (only reached if train_model's test passed)."""
    result['predictions'].to_csv(OUTPUT_FILE, index=False)
    print(f'saved {len(result["predictions"])} predictions -> {OUTPUT_FILE}')


@test
def test_file_written(*args) -> None:
    assert Path(OUTPUT_FILE).exists(), f'{OUTPUT_FILE} was not created'
