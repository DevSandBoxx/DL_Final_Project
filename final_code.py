# -*- coding: utf-8 -*-
"""final.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1PF3wkRY8RxoVXBEwfYD-Fu1aMeKM0zrI
"""

# from google.colab import drive
# drive.mount('/content/drive')

# Commented out IPython magic to ensure Python compatibility.
# Add CS7643 shortcut to drive
# %cd "drive/MyDrive/CS7643"

# Commented out IPython magic to ensure Python compatibility.
# %load_ext autoreload
# %autoreload 2

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import ast
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import LabelEncoder

# !pip install scikit-learn --upgrade
# !pip install seaborn

"""# Helper Functions"""

def clean_embedding_string(s):
  s = s[1:-1].strip()
  return [float(i) for i in s.split()]


# Preprocess data. Drop first column. Parse embeddings and one-hot vectors
# Expand lists to columns. Concat everything and drop nulls
def preprocessing(data):
  data = data.drop(data.columns[0], axis=1)

  data['title_embeddings'] = data['title_embeddings'].apply(clean_embedding_string)

  data['one_hot_artist'] = data['one_hot_artist'].apply(ast.literal_eval)
  data['one_hot_artist'] = data['one_hot_artist'].apply(lambda x: [float(i) for i in x])

  data['one_hot_genre'] = data['one_hot_genre'].apply(ast.literal_eval)
  data['one_hot_genre'] = data['one_hot_genre'].apply(lambda x: [float(i) for i in x])

  title_embeddings = pd.DataFrame(data['title_embeddings'].tolist(),
                                columns=[f'title_embedding_{i}'
                                         for i in range(len(data['title_embeddings'][0]))])
  artist_one_hot = pd.DataFrame(data['one_hot_artist'].tolist(),
                                columns=[f'artist_{i}'
                                         for i in range(len(data['one_hot_artist'][0]))])
  genre_one_hot = pd.DataFrame(data['one_hot_genre'].tolist(),
                                columns=[f'genre_{i}'
                                         for i in range(len(data['one_hot_genre'][0]))])
  regular_features = [
    'duration', 'danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness',
    'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo', 'duration_mins',
    'release_year', 'release_month', 'release_day', 'popularity'
  ]

  data = pd.concat([data[regular_features], title_embeddings, artist_one_hot, genre_one_hot], axis=1)

  cols_to_check = ['release_year', 'release_month', 'release_day']
  data = data.dropna(subset=cols_to_check)


  X = data.drop('popularity', axis=1)
  y = data['popularity']

  return X, y

# Preprocess without encodings, extract title embeddings, combine original features with preprocessed date columns.
# Split numerical and categorical columns

def preprocessing_no_encodings(original_data, preprocessed_data):
  original_data = original_data.drop(original_data.columns[0], axis=1)

  preprocessed_data['title_embeddings'] = preprocessed_data['title_embeddings'].apply(clean_embedding_string)

  title_embeddings = pd.DataFrame(preprocessed_data['title_embeddings'].tolist(),
                                columns=[f'title_embedding_{i}'
                                         for i in range(len(preprocessed_data['title_embeddings'][0]))])

  regular_features = [
    'duration', 'danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness',
    'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo', 'duration_mins',
    'popularity', 'artist_name', 'genre'
  ]

  new_data = pd.concat([original_data[regular_features],
                        preprocessed_data[['release_year', 'release_month', 'release_day']],
                        title_embeddings],
                       axis=1)

  cols_to_check = ['release_year', 'release_month', 'release_day']
  new_data = new_data.dropna(subset=cols_to_check)


  numerical_columns = ['duration', 'danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness',
    'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo', 'duration_mins', 'release_year', 'release_month', 'release_day']
  categorical_columns = ['artist_name', 'genre']


  X = new_data.drop('popularity', axis=1)
  y = new_data['popularity']

  return X[numerical_columns], X[categorical_columns], y

