import vectorbt as vbt
import pandas as pd
import numpy as np
import fta
import plotly.graph_objects as go
import os
from strategy.just_keep_buying_with_technicals import trade


def main():
	url = "https://raw.githubusercontent.com/voidful/tw_stocker/main/data/4967.csv"
	df = pd.read_csv(url, index_col='Datetime')

	ta = fta.TA_Features()
	df_full = ta.get_all_indicators(df)

	states_buy, states_sell, states_entry, states_exit, total_gains, invest = trade(df_full)

	fees = 0  # 假設交易費用為 0
	portfolio_kwargs = dict(size=np.inf, fees=float(fees), freq='5m')
	portfolio = vbt.Portfolio.from_signals(df_full['close'], states_entry, states_exit, **portfolio_kwargs)
	
	# 列印統計資訊
	print(portfolio.stats())
	
	# 產生互動式 Plotly 圖表
	fig = go.Figure()
	
	# 添加股票價格線
	fig.add_trace(go.Scatter(
		x=df_full.index,
		y=df_full['close'],
		mode='lines',
		name='收盤價',
		line=dict(color='blue', width=2)
	))
	
	# 添加買入訊號
	buy_indices = np.where(states_buy)[0]
	if len(buy_indices) > 0:
		fig.add_trace(go.Scatter(
			x=df_full.index[buy_indices],
			y=df_full['close'].iloc[buy_indices],
			mode='markers',
			name='買入',
			marker=dict(symbol='triangle-up', size=10, color='green')
		))
	
	# 添加賣出訊號
	sell_indices = np.where(states_sell)[0]
	if len(sell_indices) > 0:
		fig.add_trace(go.Scatter(
			x=df_full.index[sell_indices],
			y=df_full['close'].iloc[sell_indices],
			mode='markers',
			name='賣出',
			marker=dict(symbol='triangle-down', size=10, color='red')
		))
	
	# 設置圖表配置
	fig.update_layout(
		title='股票 4967 - 交易策略回測圖表',
		xaxis_title='日期時間',
		yaxis_title='價格 (元)',
		hovermode='x unified',
		height=600,
		template='plotly_white'
	)
	
	# 保存為 HTML
	output_path = os.path.join(os.path.dirname(__file__), 'portfolio_plot.html')
	fig.write_html(output_path)
	print(f"\n圖表已保存至: {output_path}")
	
	# 如果在互動環境中，也顯示圖表
	try:
		fig.show()
	except:
		pass  # 如果在無 GUI 環境中會失敗，但已經保存到檔案


if __name__ == '__main__':
	main()