for XDAYS in $(seq 2 11); do 
    START=$(date --date="$XDAYS days ago" +'%Y-%m-%d 00:00:00')
    END=$(date --date="$XDAYS days ago" +'%Y-%m-%d 23:59:00')
    DAILY_FILE=SPY_$(date --date="$XDAYS days ago" +'%Y%m%d').avr; 
    python td_get_price_history.py -s SPY -S "'$START'" -E "'$END'" -e True -k DORAEMON001 
    avro write --schema=config/td-schema.json --input-type=json -o charts/${DAILY_FILE} charts/SPY.jsonl
    [ -d datalake-tdameritrade ] && mv charts/${DAILY_FILE} datalake-tdameritrade/
done