# Build and train linear regression model
def train_linear_regression(X_train, X_test, y_train, y_test):
  lr_regressor = LinearRegression()
  lr_regressor.fit(X_train, y_train)

  y_pred = lr_regressor.predict(X_test)

  mse = mean_squared_error(y_test, y_pred)
  r2 = r2_score(y_test, y_pred)

  metrics = [f"Mean Squared Error: {mse:.4f}", f"R² Score: {r2:.4f}"]
  print(metrics)
  return lr_regressor, y_pred

# Build and train Rnadom Forest model
def train_random_forest(X_train, X_test, y_train, y_test, n_estimators=100, random_state=42, n_jobs=-1):
  model = RandomForestRegressor(n_estimators=n_estimators, random_state=random_state, n_jobs=n_jobs)
  model.fit(X_train, y_train)
  y_pred = model.predict(X_test)

  mse = mean_squared_error(y_test, y_pred)
  r2 = r2_score(y_test, y_pred)

  metrics = [f"Mean Squared Error: {mse:.4f}", f"R² Score: {r2:.4f}"]
  print(metrics)
  return model, y_pred

import torch
import torch.nn as nn
import torch.optim as optim

# Build standard MLP model as a 3 layer neural network
class MLP(nn.Module):
    def __init__(self, input_dim):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 1)
        )

    def forward(self, x):
        return self.net(x).squeeze()

# Train the standard mlp model using ADAM and MSE Loss
def train_mlp(X_train, X_test, y_train, y_test, epochs=50, lr=1e-3):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    X_train_t = torch.tensor(X_train.values, dtype=torch.float32).to(device)
    X_test_t = torch.tensor(X_test.values, dtype=torch.float32).to(device)
    y_train_t = torch.tensor(y_train.values, dtype=torch.float32).to(device)
    y_test_t = torch.tensor(y_test.values, dtype=torch.float32).to(device)

    model = MLP(input_dim=X_train.shape[1]).to(device)
    optimizer = optim.Adam(model.parameters(), lr=lr)
    criterion = nn.MSELoss()

    for epoch in range(epochs):
        model.train()
        optimizer.zero_grad()
        output = model(X_train_t)
        loss = criterion(output, y_train_t)
        loss.backward()
        optimizer.step()

    model.eval()
    with torch.no_grad():
        preds = model(X_test_t)
        mse = criterion(preds, y_test_t).item()
        r2 = r2_score(y_test_t.cpu().numpy(), preds.cpu().numpy())

    print(f"[MLP] MSE: {mse:.4f} | R²: {r2:.4f}")
    return model

# Train the standard mlp model using ADAM and MSE Loss, but with scaling on the input data
def train_mlp_standard_scale(X_train, X_test, y_train, y_test, epochs=50, lr=1e-3):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    X_train_t = torch.tensor(X_train, dtype=torch.float32).to(device)
    X_test_t = torch.tensor(X_test, dtype=torch.float32).to(device)
    y_train_t = torch.tensor(y_train, dtype=torch.float32).squeeze().to(device)
    y_test_t = torch.tensor(y_test, dtype=torch.float32).squeeze().to(device)

    # Define model, optimizer, and loss function
    model = MLP(input_dim=X_train.shape[1]).to(device)
    optimizer = optim.Adam(model.parameters(), lr=lr)
    criterion = nn.MSELoss()

    train_losses = []
    val_losses = []

    # Training loop
    for epoch in range(epochs):
        model.train()
        optimizer.zero_grad()
        output = model(X_train_t)
        train_loss = criterion(output, y_train_t)
        train_loss.backward()
        optimizer.step()

        train_losses.append(train_loss.item())

        # Validation
        model.eval()
        with torch.no_grad():
            preds = model(X_test_t)
            val_loss = criterion(preds, y_test_t).item()
            val_losses.append(val_loss)

        if (epoch + 1) % 100 == 0:
            r2 = r2_score(y_test_t.cpu().numpy(), preds.cpu().numpy())
            print(f"Epoch {epoch+1}/{epochs} | Train Loss: {train_loss.item():.4f} | Validation Loss: {val_loss:.4f} | R²: {r2:.4f}")

    print(f"Final [MLP] MSE: {val_loss:.4f} | R²: {r2:.4f}")

    return model, train_losses, val_losses, preds.cpu().numpy()

