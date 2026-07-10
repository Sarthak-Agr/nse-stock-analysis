import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
import warnings
import os
warnings.filterwarnings('ignore')

os.makedirs('visuals', exist_ok=True)

plt.rcParams.update({
    'figure.facecolor': 'white',
    'axes.facecolor': '#f8f9fa',
    'axes.grid': True,
    'grid.color': '#e0e0e0',
    'grid.linestyle': '--',
    'grid.alpha': 0.7,
    'font.family': 'sans-serif',
    'axes.spines.top': False,
    'axes.spines.right': False,
})

TICKERS = ['RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS']
NAMES   = {'RELIANCE.NS': 'Reliance', 'TCS.NS': 'TCS',
           'HDFCBANK.NS': 'HDFC Bank', 'INFY.NS': 'Infosys'}
COLORS  = ['#2196F3', '#4CAF50', '#FF9800', '#9C27B0']
START, END = '2022-01-01', '2026-07-06'

print("Downloading data...")
raw  = yf.download(TICKERS, start=START, end=END, auto_adjust=True)
data = raw['Close']
data.columns = [NAMES[t] for t in data.columns]
print(f"Downloaded {len(data)} rows\n")

# ── 1. Price Trends ──────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(12, 6))
for col, color in zip(data.columns, COLORS):
    ax.plot(data.index, data[col], label=col, color=color, linewidth=2)
ax.set_title('NSE Stock Price Trends (2022–2026)', fontsize=15, fontweight='bold', pad=15)
ax.set_ylabel('Price (INR)')
ax.set_xlabel('')
ax.legend(loc='upper left')
plt.tight_layout()
plt.savefig('visuals/1_price_trends.png', dpi=150, bbox_inches='tight')
plt.close()
print("✓ Chart 1: Price trends saved")

# ── 2. Daily Returns & Volatility ────────────────────────────────────────────
returns = data.pct_change().dropna()
ann_vol = (returns.std() * (252 ** 0.5) * 100).round(2)

fig, axes = plt.subplots(2, 2, figsize=(14, 8))
axes = axes.flatten()
for i, (col, color) in enumerate(zip(data.columns, COLORS)):
    axes[i].plot(returns.index, returns[col] * 100, color=color, alpha=0.7, linewidth=0.8)
    axes[i].axhline(0, color='black', linewidth=0.8)
    axes[i].set_title(f'{col}  |  Volatility: {ann_vol[col]}% p.a.', fontweight='bold')
    axes[i].set_ylabel('Daily Return (%)')
fig.suptitle('Daily Returns by Stock (2022–2026)', fontsize=14, fontweight='bold', y=1.01)
plt.tight_layout()
plt.savefig('visuals/2_daily_returns.png', dpi=150, bbox_inches='tight')
plt.close()
print("✓ Chart 2: Daily returns saved")

# ── 3. Correlation Heatmap ───────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(8, 6))
corr = returns.corr()
mask = pd.DataFrame(False, index=corr.index, columns=corr.columns)
for i in range(len(mask)):
    for j in range(i):
        mask.iloc[i, j] = True
sns.heatmap(corr, annot=True, fmt='.2f', cmap='RdYlGn',
            vmin=-1, vmax=1, ax=ax, mask=mask,
            annot_kws={'size': 13, 'weight': 'bold'},
            linewidths=2, linecolor='white', square=True)
ax.set_title('Stock Return Correlation Matrix', fontsize=14, fontweight='bold', pad=15)
plt.tight_layout()
plt.savefig('visuals/3_correlation_heatmap.png', dpi=150, bbox_inches='tight')
plt.close()
print("✓ Chart 3: Correlation heatmap saved")

# ── 4. Moving Averages (TCS) ─────────────────────────────────────────────────
tcs = data['TCS'].copy()
ma50  = tcs.rolling(50).mean()
ma200 = tcs.rolling(200).mean()

