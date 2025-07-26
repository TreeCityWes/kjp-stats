# main.py
import json
import requests

# === CONFIG ===
RPC_URL = "https://api.mainnet-beta.solana.com"
KJP_MINT = "3zGcFLiVtYesdjqphEEHfqWo1bNsnKZ2SDy6AGVapump"
STAKING_POOL = "u1ZscFB8fcCcZDtmLd4LHHVmqTASkEbjq2gY4d7Dgcq"
DEXSCREENER_POOL = "dzkhigmtz8tffc35xs9zg8qa9yksfkknwetfsmr8e2c7"
DEXSCREENER_API_URL = f"https://api.dexscreener.com/latest/dex/pairs/solana/{DEXSCREENER_POOL}"

# === GET KJP SPL TOKEN BALANCE VIA JSON‑RPC ===
def get_token_balance(owner: str, mint: str) -> float:
    headers = {"Content-Type": "application/json"}
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTokenAccountsByOwner",
        "params": [
            owner,
            {"mint": mint},
            {"encoding": "jsonParsed"}
        ]
    }
    r = requests.post(RPC_URL, json=payload, headers=headers)
    r.raise_for_status()
    resp = r.json()
    accts = resp.get("result", {}).get("value", [])
    if not accts:
        return 0.0
    # take first token‐account
    info = accts[0]["account"]["data"]["parsed"]["info"]
    return float(info["tokenAmount"]["uiAmount"])

# === GET STATS FROM DEXSCREENER ===
def get_dexscreener_stats() -> dict:
    r = requests.get(DEXSCREENER_API_URL)
    r.raise_for_status()
    p = r.json().get("pair", {})
    txns = p.get("txns", {}).get("h24", {})
    return {
        "priceUsd": p.get("priceUsd"),
        "priceChange24h": p.get("priceChange", {}).get("h24"),
        "volume24h": p.get("volume", {}).get("h24"),
        "buys24h": txns.get("buys", 0),
        "sells24h": txns.get("sells", 0),
        "trades24h": txns.get("buys", 0) + txns.get("sells", 0),
        "holders": p.get("holders"),
        "liquidityUsd": p.get("liquidity", {}).get("usd"),
        "fullyDilutedValuation": p.get("fdv"),
        "marketCap": p.get("marketCap"),
    }

def main():
    balance = get_token_balance(STAKING_POOL, KJP_MINT)
    stats   = get_dexscreener_stats()

    out = {
        "stakingPool": STAKING_POOL,
        "kjpMint":     KJP_MINT,
        "kjpBalance":  balance,
        "dexscreener": stats,
    }
    with open("kjp_stats.json", "w") as f:
        json.dump(out, f, indent=2)
    print("Done — wrote kjp_stats.json")

if __name__ == "__main__":
    main()