class MLPWithEmbeddings(nn.Module):
    def __init__(self, num_features, cat_dims, embed_dim=16):
        super().__init__()
        # Create embedding layers for each categorical feature
        self.embeddings = nn.ModuleList(
            [nn.Embedding(dim, embed_dim) for dim in cat_dims]
        )
        total_embed = embed_dim * len(cat_dims)
        self.fc = nn.Sequential(
            nn.Linear(num_features + total_embed, 512),
            nn.ReLU(),
            nn.Dropout(0.6),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(128, 1),
        )

    def forward(self, x_num, x_cat):
        embedded = []
        for i, emb in enumerate(self.embeddings):
            # Ensure indices are within bounds
            x_cat_i = x_cat[:, i].clamp(0, self.embeddings[i].num_embeddings - 1)
            embedded.append(emb(x_cat_i))

        # Concatenate embedded categorical features with numerical features
        x = torch.cat(embedded + [x_num], dim=1)
        return self.fc(x).squeeze()

# Replicate the above functionality but for the input data and MLP model that involves custom embeddings
def train_mlp_with_embeddings(
    X_train_num,
    X_test_num,
    X_train_cat,
    X_test_cat,
    y_train,
    y_test,
    cat_dims,
    epochs=50,
    lr=1e-3,
):
    # Force CPU mode to avoid CUDA errors
    device = torch.device("cpu")
    torch.cuda.is_available = (
        lambda: False
    )

    print(f"X_train_num shape: {X_train_num.shape if hasattr(X_train_num, 'shape') else 'unknown'}")
    print(f"X_train_cat shape: {X_train_cat.shape if hasattr(X_train_cat, 'shape') else 'unknown'}")
    print(f"cat_dims: {cat_dims}")

    # Convert data to numpy
    if isinstance(X_train_num, torch.Tensor):
        X_train_num = X_train_num.cpu().numpy()
    if isinstance(X_test_num, torch.Tensor):
        X_test_num = X_test_num.cpu().numpy()
    if isinstance(X_train_cat, torch.Tensor):
        X_train_cat = X_train_cat.cpu().numpy()
    if isinstance(X_test_cat, torch.Tensor):
        X_test_cat = X_test_cat.cpu().numpy()
    if isinstance(y_train, torch.Tensor):
        y_train = y_train.cpu().numpy()
    if isinstance(y_test, torch.Tensor):
        y_test = y_test.cpu().numpy()

    X_train_num = torch.tensor(X_train_num, dtype=torch.float32)
    X_test_num = torch.tensor(X_test_num, dtype=torch.float32)

    # Verify categorical data is in bounds and fix if needed
    for i, dim in enumerate(cat_dims):
        if np.max(X_train_cat[:, i]) >= dim:
            print(
                f"Warning: Category {i} has values out of bounds. Max: {np.max(X_train_cat[:, i])}, Allowed: {dim-1}"
            )
            X_train_cat[:, i] = np.clip(X_train_cat[:, i], 0, dim - 1)
        if np.max(X_test_cat[:, i]) >= dim:
            print(
                f"Warning: Category {i} has values out of bounds. Max: {np.max(X_test_cat[:, i])}, Allowed: {dim-1}"
            )
            X_test_cat[:, i] = np.clip(X_test_cat[:, i], 0, dim - 1)

    X_train_cat = torch.tensor(X_train_cat, dtype=torch.long)
    X_test_cat = torch.tensor(X_test_cat, dtype=torch.long)

    # Handle different formats of target variables
    if hasattr(y_train, "values"):
        y_train = torch.tensor(y_train.values, dtype=torch.float32)
    else:
        y_train = torch.tensor(y_train, dtype=torch.float32)

    if hasattr(y_test, "values"):
        y_test = torch.tensor(y_test.values, dtype=torch.float32)
    else:
        y_test = torch.tensor(y_test, dtype=torch.float32)

    # Initialize model, optimizer, and loss function
    model = MLPWithEmbeddings(X_train_num.shape[1], cat_dims)
    optimizer = optim.Adam(model.parameters(), lr=lr)
    criterion = nn.MSELoss()

    train_losses, val_losses = [], []

    # Training loop with gradient clipping
    for epoch in range(epochs):
        model.train()
        optimizer.zero_grad()

        try:
            output = model(X_train_num, X_train_cat)
            loss = criterion(output, y_train)
            loss.backward()

            # Add gradient clipping to prevent exploding gradients
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)

            optimizer.step()

            # Process progress every 10 epochs
            if (epoch + 1) % 10 == 0:
                model.eval()
                with torch.no_grad():
                    train_preds = model(X_train_num, X_train_cat)
                    train_loss = criterion(train_preds, y_train).item()
                    train_losses.append(train_loss)

                    test_preds = model(X_test_num, X_test_cat)
                    test_loss = criterion(test_preds, y_test).item()
                    val_losses.append(test_loss)
                if (epoch + 1) % 1000 == 0:
                    
                    print(
                        f"Epoch {epoch+1}/{epochs}, Train Loss: {train_loss:.4f}, Test Loss: {test_loss:.4f}"
                    )
        except RuntimeError as e:
            print(f"Error during training: {str(e)}")
            print("Attempting to continue with next epoch...")
            continue

    # Final evaluation
    model.eval()
    with torch.no_grad():
        try:
            preds = model(X_test_num, X_test_cat)
            mse = criterion(preds, y_test).item()
            r2 = r2_score(y_test.numpy(), preds.numpy())
            print(f"[MLP + Embeddings] MSE: {mse:.4f} | R²: {r2:.4f}")
        except Exception as e:
            print(f"Error during evaluation: {str(e)}")
            mse = float("nan")
            r2 = float("nan")
            print("[MLP + Embeddings] Failed to compute final metrics")

    return model, train_losses, val_losses, preds.cpu().numpy()


