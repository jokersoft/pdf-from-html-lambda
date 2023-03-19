# Links
- Python Lambda code based on: https://dev.to/bschoeneweis/converting-html-to-a-pdf-using-python-aws-lambda-and-wkhtmltopdf-3mdh
- https://tech.mybuilder.com/compiling-wkhtmltopdf-aws-lambda-with-bref-easier-than-you-think/
- https://dev.to/bschoeneweis/converting-html-to-a-pdf-using-python-aws-lambda-and-wkhtmltopdf-3mdh
- https://wkhtmltopdf.org/downloads.html

# wkhtmltopdf layer
`arn:aws:lambda:eu-central-1:087756641496:layer:wkhtmltopdf:1`

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

# Event payload
From html file on S3 to pdf file on S3 
```json
{
  "bucket": "jokersoft.pdf-test",
  "file_key": "index.html",
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
