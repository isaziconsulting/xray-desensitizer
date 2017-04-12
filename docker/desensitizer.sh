#!/bin/bash

echo "Please enter the path to the input directory, followed by [ENTER] (this should start with '/host/')"
read INPATH

echo "Please enter the output directory path, followed by [ENTER] (leave blank if you would like it to write to your desktop)"
read OUTPATH

if [$OUTPATH -eq ""]
then
	OUTPATH="/host/Desktop/processed_xrays"
fi

docker run -v $HOME:/host -w /xray-desensitizer/src -t -i -e datapath=$INPATH -e writepath=$OUTPATH isazi/xray-desensitizer:latest