"""#Main Code

##Preprocessing Analysis
"""

original_dataset = pd.read_csv("tiktok.csv")

preprocessed_dataset = pd.read_csv('preprocessed_tiktok.csv')

print(preprocessed_dataset.columns)

# runtime: ≈27sec
X, y = preprocessing(preprocessed_dataset)

print(list(X.columns))

print(X.shape)
print(y.shape)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

"""###Analysis 1
Random Forest Top N features shows artist_397 as the second most important feature. We check to see the most frequent artist names in the original dataset
"""

artist_counts = original_dataset['artist_name'].value_counts()

plt.figure(figsize=(12, 6))
sns.barplot(x=artist_counts.index[:20], y=artist_counts.values[:20])
plt.xticks(rotation=90)
plt.title('Top 20 Artists by Frequency')
plt.xlabel('Artist')
plt.ylabel('Frequency')
plt.savefig('frequent_artist.png', dpi=300, bbox_inches='tight')

# One-hot encode the 'artist' column
one_hot_encoded = pd.get_dummies(original_dataset['artist_name'])

artist_columns = one_hot_encoded.columns.tolist()

# find the artist corresponding to 'artist_397'

artist_index = 397
artist_column_name = artist_columns[artist_index]
print()
print("Artist of index", artist_index, "is", artist_column_name)

"""##Experiment 1 - Linear Regression (~2 min runtime)"""

lr_regressor, linear_regression_y_pred = train_linear_regression(X_train, X_test, y_train, y_test)

"""###Hyperparameter Tuning and Visuals

####Scatter Plot
"""

