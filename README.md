# DocumentFiler
Automatic PDFtoText and refiling of scanned PDF documents

Given an input folder of PDF documents, process each of them and move 'matched' documents into a sub-folder of an output folder.

## Dependencies
pdftotext is required to convert from searchable PDF documents into text for processing and categorising.

## Usage
    usage: DocumentFiler.py [-h] [--config CONFIG] [--p2t P2T] [--output OUTPUT]
                            input [input ...]

    Automatic PDFtoText and refiling of scanned PDF documents

    positional arguments:
    input            An input folder of material to process

    optional arguments:
    -h, --help       show this help message and exit
    --config CONFIG  The confguration file to use if there isn't one in the
                    input
    --p2t P2T        The location of pdttotext if not in the default path
    --output OUTPUT  The output folder to use
    
## Configuration
DocumentFiler can load a JSON document to provide user specific configuration options for potentially sensitive information such as a list of companies or addresses.  This configuration file will be loaded from
 - the current input folder if it exists,
 - the configuration path given on the command line, or
 - the same folder as the application.

