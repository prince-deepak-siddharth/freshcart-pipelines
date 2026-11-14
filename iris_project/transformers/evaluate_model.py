import pandas as pd
from sklearn.metrics import accuracy_score, confusion_matrix, precision_recall_fscore_support

if 'transformer' not in globals() or 'test' not in globals():
    try:
        from mage_ai.data_preparation.decorators import test, transformer
    except ImportError:
        def transformer(func):
            return func

        def test(func):
            return func

CLASS_NAMES = ['setosa', 'versicolor', 'virginica']


@transformer
def evaluate(result: dict, *args, **kwargs) -> pd.DataFrame:
    """Second branch after train_model: confusion matrix + per-class metrics table."""
    pred = result['predictions']
    y_true, y_pred = pred['target'], pred['predicted']

    cm = pd.DataFrame(confusion_matrix(y_true, y_pred, labels=[0, 1, 2]),
                      index=[f'true_{c}' for c in CLASS_NAMES],
                      columns=[f'pred_{c}' for c in CLASS_NAMES])
    print('Confusion matrix (rows = true, columns = predicted):')
    print(cm.to_string())

    p, r, f, support = precision_recall_fscore_support(y_true, y_pred, labels=[0, 1, 2], zero_division=0)
    metrics = pd.DataFrame({'class': CLASS_NAMES, 'precision': p.round(3), 'recall': r.round(3),
                            'f1': f.round(3), 'support': support})
    metrics.loc[len(metrics)] = ['accuracy', None, None, round(accuracy_score(y_true, y_pred), 3), len(pred)]
    print('\nMetrics:')
    print(metrics.to_string(index=False))
    return metrics


@test
def test_metrics(output, *args) -> None:
    assert output is not None, 'The output is undefined'
    assert len(output) == 4, 'Expected 3 class rows + 1 accuracy row'
    assert int(output.loc[output['class'] != 'accuracy', 'support'].sum()) == 30
