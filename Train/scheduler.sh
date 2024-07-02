#!/bin/bash

usage() {
    echo "Usage: $0 <directory_path> <batch_size> <epochs> -m <model_name> [-f <freeze_layers>]"
    echo "  -m <model_name>                 YOLO model name"
    echo "  -f <freeze_layers>              Layers to freeze, e.g., \"[firstLayerIndex, lastLayerIndex]\""
    exit 1
}

def_freeze="[0, 0]"
model=""
freeze=""

POSITIONAL_ARGS=()

while [[ $# -gt 0 ]]; do
    case $1 in
        -f|--freeze )
            	freeze="$2"
            	shift
	    	shift
	    	;;
        -m|--model )
            	model="$2"
	    	shift 
	    	shift
            	;;
	-*|--*)
	   	echo "Unknown option $1"
		usage
		exit 1
		;;
        : )
            	echo "Invalid option: -$OPTARG requires an argument" 1>&2
            	usage
            	;;
	* )
		POSITIONAL_ARGS+=("$1")
		shift
		;;
    esac
done

set -- "${POSITIONAL_ARGS[@]}"

if [ $# -ne 3 ]; then
    usage
fi


if [ -z "$freeze" ]; then
    	echo "No freezing layer"
    	freeze=$def_freeze
else
    	if [[ ! $freeze =~ ^\[\ *[0-9]+\ *(,\ *[0-9]+\ *)*\]$ ]]; then
        	echo "Error: Input must be in python format [int, int, ...]"
        	exit 1
    	else
        	echo "Freezing from $freeze"
	fi
fi

transferLearn=false
if [ -z "$model" ]; then
	echo "Transfer learning enabled"
	transferLearn=true
else 
	echo "Using model: $model"
fi

echo ""



directory_path=$1
batchsize=$2
epochs_str=$3

if [[ ! $epochs_str =~ ^\(\ *[0-9]+\ *(,\ *[0-9]+\ *)*\)$ ]]; then
    echo "Error: Input must be in the format (int, int, ...)"
    exit 1
fi

epochs_str=${epochs_str//[\(\)]/}
epochs_str=${epochs_str// /}

IFS=',' read -r -a epochs <<< "$epochs_str"


default_name="Cook_Station_"
default_name2="/weights/best.pt"
head_length=$((${#directory_path}+${#default_name}))
tail_length=${#default_name2}

#tensorboard --logdir $directory_path/ &

idx=1

for epoch in "${epochs[@]}"
do
	echo "Running iteration $idx..."
	echo ""
	matching_directories=($(find $directory_path -type f -path '*/Cook_Station_*/weights/best.pt' | sort -rV))
	
	if [ -z "$matching_directories" ] && [ "$transferLearn" == true ]; then
		echo "No model specified. Exiting..."
		break
	fi
	
	choosen_dir=${matching_directories[0]}	
	tail_pos=$((${#choosen_dir}-tail_length))
	iterationID=${choosen_dir:$head_length:$(($tail_pos-$head_length))}
	name="$default_name$(($iterationID+1))"
	if [ -z "$matching_directories" ]; then
		choosen_dir=$model
	fi

	./PotholeV8.py -directory "$choosen_dir" -project "$directory_path" -batch "$batchsize" -epoch "$epoch" -name "$name" -freeze "$freeze"
	exit_status=$?
	if [ $exit_status -eq 1 ]; then
		batchsize=$((batchsize - 1))
		echo "BATCH SIZE REDUCED BY ONE: $batchsize"
	else
		./export.py -directory "$directory_path$name$default_name2"
	fi
    	echo "Iteration $idx complete."
	idx=$((idx+1));
done
