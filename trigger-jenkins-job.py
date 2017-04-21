from __future__ import print_function

import base64
import string
import httplib
import boto3
import datetime
import json
import time


def trigger_jenkins_job():
    print("----trigger jenkins job start-------")
    conn = httplib.HTTPConnection(YOUR_JENKINS_IP, YOUR_JENKINS_PORT)
    //Your Jenkins crentials
    auth = base64.b64encode(YOUR_USERNAME+":"+YOUR_PASSWORD).decode("ascii")
    head = { 'Authorization' : 'Basic %s' %  auth }
    conn.request("POST", "/job/YOUR_JOB_NAME/build", headers = head)
    
    res = conn.getresponse()
    print(res.status)
    print(res.reason)
    conn.close()
    print("----trigger jenkins job end-------")
    time.sleep(20)
    
def get_latest_jenkins_job_build_id(job_name):
    conn = httplib.HTTPConnection(YOUR_JENKINS_IP, YOUR_JENKINS_PORT)
    //Your Jenkins crentials
    auth = base64.b64encode(YOUR_USERNAME+":"+YOUR_PASSWORD).decode("ascii")
    head = { 'Authorization' : 'Basic %s' %  auth }
    conn.request("POST", "/job/YOUR_JOB_NAME/api/json?pretty=true", headers = head)
    
    res = conn.getresponse()
    print(res.status)
    print(res.reason)
    resp_str = res.read();
    #print(resp_str)
    resp_dict = json.loads(resp_str)
    #print(resp_dict['lastBuild']['number'])
    conn.close()
    return resp_dict['lastBuild']['number']
    
def get_jenkins_job_status(buildId):
    print("----get jenkins job status start-------")
    conn = httplib.HTTPConnection(YOUR_JENKINS_IP, YOUR_JENKINS_PORT)
    //Your Jenkins crentials
    auth = base64.b64encode(YOUR_USERNAME+":"+YOUR_PASSWORD).decode("ascii")
    head = { 'Authorization' : 'Basic %s' %  auth }
    conn.request("POST", "/job/YOUR_JOB_NAME/"+str(buildId)+"/api/json?pretty=true", headers = head)
    
    res = conn.getresponse()
    print(res.status)
    print(res.reason)
    resp_str = res.read();
    #print(resp_str)
    resp_dict = json.loads(resp_str)
    #print(resp_dict['result'])
    conn.close()
    print("----get jenkins job status end-------")
    return resp_dict['result']
    
def set_aws_job_status(aws_job_id, jenkins_job_status):
    try:
        
        client = boto3.client('codepipeline')
        
        if jenkins_job_status == "SUCCESS":
            print("SUCCESS?????")
            response = client.put_job_success_result(jobId=aws_job_id)
            print(response)
        else:
            print("FAILED?????")
            response = client.put_job_failure_result(jobId=aws_job_id, failureDetails={'type': 'JobFailed', 'message': 'Test failed', 'externalExecutionId': str(aws_job_id)})
            print(response)
    except Exception as e:
        print('Function failed due to exception.') 
        print(e)
    
def lambda_handler(event, context):
    print('0. get latest jenkins job id')
    current_jenkins_build_number = get_latest_jenkins_job_build_id(YOUR_JENKINS_JOB_NAME)
    print(current_jenkins_build_number)
    
    print('1. triggering the jekins job')
    trigger_jenkins_job()
    
    print('2. get latest jenkins job id')
    current_jenkins_build_number = get_latest_jenkins_job_build_id(YOUR_JENKINS_JOB_NAME)
    print(current_jenkins_build_number)
    
    print('3. get latest jenkins job status')
    current_status = get_jenkins_job_status(current_jenkins_build_number)
    print(current_status)
    
    for i in range(0,100):
        print("in the loop?")
        print(i)
        current_status = get_jenkins_job_status(current_jenkins_build_number)
        print(current_status)
        if str(current_status) in "None":
            time.sleep(1)
            print('waiting for job to be triggered')
        else:
            break
    current_status = get_jenkins_job_status(current_jenkins_build_number)
    print(current_status)
    
    print('4. get aws job id')
    jobId = event.get("CodePipeline.job").get("id");
    print(jobId)
    
    print('5. set aws job status')
    set_aws_job_status(jobId, current_status)
    
    return "Complete."
