import { Contract, RpcProvider } from 'starknet';

// Replace with your actual values
const CONTRACT_ADDRESS = '0x03a7bc97fc9a9dac1c568ce2be266d25531305dc8c85fa048400801c9e2b9e3c';
const provider = new RpcProvider({ nodeUrl: 'https://starknet-sepolia.public.blastapi.io/rpc/v0_6' });

import abi from './abi.json';

export const contract = new Contract(abi as any, CONTRACT_ADDRESS, provider);
