# Alexa control of weight logging:
## Alexa Skills
In the Alexa developer console I created a skill called "weight logger" that when invoked with an intent ("Alexa, tell weight logger...") will send data to an AWS Lambda function  
Correct language when speaking to Alexa:  
"Alexa, tell weight logger that I weigh ___ pounds"  
She should respond with "logged ___ pounds"  
--> troubleshooting: If she doesn't check the JSON output in the test page of the developer console- if it logged the weight correctly it's likely an issue with lambda  
## AWS Lambda
Lambda gets the weight value from the Alexa Skill and runs some python code to append it to weights.json in my github repository  
--> troubleshooting: if there are issues go to the monitor tab of the function alexa-log-weight, scroll down and look at the cloudwatch logs

## Github
in .github/workflows theres a .yml file that tells github what to do- when a push includes changes to weights.json it executes some python code (that updates my weight figure) and then pushes changes to the repository  
--> troubleshooting: errors here can be traced down by going to the Actions tab in the github repo