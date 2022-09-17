from math import fabs
import os
import pandas
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import precision_score
from pathlib import Path
from pprint import pprint

DATA_DIRECTORY =  os.path.join(Path(__file__).parent.parent, 'data')

PREDICTORS = ['close', 'volume']

# How many individual decisions trees to train.
# Train X amount and average the results
# More than 500 might be overkill
# Default is 100
N_ESTIMATORS = 200

# Prevents the data from tightly fitting itself to the input data.
# The less tightly the data fits the more generalize it can be
MIN_SAMPLES_SPLIT = 200

# This ensures every time you run the model it will give you the same results.
RANDOM_STATE=1

# Set the precision higher for more accurate predictions
BACK_TEST_PRECISION = 0.7

# Set lower for better predictions
BACK_TEST_STEP_INDEX = 5


def read_data():
    file_path = os.path.join(DATA_DIRECTORY, 'prices.csv')
    data = pandas.read_csv(file_path, sep='\t')
    return data


def prepare_data(data):
    data = data.rename(columns={'last_trade': 'close','rolling_24_hour_volume': 'volume' })
    data['next_price'] = data['close'].shift(-1)
    data['target'] = data.rolling(2).apply(lambda x: x.iloc[1] > x.iloc[0])['close']
    data.pop('pair')
    data.pop('status')
    data.pop('ask')
    data.pop('bid')
    data = data.iloc[1:]
    return data


def back_test(data, model, predictors, start=1000, step=750):
    start = int(len(data) / 3)

    predictions_combined = []

    for i in range(start, data.shape[0], BACK_TEST_STEP_INDEX):
        train = data.iloc[0:i].copy()
        test = data.iloc[i:(i+step)].copy()

        model.fit(train[predictors], train['target'])
        predictions = model.predict_proba(test[predictors])[:,1]
        predictions = pandas.Series(predictions, index=test.index)
        predictions[predictions > BACK_TEST_PRECISION] = 1
        predictions[predictions <= BACK_TEST_PRECISION] = 0

        combined = pandas.concat({'target': test['target'], 'predictions': predictions}, axis=1)
        predictions_combined.append(combined)

    return pandas.concat(predictions_combined)


def will_next_price_increase(data):
    model = RandomForestClassifier(
        n_estimators=N_ESTIMATORS,
        min_samples_split=MIN_SAMPLES_SPLIT,
        random_state=RANDOM_STATE
    )

    pprint(data)
    index_separation = int(len(data) / 5)
    # Use data until the last X rows
    train = data.iloc[:-index_separation]

    # Use the last X rows for testing
    test = data.iloc[-index_separation:]

    model.fit(train[PREDICTORS], train['target'])

    predictions = model.predict(test[PREDICTORS])
    predictions = pandas.Series(predictions, index=test.index)

    # combined = pandas.concat({'target': test['target'], 'predictions': predictions}, axis=1)

    # combined.plot()
    # plt.show()

    weekly_mean = data.rolling(7).mean()
    quarterly_mean = data.rolling(90).mean()
    annual_mean = data.rolling(365).mean()

    weekly_trend = data.shift(1).rolling(7).mean()['target']

    data['weekly_trend'] = weekly_trend

    data['weekly_mean'] = weekly_mean['close'] / data['close']
    # data['quarterly_mean'] = quarterly_mean['close'] / data['close']
    # data['annual_mean'] = annual_mean['close'] / data['close']

    # data['annual_weekly_mean'] = data['annual_mean'] / data['weekly_mean']
    # data['annual_quarterly_mean'] = data['annual_mean'] / data['quarterly_mean']

    data['low_close_ratio'] = data['close'] / data['close']

    full_predictors = PREDICTORS + [
        'low_close_ratio',
        'weekly_mean',
        'weekly_trend',
        # 'annual_mean',
        # 'annual_weekly_mean',
        # 'annual_quarterly_mean',
    ]

    predictions = back_test(data.iloc[7:], model, full_predictors)

    accuracy = precision_score(predictions['target'], predictions['predictions'])
    print('Accuracy:', accuracy)

    trading_count = predictions['predictions'].value_counts()
    print('Trading Count:', trading_count)

    will_increase_predict = bool(predictions['predictions'].iloc[-1])
    print('Will Increase predict:', will_increase_predict)

    will_increase_target = bool(predictions['target'].iloc[-1])
    print('Will Increase target:', will_increase_target)
    return will_increase_target


def predict():
    data = read_data()
    if len(data) < 50:
        return False
    prepared_data = prepare_data(data)
    return will_next_price_increase(prepared_data)
