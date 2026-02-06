"""
Test WebSocket connection to verify BTC, ETH, and SOL price streaming.

This script connects to the Binance WebSocket and prints incoming prices
for all three monitored assets.
"""

import asyncio
import json
import websockets
from datetime import datetime


async def test_binance_stream():
    """Test the multi-asset Binance WebSocket stream."""
    uri = "wss://stream.binance.com:9443/stream?streams=btcusdt@trade/ethusdt@trade/solusdt@trade"

    print("🔌 Connecting to Binance WebSocket...")
    print(f"📡 URL: {uri}\n")

    prices_seen = {"BTC": False, "ETH": False, "SOL": False}

    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected! Listening for price updates...\n")

            # Listen for 30 seconds or until we see all three assets
            timeout = 30
            start_time = asyncio.get_event_loop().time()

            while asyncio.get_event_loop().time() - start_time < timeout:
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    data = json.loads(message)

                    if "stream" in data and "data" in data:
                        trade_data = data["data"]
                        symbol = trade_data.get("s", "")
                        price = float(trade_data.get("p", 0))

                        asset = symbol.replace("USDT", "")

                        # Mark asset as seen
                        if asset in prices_seen and not prices_seen[asset]:
                            prices_seen[asset] = True
                            timestamp = datetime.now().strftime("%H:%M:%S")

                            # Color codes for terminal
                            colors = {
                                "BTC": "\033[38;5;208m",  # Orange
                                "ETH": "\033[38;5;75m",   # Blue
                                "SOL": "\033[38;5;135m"   # Purple
                            }
                            reset = "\033[0m"

                            color = colors.get(asset, "")
                            symbol_map = {"BTC": "₿", "ETH": "Ξ", "SOL": "◎"}
                            emoji = symbol_map.get(asset, "")

                            print(f"{color}✓ {emoji} {asset}: ${price:,.2f}{reset} [{timestamp}]")

                        # Exit if we've seen all three assets
                        if all(prices_seen.values()):
                            print("\n✨ Successfully received prices for all 3 assets!")
                            break

                except asyncio.TimeoutError:
                    print("⏱️  Waiting for data...")
                    continue

            # Summary
            print("\n" + "="*50)
            print("📊 Test Summary:")
            for asset, seen in prices_seen.items():
                status = "✅ Received" if seen else "❌ Missing"
                print(f"  {status}: {asset}")
            print("="*50)

            if all(prices_seen.values()):
                print("\n🎉 WebSocket is working correctly!")
            else:
                missing = [a for a, s in prices_seen.items() if not s]
                print(f"\n⚠️  Warning: Missing data for {', '.join(missing)}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise


if __name__ == "__main__":
    # Fix Windows console encoding
    import sys
    if sys.platform == "win32":
        import codecs
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")
        sys.stderr = codecs.getwriter("utf-8")(sys.stderr.buffer, "strict")

    print("="*50)
    print("Fear & Greed 6900 - WebSocket Test")
    print("="*50 + "\n")

    asyncio.run(test_binance_stream())