# y_test and y_pred are actual and predicted values
plt.figure(figsize=(8, 6))

sns.scatterplot(x=y_test, y=linear_regression_y_pred, alpha=0.6, label='Predictions')
plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', label='Ideal Fit')  # ideal line (y=x)

plt.xlabel('Actual Values')
plt.ylabel('Predicted Values')
plt.title('Linear Regression: Actual vs Predicted')
plt.legend()
plt.savefig('linear_results.png', dpi=300, bbox_inches='tight')

"""####Coefficient Evaluation"""

# Using a model with coeffs!
coefs = lr_regressor.coef_
features = X_train.columns

# Sort coefficients by absolute value to get the top features
sorted_idx = np.argsort(np.abs(coefs))[::-1]  # Sort descending by absolute value
top_n = 100

# Select the top N features and their corresponding coefficients
top_features = [features[i] for i in sorted_idx[:top_n]]
top_coefs = coefs[sorted_idx[:top_n]]

# Create a bar plot for the top features and their coefficients
plt.figure(figsize=(20, 6))
sns.barplot(x=top_features, y=top_coefs)

plt.title(f'Top {top_n} Features Based on Coefficients')
plt.ylabel('Coefficient Value')
plt.xticks(rotation=45)
plt.savefig('linear_coeffs.png', dpi=300, bbox_inches='tight')

"""##Experiment 2 - Random Forest (5 - 18 min. rutime (took 5 for me)"""

rf_model, rf_y_pred = train_random_forest(X_train, X_test, y_train, y_test)

"""###Hyperparameter Tuning and Visualizations

####Top N Features
"""

def plot_feature_importance(model, X_train, top_n=10):
    feature_importances = model.feature_importances_
    sorted_idx = np.argsort(feature_importances)[::-1]

    plt.figure(figsize=(10, 6))
    sns.barplot(x=feature_importances[sorted_idx][:top_n],
                y=X_train.columns[sorted_idx][:top_n],
                orient='h')
    plt.title(f'Top {top_n} Feature Importances')
    plt.xlabel('Importance')
    plt.ylabel('Feature')
    plt.savefig('feature_importance.png', dpi=300, bbox_inches='tight')

plot_feature_importance(rf_model, X_train, top_n=30)

"""#### Residuals Plot"""

def plot_residuals(y_test, y_pred):
    residuals = y_test - y_pred
    plt.figure(figsize=(10, 6))
    sns.scatterplot(x=y_pred, y=residuals)
    plt.hlines(0, min(y_pred), max(y_pred), colors='red', linestyles='--')
    plt.title('Residuals vs Predicted')
    plt.xlabel('Predicted Values')
    plt.ylabel('Residuals')
    plt.savefig('residuals.png', dpi=300, bbox_inches='tight')

plot_residuals(y_test, rf_y_pred)

"""####Cross Validation"""

from sklearn.model_selection import cross_val_score
scores = cross_val_score(rf_model, X_train, y_train, cv=5, scoring='r2')
print(f"CV Scores: {scores}")
print(f"Mean R²: {scores.mean():.4f} ± {scores.std():.4f}")

"""###Retrial 1 - Only Top N Features selected

n = 100, 50


"""

# Get the feature importances from the trained RandomForest model
feature_importances = rf_model.feature_importances_

# Get the feature names (if X_train is a pandas DataFrame)
features = X_train.columns

# Sort features by importance in descending order
sorted_idx = np.argsort(feature_importances)[::-1]

n = 50

# Get the top n most important features
top_n_features = features[sorted_idx][:n]

# Subset the original dataset to only include the top 100 features
X_train_top_n = X_train[top_n_features]
X_test_top_n = X_test[top_n_features]  # Apply same transformation to the test data

# train a new model using these top 100 features
rf_model_top_n = RandomForestRegressor()
rf_model_top_n.fit(X_train_top_n, y_train)

# Make predictions using the top 100 features
rf_y_pred_top_n = rf_model_top_n.predict(X_test_top_n)

