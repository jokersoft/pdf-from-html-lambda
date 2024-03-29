pdf-from-html-lambda
===
Tools, required to produce pdf from html on AWS platform.

# Links
- Python Lambda code based on: https://dev.to/bschoeneweis/converting-html-to-a-pdf-using-python-aws-lambda-and-wkhtmltopdf-3mdh
- https://tech.mybuilder.com/compiling-wkhtmltopdf-aws-lambda-with-bref-easier-than-you-think/
- https://dev.to/bschoeneweis/converting-html-to-a-pdf-using-python-aws-lambda-and-wkhtmltopdf-3mdh
- https://wkhtmltopdf.org/downloads.html

# wkhtmltopdf layer
`arn:aws:lambda:eu-central-1:087756641496:layer:wkhtmltopdf:1`

Layer is private ATM.

## Build wkhtmltopdf layer:
1. Auth in AWS
2. [Download](https://wkhtmltopdf.org/downloads.html) your version from original source 
3. Do something like:
```shell
aws lambda publish-layer-version --layer-name wkhtmltopdf --description "standalone wkhtmltopdf binary" --zip-file fileb://wkhtmltox-0.12.6-4.amazonlinux2_lambda.zip
```

## Also
https://github.com/brandonlim-hs/fonts-aws-lambda-layer my solve fonts issue.

# Runtime environment
## Required env vars
Variables expected to inject:
```shell
BUCKET_NAME=jokersoft.pdf-test
```

## Run wkhtmltopdf pdf generation locally
### Mac OS
```shell
brew install --cask wkhtmltopdf
wkhtmltopdf --title "Google.com as PDF" --margin-left "10mm" http://google.com google.pdf
```
Try to find answers about possible arguments [here](https://wkhtmltopdf.org/docs.html)

# Deploy Lambda
```shell
cd src
zip artifact.zip main.py
```

# Event payload
From html file on S3 to pdf file on S3

```json
{
  "bucket": "jokersoft.pdf-test",
  "file_key": "om-test/reports/index.html",
  "folder": "tmp/", // optional, default: tmp/ 
  "wkhtmltopdf_options": {
    "orientation": "portrait",
    "title": "Test PDF Generation",
    "margin": "10mm 10mm 10mm 10mm"
  }
}
```

From html string to pdf file on S3
```json
{
  "bucket": "jokersoft.pdf-test",
  "html_string": "<!DOCTYPE html><html><head></head><body>This is an example of a simple HTML page.</body></html>",
  "wkhtmltopdf_options": {
    "orientation": "portrait",
    "title": "Test PDF Generation",
    "margin": "10mm 10mm 10mm 10mm"
  }
}
```

From url to pdf file on S3
```json
{
  "bucket": "jokersoft.pdf-test",
  "url": "https://stackoverflow.com",
  "wkhtmltopdf_options": {
    "orientation": "portrait",
    "title": "Test PDF Generation",
    "margin": "10mm 10mm 10mm 10mm"
  }
}
```
