import asyncio
from starknet_py.net.full_node_client import FullNodeClient

async def test_rpc():
    # Try multiple compatible endpoints
    NODE_URLS = [
        "https://starknet-sepolia.public.blastapi.io/rpc/v0_8",
        "https://starknet-sepolia.drpc.org",
        "https://free-rpc.nethermind.io/sepolia-juno/v0_8"
    ]
    
    for url in NODE_URLS:
        try:
            print(f"🔌 Testing {url}")
            client = FullNodeClient(node_url=url)
            
            # Test 1: Chain ID (should return hex string)
            chain_id = await client.get_chain_id()
            if isinstance(chain_id, str):
                chain_id = int(chain_id, 16)
            print(f"✅ Chain ID: {hex(chain_id)} (Expected: 0x534e5f5345504f4c4941)")
            
            # Test 2: Block number (handle both int and string)
            block = await client.get_block("latest")
            block_num = block.block_number if hasattr(block, 'block_number') else 0
            print(f"✅ Latest block: #{block_num}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed with {url}: {str(e)}")
            continue
    
    return False

if __name__ == "__main__":
    success = asyncio.run(test_rpc())
    print("\nTest result:", "PASSED" if success else "FAILED")