#[starknet::contract]
mod detection_contract {
    use starknet::ContractAddress;
    use starknet::storage::Map;

    #[storage]
    struct Storage {
        detection_results: Map<felt252, felt252>,
    }

    #[derive(starknet::Event, Drop, Destruct)]
    struct DetectionStored {
        hash: felt252,
        result: felt252,
        by: ContractAddress,
    }

    #[derive(starknet::Event, Drop)]
    #[event]
    enum Event {
        DetectionStored: DetectionStored,
    }

    #[external(v0)]
    fn store_result(ref self: ContractState, hash: felt252, result: felt252) {
        self.detection_results.write(hash, result);
        let caller = starknet::get_caller_address();
        self.emit(Event::DetectionStored(DetectionStored { hash, result, by: caller }));
    }

    #[external(v0)]
    fn get_result(self: @ContractState, hash: felt252) -> felt252 {
        self.detection_results.read(hash)
    }
}
