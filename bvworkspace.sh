#!/bin/bash


rm_file(){
    if [ -f "$1" ]
    then
        rm $1
    fi
}

lns_file(){
    if [ -f "$1" ]
    then
        ln -s "$1" "$2"
    else
        echo "not found $2"
    fi
}

update_ln_fils(){
    rm_file $2
    lns_file $@
}

use_comm() {
    update_ln_fils "datas/abis/usdt_abi.py" "usdt_abi.py"
    update_ln_fils "datas/abis/wbtc_abi.py" "wbtc_abi.py"
    update_ln_fils "datas/abis/erc20_std_abi.py" "erc20_std_abi.py"
    update_ln_fils "datas/wallet/bwallet" "bwallet"
    update_ln_fils "datas/wallet/ewallet" "ewallet"
}
use_internal(){
    echo "call use_internal"
    update_ln_fils "datas/config/bvexchange_internal.toml" "bvexchange.toml"
    update_ln_fils "datas/wallet/vwallet_internal" "vwallet"
    update_ln_fils "datas/keys/mint_internal.key" "mint_test.key"
    update_ln_fils "datas/redis/redis_internal.conf" "redis.conf"
    update_ln_fils "datas/redis/redis_internal_start.sh" "redis_start"
    update_ln_fils "datas/abis/vmp_main_abi_internal.py" "vmp_main_abi.py"
    update_ln_fils "datas/abis/vmp_datas_abi_internal.py" "vmp_datas_abi.py"
    update_ln_fils "datas/abis/vmp_state_abi_internal.py" "vmp_state_abi.py"
    use_comm
}

use_test(){
    echo "call use_test"
    use_internal
    update_ln_fils "datas/config/bvexchange_test.toml" "bvexchange.toml"
    update_ln_fils "datas/wallet/vwallet_test" "vwallet"
    update_ln_fils "datas/redis/redis_test.conf" "redis.conf"
    update_ln_fils "datas/redis/redis_test_start.sh" "redis_start"
    update_ln_fils "datas/abis/vmp_main_abi_internal.py" "vmp_main_abi.py"
    update_ln_fils "datas/abis/vmp_datas_abi_internal.py" "vmp_datas_abi.py"
    update_ln_fils "datas/abis/vmp_state_abi_internal.py" "vmp_state_abi.py"
    use_comm
}

use_external(){
    echo "call use_external"
    update_ln_fils "datas/config/bvexchange_external.toml" "bvexchange.toml"
    update_ln_fils "datas/wallet/vwallet_external" "vwallet"
    update_ln_fils "datas/keys/mint_external.key" "mint_test.key"
    update_ln_fils "datas/redis/redis_external.conf" "redis.conf"
    update_ln_fils "datas/redis/redis_external_start.sh" "redis_start"
    update_ln_fils "datas/abis/vmp_main_abi_external.py" "vmp_main_abi.py"
    update_ln_fils "datas/abis/vmp_datas_abi_external.py" "vmp_datas_abi.py"
    update_ln_fils "datas/abis/vmp_state_abi_external.py" "vmp_state_abi.py"
    use_comm
}

change_workspace(){
    if [ $1 == 1 ]
    then
        use_internal
    elif [ $1 == 2 ]
    then
        use_external
    elif [ $1 == 3 ]
    then
        use_test
    else
        echo "select index:"
        echo "  internal: 1"
        echo "  external: 2"
        echo "  test: 3"
        return -1
    fi
    return 0
}

reselect(){
    count=0
    max_count=3
    while (( $count < $max_count ))
    do
        echo "select index:"
        echo "  internal: 1"
        echo "  external: 2"
        echo "  test: 3"
        read -p "input 1 or 2 3: " sel_val
        echo $sel_val
        change_workspace $sel_val
        if [ $? == 0 ] ; then break; fi
        let count++
    done
}

echo $#
if [ $# == 0 ]
then
    reselect
elif [ $# == 1 ]
then
    if [ $1 == "internal" ]
    then
        use_internal
    elif [$1 == "external" ]
    then
        use_external
    elif [$1 == "test" ]
    then
        use_test
    else
        echo "args is invalid. can use args: internal external test"
        return
    fi
else
    echo "args is invalid. can use args: internal external test"
fi

