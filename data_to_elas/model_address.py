import yaml

from elasticsearch_dsl import DocType, Integer, Text, Nested, Keyword, Double, InnerDoc, Completion
from elasticsearch_dsl.connections import connections
from elasticsearch_dsl import Search
from elasticsearch_dsl import analyzer
from elasticsearch import Elasticsearch


link = yaml.load(open('config.yml'))
ELASTICSEARCH_URL = link['ELASTICSEARCH_URI']

client = connections.create_connection(
                hosts=ELASTICSEARCH_URL,
                timeout=20)


class Address(DocType): 
    subdistrict_id = Integer()
    subdistrict_name = Text()
    subdistrict_type = Text()
    subdistrict_location = Text()
    district_id = Integer()
    district_name = Text()
    district_type = Text()
    district_location = Text()
    province_id = Integer()
    province_name = Text()
    province_type = Text()
    full_address = Text()
    suggestions = Completion(contexts=[{"name":"location", "type":"geo", "precision":"10km"}], 
                             analyzer=analyzer('standard'))

    class Meta:
        index = 'addresses'

Address.init(using=client)