# Evaluate the new model's performance
from sklearn.metrics import mean_squared_error, r2_score

mse = mean_squared_error(y_test, rf_y_pred_top_n)
r2 = r2_score(y_test, rf_y_pred_top_n)

print(f"Mean Squared Error: {mse:.4f}")
print(f"R² Score: {r2:.4f}")

"""####Results

Reducing features down to 100, reduced error to 309, with R^2 of 0.4571. Reducing to 50 had no improvement, with MSE 311.1337, R^2 of 0.4784.

##Experiment 3 - PCA
"""

# Standardize the data
scaler = StandardScaler()
features_scaled = scaler.fit_transform(X)

components = 3

# Apply PCA
pca = PCA(n_components=3)
principal_components = pca.fit_transform(features_scaled)

# Convert the principal components into a DataFrame
pc_df = pd.DataFrame(data=principal_components, columns=['PC1', 'PC2', 'PC3'])

# Visualize the results (for 3 components)
# A 3D plot is best to visualize 3 components
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

ax.scatter(pc_df['PC1'], pc_df['PC2'], pc_df['PC3'], s=50)
ax.set_xlabel('PC1')
ax.set_ylabel('PC2')
ax.set_zlabel('PC3')
ax.set_title('3D PCA of Dataset')
plt.savefig('pca.png', dpi=300, bbox_inches='tight')

# Explained Variance Ratio
print(f'Explained Variance Ratio: {pca.explained_variance_ratio_}')
print(f'Total Variance Explained: {sum(pca.explained_variance_ratio_)}')

"""##Experiment 4 - Multilayer Perceptron (MLP)"""

mlp_model = train_mlp(X_train, X_test, y_train, y_test)

"""###Hyperparameter Tuning and Visualizations

Model is doing significantly worse than Random Forest.

Tests:
- Normalize and Scale features appropiately
- Change hyperparameters: epoch, lr
- Add more layers

####Test 1: Normalize and Scale features appropiately
"""

scaler = StandardScaler()

# Initialize scaler
scaler_X = StandardScaler()
scaler_y = StandardScaler()

# Fit and transform the features
X_train_scaled = scaler_X.fit_transform(X_train)
X_test_scaled = scaler_X.transform(X_test)

# Fit and transform the target variable
y_train_scaled = scaler_y.fit_transform(y_train.values.reshape(-1, 1))  # 2D array
y_test_scaled = scaler_y.transform(y_test.values.reshape(-1, 1))  #2D array

EPOCHS=100
LEARNING_RATE=1e-3

mlp_model, train_losses, val_losses, mlp_preds_scaled  = train_mlp_standard_scale(X_train_scaled, X_test_scaled, y_train_scaled, y_test_scaled, epochs=EPOCHS,lr=LEARNING_RATE)
mlp_preds_original = scaler_y.inverse_transform(mlp_preds_scaled.reshape(-1, 1)).flatten()
mse_mlp_original = mean_squared_error(y_test.values, mlp_preds_original)
r2_mlp_original = r2_score(y_test.values, mlp_preds_original)

print(f"Final [MLP] MSE (Original Scale): {mse_mlp_original:.4f} | R² (Original Scale): {r2_mlp_original:.4f}")

"""####Result:

Final [MLP] MSE: 0.5967 | R²: 0.3755

####Test 1 Chart: Learning Curves and Accuracy
"""

