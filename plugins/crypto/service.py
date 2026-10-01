import requests
import pandas as pd
import torch
import joblib
from torch import nn
from langchain_core.tools import tool
from functools import lru_cache

BASE_URL = "https://api.binance.com/api/v3/klines"
SYMBOL = "BTCUSDT"

COLUMNS = [
    "open_time", "open", "high", "low", "close", "volume",
    "close_time", "quote_volume", "trades",
    "taker_buy_base", "taker_buy_quote", "ignore",
]

class LSTMModel(nn.Module):
    def __init__(self):
        super().__init__()

        self.lstm = nn.LSTM(9, 64, 4, batch_first=True, dropout=0.2)

        self.backbone = nn.Sequential(
            nn.Linear(64, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.Dropout(0.2)
        )

        self.close_head = nn.Sequential(
            nn.Linear(32, 16),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(16, 1)
        )

        self.suggest_head = nn.Sequential(
            nn.Linear(32, 16),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(16, 3),
        )

    def forward(self, x):
        _, (h_n, _) = self.lstm(x)

        h  = h_n[-1]

        backbone = self.backbone(h)
        close_output = self.close_head(backbone)
        suggest_output = self.suggest_head(backbone)

        return close_output, suggest_output

def current_candles(interval, limit):
    result = requests.get(BASE_URL, params={"symbol": SYMBOL, "interval": interval, "limit": limit})
    result.raise_for_status()
    return result.json()

def greed_fear():
    result = requests.get(
        "https://api.alternative.me/fng/",
        params={"limit": 20}
    )
    result.raise_for_status()

    return result.json()["data"]

@lru_cache(maxsize=2)
def load_artifacts(interval):
    if interval not in ("4h", "1d"):
        raise ValueError("Interval harus '4h' atau '1d'")

    model_dir = f"plugins/crypto/models/{SYMBOL}_{interval}"
    scaler_x = joblib.load(f"{model_dir}/input_scaler.pkl")
    scaler_y = joblib.load(f"{model_dir}/target_scaler.pkl")

    model = LSTMModel()
    model.load_state_dict(
        torch.load(f"{model_dir}/lstm_btc_model.pth", map_location="cpu", weights_only=True)
    )
    model.eval()

    return model, scaler_x, scaler_y

@tool
def tool_call(interval):
    '''
    Tool ini akan memberikan data crypto yang bisa kamu gunakan untuk memprediksi dan memberikan keputusan 4 jam kedepan ataupun 1 hari kedepan

    Args:
        interval: saat ini baru hanya ada 4h dan 1d, pilih 4h untuk prediksi candle 4 jam yang akan datang, pilih 1d untuk satu hari yang akan datang
    '''
    model, scaler_x, scaler_y = load_artifacts(interval)

    if interval == "1d":
        limit = 30
    else:
        limit = 180

    df = pd.DataFrame(current_candles(interval, limit), columns=COLUMNS).drop(columns=["ignore"])

    greed_fear_index = pd.DataFrame(greed_fear())
    greed_fear_index["timestamp"] = pd.to_datetime(greed_fear_index["timestamp"].astype(int), unit="s").dt.strftime("%Y-%m-%d %H:%M:%S")
    greed_fear_index = greed_fear_index.drop(columns=["time_until_update"])

    df["open_time"] = pd.to_datetime(df["open_time"], unit="ms").dt.strftime("%Y-%m-%d %H:%M:%S")
    df["close_time"] = pd.to_datetime(df["close_time"], unit="ms").dt.strftime("%Y-%m-%d %H:%M:%S")

    df_input = df[["open", "high", "low", "close", "volume", "quote_volume", "trades", "taker_buy_base", "taker_buy_quote"]]

    scaled_x = scaler_x.transform(df_input.astype(float))
    x = torch.tensor(scaled_x, dtype=torch.float32).unsqueeze(0)

    with torch.no_grad():
        close, suggest = model(x)
        softmax = torch.nn.functional.softmax(suggest, dim=1).squeeze().detach().numpy()
        result = torch.cat([close, suggest], dim=1)
        result = scaler_y.inverse_transform([result.squeeze().detach().numpy()])[-1]
        result = {
            "current_close": float(df["close"].iloc[-1]),
            "pred_close": float(result[0]),
            "pred_buy": float(softmax[0].astype(float)),
            "pred_hold": float(softmax[1].astype(float)),
            "pred_sell": float(softmax[2].astype(float)),
            "candles": df.to_dict("records"),
            "greed_fear_index": greed_fear_index.to_dict("records")
        }

    return result