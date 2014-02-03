*** Settings ***

Documentation  A resource file containing the application specific keywords
...            that create our own domain specific language. This resource
...            implements keywords for testing HTML version of the test
...            application.
Library        EntrezLibrary


*** Variables ***

${SERVER}        www.ncbi.nlm.nih.gov
${BROWSER}       phantomjs
${DELAY}         1
${VALID USER}    demo
${VALID PASSWD}  mode
${PUBMED}        http://${SERVER}/pubmed/
${PUBMED_TITLE}  Home - PubMed - NCBI
${WELCOME URL}   http://${SERVER}/html/welcome.html
${ERROR URL}     http://${SERVER}/html/error.html





Search PubMed For  [Arguments]  ${term}
    Input Text  term  ${term}
    Click Button  search
