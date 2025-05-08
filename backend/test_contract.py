# test_contract.py
import asyncio
from starknet_utils import init_starknet, store_result, get_result

async def main():
    await init_starknet()
    test_hash = 0x1234  # Test value
    
    tx_hash = await store_result(test_hash, 1)
    print(f"✅ Stored. Tx hash: {tx_hash}")
    
    value = await get_result(test_hash)
    print(f"✅ Retrieved: {value}")

asyncio.run(main())