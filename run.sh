is_elasticsearch_ready() {
    eval "curl -I http://localhost:9200"
}

i=0
while ! is_elasticsearch_ready; do
    i=`expr $i + 1`
    if [ $i -ge 10 ]; then
        echo "$(date) - elasticsearch still not ready, giving up"
        exit 1
    fi
    echo "$(date) - waiting for elasticsearch to be ready"
    sleep 3
done

python data_to_elas/read_location.py
node completion_ui/index.js