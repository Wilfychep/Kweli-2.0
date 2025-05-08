import os
import json
import logging
import asyncio
from dotenv import load_dotenv
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.signer.key_pair import KeyPair
from starknet_py.net.account.account import Account
from starknet_py.contract import Contract
from starknet_py.net.models import StarknetChainId

# Load environment
load_dotenv()

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration - Added type hints and validation
NODE_URL = os.getenv("NODE_URL", "https://starknet-sepolia.infura.io/v3/YOUR_KEY")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")
ACCOUNT_ADDRESS = os.getenv("ACCOUNT_ADDRESS")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")

# Global clients with initialization flag
client = account = contract = None
initialized = False

async def init_starknet() -> Contract:
    """Initialize Starknet components with Android compatibility"""
    global client, account, contract, initialized
    
    if initialized:
        return contract
        
    # Android-safe path resolution
    abi_path = os.path.join(os.path.dirname(__file__), "..", "lib", "starknet", "abi.json")
    
    try:
        client = FullNodeClient(node_url=NODE_URL)
        
        account = Account(
            address=int(ACCOUNT_ADDRESS, 16),
            client=client,
            key_pair=KeyPair.from_private_key(int(PRIVATE_KEY, 16)),
            chain=StarknetChainId.SEPOLIA
        )
        
        with open(abi_path) as f:
            contract = Contract(
                address=int(CONTRACT_ADDRESS, 16),
                abi=json.load(f),
                provider=account
            )
        
        initialized = True
        logger.info("✅ Starknet initialized")
        return contract
        
    except Exception as e:
        logger.error(f"❌ Initialization failed: {str(e)}")
        raise

async def store_result(felt_hash: int, result: int) -> str:
    """Store result with Android-compatible error handling"""
    if not initialized:
        await init_starknet()
    
    try:
        call = contract.functions["store_result"].prepare_call(
            hash=felt_hash,
            result=result
        )
        
        tx_response = await account.execute_v3(
            calls=[call],
            auto_estimate=True
        )
        
        await client.wait_for_tx(tx_response.transaction_hash, check_interval=2.0)
        
        logger.info(f"✅ Result stored. Tx hash: {hex(tx_response.transaction_hash)}")
        return hex(tx_response.transaction_hash)
        
    except Exception as e:
        logger.error(f"❌ Store failed: {str(e)}")
        raise

async def get_result(felt_hash: int) -> int:
    """Get result with retry logic"""
    if not initialized:
        await init_starknet()
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            (result,) = await contract.functions["get_result"].call(hash=felt_hash)
            return result
        except Exception as e:
            if attempt == max_retries - 1:
                logger.error(f"❌ Final attempt failed: {str(e)}")
                raise
            await asyncio.sleep(1 * (attempt + 1))

# Android-compatible sync wrappers
def store_result_sync(contract: Contract, felt_hash: int, result: int) -> str:
    """Thread-safe synchronous wrapper"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(store_result(felt_hash, result))
    except Exception as e:
        logger.error(f"❌ Sync store failed: {str(e)}")
        raise
    finally:
        loop.close()

def get_result_sync(contract: Contract, felt_hash: int) -> int:
    """Thread-safe synchronous wrapper"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(get_result(felt_hash))
    except Exception as e:
        logger.error(f"❌ Sync get failed: {str(e)}")
        raise
    finally:
        loop.close()