#!/bin/bash

# -- Running Weaviate DB
# -- Review data using >> https://console.semi.technology/
docker run -it --rm --name weaviate -e "OPENAI_APIKEY=XX" -e "QUERY_DEFAULTS_LIMIT=25" -e "AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true" -e "PERSISTENCE_DATA_PATH=/var/lib/weaviate" -e "DEFAULT_VECTORIZER_MODULE=text2vec-openai" -e "ENABLE_MODULES=text2vec-openai,generative-openai" -e "CLUSTER_HOSTNAME=node1" -p 8080:8080 -v $(pwd):/weaviate-data semitechnologies/weaviate:latest

## -- Testing
curl -X GET http://localhost:8080/v1/meta