plt.figure(figsize=(10, 6))
plt.plot(range(EPOCHS), train_losses, label='Training Loss')
plt.plot(range(EPOCHS), val_losses, label='Validation Loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.title('Training and Validation Loss Over Epochs')
plt.legend()
plt.grid(True)
plt.savefig('mlp.png', dpi=300, bbox_inches='tight')

"""####Test 2: Hyperparameter and Tuning"""

EPOCHS=200
LEARNING_RATE=1e-3

mlp_model, train_losses, val_losses, mlp_preds_scaled = train_mlp_standard_scale(X_train_scaled, X_test_scaled, y_train_scaled, y_test_scaled, epochs=EPOCHS,lr=LEARNING_RATE)
mlp_preds_original = scaler_y.inverse_transform(mlp_preds_scaled.reshape(-1, 1)).flatten()
mse_mlp_original = mean_squared_error(y_test.values, mlp_preds_original)
r2_mlp_original = r2_score(y_test.values, mlp_preds_original)

print(f"Final [MLP] MSE (Original Scale): {mse_mlp_original:.4f} | R² (Original Scale): {r2_mlp_original:.4f}")

"""####Results

Epoch 194/200 | Train Loss: 0.0751 | Validation Loss: 0.5795 | R²: 0.3934

####Test 2 Chart
"""

plt.figure(figsize=(10, 6))
plt.plot(range(EPOCHS), train_losses, label='Training Loss')
plt.plot(range(EPOCHS), val_losses, label='Validation Loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.title('Training and Validation Loss Over Epochs')
plt.legend()
plt.grid(True)
plt.savefig('mlp2.png', dpi=300, bbox_inches='tight')

"""##Experiment 5 - MLP with learned embeddings for categorical inputs"""

X_num, X_cat, y = preprocessing_no_encodings(original_dataset, preprocessed_dataset)

# Normalize numerical features
scaler_x = StandardScaler()
X_num = scaler_x.fit_transform(X_num)

# Label categorical features
for col in X_cat.columns:
    le = LabelEncoder()
    X_cat[col] = le.fit_transform(X_cat[col])

# Normalize popularity for MLP embedding model
scaler_y = StandardScaler()
y_scaled = scaler_y.fit_transform(y.values.reshape(-1, 1)).flatten()

X_train_num, X_test_num, X_train_cat, X_test_cat, y_train, y_test = train_test_split(
    X_num, X_cat, y_scaled, test_size=0.2, random_state=42
)

cat_dims = [
    X_train_cat[col].nunique() for col in X_train_cat.columns
]

EPOCHS=6000
LEARNING_RATE=7e-4

# Train MLP embedding model

mlp_embeddings_model, train_losses, val_losses, mlp_preds_scaled = train_mlp_with_embeddings(X_train_num, X_test_num, X_train_cat.values, X_test_cat.values, y_train, y_test, cat_dims, EPOCHS, LEARNING_RATE)
mlp_preds_original = scaler_y.inverse_transform(mlp_preds_scaled.reshape(-1, 1)).flatten()
y_test_original = scaler_y.inverse_transform(y_test.reshape(-1, 1)).flatten()
mse_mlp_original = mean_squared_error(y_test_original, mlp_preds_original)
r2_mlp_original = r2_score(y_test_original, mlp_preds_original)
print(f"Final [MLP + Embeddings] MSE (Original Scale): {mse_mlp_original:.4f} | R² (Original Scale): {r2_mlp_original:.4f}")


# Plot training curve for MLP with embedding
plt.figure(figsize=(10, 6))
plt.plot(range(EPOCHS//10), train_losses, label='Training Loss')
plt.plot(range(EPOCHS//10), val_losses, label='Validation Loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.title('Training and Validation Loss Over Epochs')
plt.legend()
plt.grid(True)
plt.savefig('mlpembed.png', dpi=300, bbox_inches='tight')


# Plot scatter plot for MLP with embedding
plt.figure(figsize=(8, 6))
sns.scatterplot(x=y_test_original, y=mlp_preds_original, alpha=0.6, label='Predictions')
plt.plot([y_test_original.min(), y_test_original.max()], [y_test_original.min(), y_test_original.max()], 'r--', label='Ideal Fit')
plt.xlabel('Actual Values')
plt.ylabel('Predicted Values')
plt.title('Multimodal MLP: Actual vs Predicted')
plt.legend()
plt.savefig('mlpembedscatter.png', dpi=300, bbox_inches='tight')
