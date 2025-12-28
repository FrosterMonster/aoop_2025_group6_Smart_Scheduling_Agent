#!/bin/bash

# 要產生的 commit 次數
COMMITS=100

# 目標檔案
FILE="auto_commit.txt"

# 若檔案不存在則建立
touch $FILE

for ((i=1; i<=COMMITS; i++))
do
    echo "Auto commit #$i - $(date)" >> $FILE
    git add $FILE
    git commit -m "add #$i"
done

echo "完成產生 $COMMITS 次 git commit"