golden = ((ma50 > ma200) & (ma50.shift(1) <= ma200.shift(1)))
death  = ((ma50 < ma200) & (ma50.shift(1) >= ma200.shift(1)))

fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(tcs.index,  tcs,   label='TCS Price',    color='#2196F3', linewidth=1.5, alpha=0.9)
ax.plot(ma50.index, ma50,  label='50-Day MA',    color='#FF9800', linewidth=2, linestyle='--')
ax.plot(ma200.index,ma200, label='200-Day MA',   color='#9C27B0', linewidth=2, linestyle='--')

for date in tcs.index[golden]:
    ax.axvline(date, color='#4CAF50', alpha=0.8, linewidth=1.5)
    ax.annotate('Golden\nCross', xy=(date, tcs[date]),
                xytext=(10, 30), textcoords='offset points',
                fontsize=8, color='#2E7D32', fontweight='bold',
                arrowprops=dict(arrowstyle='->', color='#2E7D32'))

for date in tcs.index[death]:
    ax.axvline(date, color='#F44336', alpha=0.8, linewidth=1.5)
    ax.annotate('Death\nCross', xy=(date, tcs[date]),
                xytext=(10, -50), textcoords='offset points',
                fontsize=8, color='#C62828', fontweight='bold',
                arrowprops=dict(arrowstyle='->', color='#C62828'))

ax.set_title('TCS — Price with Moving Averages & Crossover Signals', fontsize=14, fontweight='bold', pad=15)
ax.set_ylabel('Price (INR)')
ax.legend(loc='upper left')
plt.tight_layout()
plt.savefig('visuals/4_moving_averages.png', dpi=150, bbox_inches='tight')
plt.close()
print("✓ Chart 4: Moving averages saved")

# ── 5. Risk vs Return ────────────────────────────────────────────────────────
ann_ret = (returns.mean() * 252 * 100).round(2)
sharpe  = (ann_ret / ann_vol).round(2)

fig, ax = plt.subplots(figsize=(9, 7))
for col, color in zip(data.columns, COLORS):
    ax.scatter(ann_vol[col], ann_ret[col], s=200, color=color, zorder=5, edgecolors='white', linewidths=1.5)
    ax.annotate(f'{col}\n(Sharpe: {sharpe[col]})',
                xy=(ann_vol[col], ann_ret[col]),
                xytext=(8, 8), textcoords='offset points',
                fontsize=10, fontweight='bold', color=color)

ax.axhline(0, color='gray', linewidth=0.8, linestyle='--')
ax.set_xlabel('Annual Volatility / Risk (%)', fontsize=12)
ax.set_ylabel('Annual Return (%)', fontsize=12)
ax.set_title('Risk vs Return — Which Stock Gives the Best Bang for Risk?', fontsize=13, fontweight='bold', pad=15)
plt.tight_layout()
plt.savefig('visuals/5_risk_return.png', dpi=150, bbox_inches='tight')
plt.close()
print("✓ Chart 5: Risk vs return saved")

# ── Summary Stats ────────────────────────────────────────────────────────────
print("\n" + "="*55)
print("SUMMARY STATISTICS")
print("="*55)
summary = pd.DataFrame({
    'Annual Return (%)' : ann_ret,
    'Annual Volatility (%)': ann_vol,
    'Sharpe Ratio'      : sharpe,
    'Total Return (%)' : ((data.iloc[-1] / data.iloc[0] - 1) * 100).round(2)
})
print(summary.to_string())
print("="*55)
print(f"\nBest Sharpe Ratio : {sharpe.idxmax()} ({sharpe.max()})")
print(f"Lowest Risk       : {ann_vol.idxmin()} ({ann_vol.min()}% volatility)")
print(f"Highest Return    : {ann_ret.idxmax()} ({ann_ret.max()}% p.a.)")
print("\nAll charts saved to /visuals/")
print(raw.head())