var elasticsearch = require('elasticsearch');

ELASTICSEARCH_URL = 'http://localhost:9200/'

var client = new elasticsearch.Client( {  
  hosts: [
    ELASTICSEARCH_URL
  ]
});

module.exports = client;  