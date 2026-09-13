"""
Time series prediction models for grid frequency data.

Trains multiple regression models (Linear, Polynomial degree 2/3, Random Forest,
Moving Average) on historical frequency data and predicts frequency at arbitrary
future timestamps.
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import PolynomialFeatures
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')


class FrequencyPredictor:
    """
    Multi-model predictor for frequency time series data.
    """

    def __init__(self):
        self.models = {}
        self.is_fitted = False
        self.train_data = None

    def fit(self, df):
        """
        Fit multiple models on the training data.
        df should have 'time_minutes' and 'frequency' columns.
        """
        self.train_data = df.copy()

        X = df[['time_minutes']].values
        y = df['frequency'].values

        # 1. Linear Regression
        self.models['linear'] = LinearRegression()
        self.models['linear'].fit(X, y)

        # 2. Polynomial Regression (degree 2)
        poly_features = PolynomialFeatures(degree=2)
        X_poly = poly_features.fit_transform(X)
        self.models['polynomial'] = LinearRegression()
        self.models['polynomial'].fit(X_poly, y)
        self.models['poly_features'] = poly_features

        # 3. Polynomial Regression (degree 3)
        poly_features_3 = PolynomialFeatures(degree=3)
        X_poly_3 = poly_features_3.fit_transform(X)
        self.models['polynomial_3'] = LinearRegression()
        self.models['polynomial_3'].fit(X_poly_3, y)
        self.models['poly_features_3'] = poly_features_3

        # 4. Random Forest
        self.models['random_forest'] = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.models['random_forest'].fit(X, y)

        # 5. Moving Average (for reference)
        window = min(10, len(df) // 10)
        self.models['moving_avg_window'] = window

        self.is_fitted = True

    def predict(self, time_minutes, model_type='linear'):
        """
        Predict frequency at given time(s) using specified model.
        time_minutes can be a single value or array.
        """
        if not self.is_fitted:
            raise ValueError("Model not fitted yet. Call fit() first.")

        if isinstance(time_minutes, (int, float)):
            time_minutes = np.array([[time_minutes]])
        else:
            time_minutes = np.array(time_minutes).reshape(-1, 1)

        if model_type == 'linear':
            return self.models['linear'].predict(time_minutes)

        elif model_type == 'polynomial':
            X_poly = self.models['poly_features'].transform(time_minutes)
            return self.models['polynomial'].predict(X_poly)

        elif model_type == 'polynomial_3':
            X_poly = self.models['poly_features_3'].transform(time_minutes)
            return self.models['polynomial_3'].predict(X_poly)

        elif model_type == 'random_forest':
            return self.models['random_forest'].predict(time_minutes)

        elif model_type == 'moving_average':
            predictions = []
            for tm in time_minutes:
                window = self.models['moving_avg_window']
                distances = np.abs(self.train_data['time_minutes'].values - tm[0])
                nearest_indices = np.argsort(distances)[:window]
                avg = self.train_data.iloc[nearest_indices]['frequency'].mean()
                predictions.append(avg)
            return np.array(predictions)

        else:
            raise ValueError(f"Unknown model type: {model_type}")

    def predict_range(self, start_minutes, end_minutes, points=100, model_type='linear'):
        """
        Predict frequency over a range of times.
        """
        time_range = np.linspace(start_minutes, end_minutes, points)
        predictions = self.predict(time_range, model_type)
        return time_range, predictions

    def get_model_performance(self, test_df=None):
        """
        Calculate performance metrics for all models.
        """
        if test_df is None:
            test_df = self.train_data

        X_test = test_df[['time_minutes']].values
        y_test = test_df['frequency'].values

        performance = {}

        for model_name in ['linear', 'polynomial', 'polynomial_3', 'random_forest',
                            'moving_average']:
            y_pred = self.predict(X_test.flatten(), model_type=model_name)

            mse = np.mean((y_test - y_pred) ** 2)
            rmse = np.sqrt(mse)
            mae = np.mean(np.abs(y_test - y_pred))

            ss_res = np.sum((y_test - y_pred) ** 2)
            ss_tot = np.sum((y_test - np.mean(y_test)) ** 2)
            r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

            performance[model_name] = {
                'RMSE': rmse,
                'MAE': mae,
                'R²': r2
            }

        return performance


class FrequencyAnalyzer:
    """
    Analyze frequency patterns and anomalies.
    """

    @staticmethod
    def detect_anomalies(df, threshold=3):
        """
        Detect anomalies using z-score method.
        """
        df = df.copy()
        mean = df['frequency'].mean()
        std = df['frequency'].std()

        df['z_score'] = (df['frequency'] - mean) / std
        df['is_anomaly'] = np.abs(df['z_score']) > threshold

        return df

    @staticmethod
    def get_statistics(df):
        """
        Get basic statistics about frequency.
        """
        stats = {
            'mean': df['frequency'].mean(),
            'median': df['frequency'].median(),
            'std': df['frequency'].std(),
            'min': df['frequency'].min(),
            'max': df['frequency'].max(),
            'range': df['frequency'].max() - df['frequency'].min(),
            'count': len(df)
        }
        return stats

    @staticmethod
    def find_peak_hours(df):
        """
        Find time periods with highest/lowest frequencies.
        """
        if 'datetime' in df.columns:
            df = df.copy()
            df['hour'] = df['datetime'].dt.hour
            hourly_avg = df.groupby('hour')['frequency'].mean()

            return {
                'peak_hour': hourly_avg.idxmax(),
                'peak_frequency': hourly_avg.max(),
                'lowest_hour': hourly_avg.idxmin(),
                'lowest_frequency': hourly_avg.min(),
                'hourly_average': hourly_avg.to_dict()
            }
        return None


if __name__ == "__main__":
    print("FrequencyPredictor and FrequencyAnalyzer loaded.")
    print("Import this module and call FrequencyPredictor().fit(your_dataframe)")
    print("your_dataframe needs 'time_minutes' and 'frequency' columns.")
