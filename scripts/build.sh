build_targets=("bdist_dmg" "bdist_mac")

python3 setup.py "${build_targets[@]/#/}" 