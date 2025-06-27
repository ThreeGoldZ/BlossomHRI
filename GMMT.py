from sklearn.mixture import GaussianMixture
import numpy as np
import pandas as pd
import ace_tools as tools

# Simulate a 2-joint demonstration trajectory
T = 2.0
dt = 0.01
timesteps = np.arange(0, T, dt)

# Two joint trajectories: sin and cos based motion
joint1_demo = np.sin(2 * np.pi * timesteps / T) * 30 + 60
joint2_demo = np.cos(2 * np.pi * timesteps / T) * 20 + 40

# Stack time and joint positions
X = timesteps.reshape(-1, 1)                # (N, 1)
Y = np.column_stack([joint1_demo, joint2_demo])  # (N, 2)
XY = np.hstack([X, Y])                      # (N, 3)

# Fit GMM to (time, joint1, joint2)
gmm = GaussianMixture(n_components=8, covariance_type='full', random_state=42)
gmm.fit(XY)

# Gaussian Mixture Regression (GMR): Predict joint positions given time
def gmr(gmm, x_query, in_idx=[0], out_idx=[1,2]):
    means, covariances, weights = gmm.means_, gmm.covariances_, gmm.weights_
    y_out = []

    for x in x_query:
        x = np.array(x)
        prob_k = []
        mu_y_x = []
        for k in range(gmm.n_components):
            mu_k = means[k]
            sigma_k = covariances[k]

            mu_in = mu_k[in_idx]
            mu_out = mu_k[out_idx]
            sigma_in = sigma_k[np.ix_(in_idx, in_idx)]
            sigma_out = sigma_k[np.ix_(out_idx, out_idx)]
            sigma_cross = sigma_k[np.ix_(out_idx, in_idx)]

            # Conditional mean
            sigma_in_inv = np.linalg.pinv(sigma_in)
            mu_cond = mu_out + sigma_cross @ sigma_in_inv @ (x - mu_in)

            # Compute responsibility
            diff = x - mu_in
            exponent = -0.5 * diff.T @ sigma_in_inv @ diff
            norm_const = np.sqrt((2 * np.pi) ** len(in_idx) * np.linalg.det(sigma_in))
            p = weights[k] * np.exp(exponent) / (norm_const + 1e-10)

            prob_k.append(p)
            mu_y_x.append(mu_cond)

        prob_k = np.array(prob_k)
        prob_k /= np.sum(prob_k) + 1e-10
        mu_y_x = np.array(mu_y_x)
        y_out.append(np.sum(prob_k[:, None] * mu_y_x, axis=0))

    return np.array(y_out)

# Query over the same time range
X_query = timesteps.reshape(-1, 1)
Y_pred = gmr(gmm, X_query)

# Display results
df = pd.DataFrame({
    'time': timesteps,
    'joint1_demo': joint1_demo,
    'joint2_demo': joint2_demo,
    'joint1_gmm': Y_pred[:, 0],
    'joint2_gmm': Y_pred[:, 1],
})
tools.display_dataframe_to_user(name="GMM Multivariate Trajectory Learning", dataframe=df)
