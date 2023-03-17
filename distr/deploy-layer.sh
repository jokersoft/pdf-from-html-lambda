#!/bin/bash

aws lambda publish-layer-version --layer-name wkhtmltopdf --description "standalone wkhtmltopdf binary" --zip-file fileb://wkhtmltox-0.12.6-4.amazonlinux2_lambda.zip
