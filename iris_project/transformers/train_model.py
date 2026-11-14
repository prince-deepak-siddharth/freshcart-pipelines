import pandas as pd
from sklearn.metrics import accuracy_score
from sklearn.tree import DecisionTreeClassifier

if 'transformer' not in globals() or 'test' not in globals():
    try:
        from mage_ai.data_preparation.decorators import test, transformer
    except ImportError:
        def transformer(func):
            return func

        def test(func):
            return func

FEATURES = ['sepal length (cm)', 'sepal width (cm)', 'petal length (cm)', 'petal width (cm)']
MIN_ACCURACY = 0.90  # the quality gate


@transformer
def train(df: pd.DataFrame, *args, **kwargs) -> dict:
    """Train a decision tree. max_depth is a runtime variable: --runtime-vars '{"max_depth": 3}'."""
    max_depth = int(kwargs.get('max_depth', 3))
    train_df = df[df['split'] == 'train']
    test_df = df[df['split'] == 'test']

    model = DecisionTreeClassifier(max_depth=max_depth, random_state=42)
    model.fit(train_df[FEATURES], train_df['target'])

    predictions = test_df.copy()
    predictions['predicted'] = model.predict(test_df[FEATURES])
    accuracy = float(accuracy_score(predictions['target'], predictions['predicted']))
    print(f'max_depth={max_depth}  test accuracy={accuracy:.4f}')

    return {'model': model, 'predictions': predictions,
            'test_accuracy': accuracy, 'max_depth': max_depth}


@test
def test_accuracy(output, *args) -> None:
    """If this fails, Mage stops the pipeline and save_results never runs."""
    assert output is not None, 'The output is undefined'
    acc = output['test_accuracy']
    assert acc >= MIN_ACCURACY, (
        f'test_accuracy {acc:.3f} is below {MIN_ACCURACY} (max_depth={output["max_depth"]})')
