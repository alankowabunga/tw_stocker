import logging
import nlp2
import pandas as pd
from jinja2 import Environment, FileSystemLoader

from strategy.grid import trade

logging.basicConfig(level=logging.INFO)


def recommend_stock(url, parameters):
    df = pd.read_csv(url, index_col='Datetime')
    df.columns = map(str.lower, df.columns)
    df['open'] = pd.to_numeric(df['open'], errors='coerce')
    df['high'] = pd.to_numeric(df['high'], errors='coerce')
    df['low'] = pd.to_numeric(df['low'], errors='coerce')
    df['close'] = pd.to_numeric(df['close'], errors='coerce')
    df['volume'] = pd.to_numeric(df['volume'], errors='coerce')

    states_buy, states_sell, states_entry, states_exit, total_gains, invest = trade(df, **parameters)

    today = len(df)
    today_close_price = df.close.iloc[-1] if not df.empty else None

    # 安全地處理空的 states_buy / states_sell
    should_buy = False
    should_sell = False
    try:
        if states_buy:
            should_buy = (today - states_buy[-1]) < 27
    except Exception:
        should_buy = False

    try:
        if states_sell:
            should_sell = (today - states_sell[-1]) < 27
    except Exception:
        should_sell = False

    return should_buy, should_sell, today_close_price, total_gains


def generate_report(urls, parameters, limit=10):
    results = []
    for url in urls:
        try:
            should_buy, should_sell, today_close_price, total_gains = recommend_stock(url, parameters)
            if should_sell or should_buy:
                results.append({
                    "Stock": url.split('/')[-1].split('.')[0],
                    "Should_Buy": should_buy,
                    "Should_Sell": should_sell,
                    "Recommended_Price": today_close_price,
                    "Total_Gains": total_gains,
                })
        except Exception as e:
            logging.debug(f"Skipping {url}: {e}")

    # 排序並選擇前N檔股票，根據 Total_Gains
    sorted_results = sorted(results, key=lambda x: x.get('Total_Gains', 0) or 0, reverse=True)[:limit]

    df = pd.DataFrame(sorted_results)
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('stock_report_template.html')
    html_output = template.render(stocks=df.to_dict(orient='records'))

    with open('stock_report.html', 'w') as f:
        f.write(html_output)


def main():
    parameters = {
        "rsi_period": 14,
        "low_rsi": 30,
        "high_rsi": 70,
        "ema_period": 26,
    }

    files = list(nlp2.get_files_from_dir("data"))
    for i in files:
        try:
            url = i
            should_buy, should_sell, today_close_price, _ = recommend_stock(url, parameters)
            if should_sell or should_buy:
                logging.info(f"{i.split('/')[-1].split('.')[0]} Should buy today: {should_buy}, Should sell today: {should_sell}, Recommended price: {today_close_price}")
        except Exception as e:
            logging.debug(f"Error processing {i}: {e}")

    generate_report(files, parameters)


if __name__ == '__main__':
    main()
