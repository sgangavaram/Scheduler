import base64
from typing import Dict, Any

import assigning
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timedelta
import traceback
import pytz
import json
from job import Job, sanitize_jobs
from assigning import assignJobs, STARTING_TIME, timeRequired
from printing import passive_print, print_decimal_time


tenant = None
run_date = None
next_date = None
worker_ids = []
scheduled_jobs = []
skipped_jobs = []
scheduled_timings = {}
IAM = 'cloud_function'


# initialize firebase sdk in local
PROJECT_NAME = 'fosterate-dev'
# initialize firebase sdk
cred = credentials.Certificate("ServiceAccountKeyDev.json")
firebase_admin.initialize_app(cred)
# get firestore client
FIRESTORE_CLIENT = firestore.client()

# # initialize firebase sdk in CF
# PROJECT_NAME = 'fosterate'
# CREDENTIALS = credentials.ApplicationDefault()
# firebase_admin.initialize_app(CREDENTIALS, {
#     'projectId': PROJECT_NAME,
# })
# FIRESTORE_CLIENT = firestore.client()


class JobSheet:
    def __init__(self, id, assigned_to, assigned_to_name, tenant_id, date, updated_by, updated_on, created_by, created_on, estimated_travelling_time, number_of_jobs):
        self.id = id
        self.assignedTo = assigned_to
        self.assignedToName = assigned_to_name
        self.tenantId = tenant_id
        self.date = date
        self.updatedBy = updated_by
        self.updatedOn = updated_on
        self.createdBy = created_by
        self.createdOn = created_on
        self.estimatedTravellingTime = estimated_travelling_time
        self.numberOfJobs = number_of_jobs


def get_jobs(run_date, status, tenant_id):
    jobs = []
    docs = FIRESTORE_CLIENT.collection(u'jobs').where(u'status', u'==', status).where(u'tenantId', u'==', tenant_id).where(u'date', u'>=', run_date).where(u'date', u'<', next_date).stream()
    for doc in docs:
        job = doc.to_dict()
        try:
            jobs.append(
                Job(
                    job.get("id"),
                    job.get("bookingItemId"),
                    job.get("deadline"),
                    job.get("userId"),
                    job.get("tenantId"),
                    job.get("tenantName"),
                    job.get("tenantBlockId"),
                    job.get("tenantBlockName"),
                    job.get("basement"),
                    job.get("status"),
                    job.get("locationCoordinates"),
                    job.get("assignedTo"),
                    job.get("assignedToName"),
                    job.get("estimatedDuration"),
                    job.get("date"),
                    job.get("team"),
                    job.get("servicesInfo"),
                    job.get("job_type"),
                    job.get("emailOnFailure"),
                    job.get("notifyOnFailure"),
                    job.get("stage"),
                    job.get("vehicleId"),
                    job.get("vehicleMakeName"),
                    job.get("vehicleMakeId"),
                    job.get("vehicleModelName"),
                    job.get("vehicleModelId"),
                    job.get("vehicleNumber"),
                    job.get("vehicleImageUrl"),
                    job.get("vehicleInternalImageUrl"),
                    job.get("parkingLocation"),
                    job.get("isFlagged"),
                    job.get("rescheduleStreak"),
                )
            )
        except Exception as e:
            print("An Error Occurred : ", e, traceback.format_exc())
    return jobs


def get_available_workers(tenant_id):
    # Check with leave module
    global tenant
    tenant = FIRESTORE_CLIENT.document('tenants/' + tenant_id).get().to_dict()
    return tenant.get('workers')


def create_job_sheets(tenant_id, final_jobs):
    now = datetime.now()
    global run_date, next_date
    print("Fetching jobsheets between", run_date, next_date)
    job_sheets_ref = FIRESTORE_CLIENT.collection('job-sheets')
    user_ref = FIRESTORE_CLIENT.collection('users')
    # print(final_jobs)
    for worker in worker_ids:
        if len(final_jobs[worker]) > 0:
            print("Working on worker:", worker)
            # todo: handle if worker dict is not present
            worker_doc = user_ref.document(worker).get()
            worker_dict = worker_doc.to_dict()
            job_sheet = None
            job_sheets_a = job_sheets_ref.where('assignedTo', '==', worker).where(u'date', u'>=', run_date).where(u'date', u'<', next_date).stream()
            available_job_sheets = []
            for js in job_sheets_a:
                print(js.to_dict())
                available_job_sheets.append(js)
            if any(available_job_sheets):
                # todo: re-calculate the travelling time and the effective sequence based on the collation of all jobs that are present for that worker
                available_job_sheet = list(available_job_sheets)[0].to_dict()
                print("JobSheet already present for current day")
                job_sheet = JobSheet(available_job_sheet.get('id'),
                                     available_job_sheet.get('assignedTo'),
                                     available_job_sheet.get('assignedToName'),
                                     available_job_sheet.get('tenantId'),
                                     available_job_sheet.get('date'),
                                     IAM,
                                     now,
                                     available_job_sheet.get('createdBy'),
                                     available_job_sheet.get('createdOn'),
                                     available_job_sheet.get('estimatedTravelTime'),
                                     available_job_sheet.get('numberOfJobs'))
            else:
                job_sheet_id = job_sheets_ref.document().id
                print("Creating job sheet id", job_sheet_id)
                job_sheet = JobSheet(job_sheet_id, worker, worker_dict['name'], tenant_id, run_date, IAM, now, IAM, now, None, None)
            for job in final_jobs[worker]:
                job.jobSheetId = job_sheet.id
                job.assignedTo = worker
                job.assignedToName = worker_dict['name']
                job.estimatedStartTime = doubleToDate(job.estimatedStartTime) if type(job.estimatedStartTime) != datetime else job.estimatedStartTime
                job.estimatedEndTime = doubleToDate(job.estimatedEndTime) if type(job.estimatedEndTime) != datetime else job.estimatedEndTime
                job.modifiedBy = IAM
                job.modifiedOn = now
                FIRESTORE_CLIENT.collection('jobs').document(job.id).update(job.__dict__)
            job_sheet.estimatedTravellingTime = print_decimal_time(scheduled_timings[worker], " ")
            job_sheet.numberOfJobs = len(final_jobs[worker]) + job_sheet.numberOfJobs if any(available_job_sheets) else len(final_jobs[worker])
            job_sheets_ref.document(job_sheet.id).set(job_sheet.__dict__)


def dateToDouble(value):
    value=value.astimezone(pytz.timezone('Asia/Kolkata'))
    return value.hour+value.minute/60


def doubleToDate(value):
    hours = int(value/1)
    minutes = int((value%1)*60)
    today = datetime.now().astimezone(pytz.timezone('Asia/Kolkata'))
    date_val = None
    if 23 < hours < 47:
        hours = int(hours%24)
        date_val = (today + timedelta(days=1)).replace(hour=hours,minute=minutes)
    else:
        date_val = today.replace(hour=hours,minute=minutes)
    return date_val


def main(payload):
    global worker_ids, scheduled_jobs, tenant, run_date, next_date
    print("Starting Execution:", datetime.now())
    try:
        tenant_id = payload.get("tenant_id")
        run_date = payload.get("run_date")
        run_date = datetime.strptime(run_date, "%d-%m-%Y")
        run_date = pytz.timezone('Asia/Kolkata').localize(run_date)
        next_date = run_date + timedelta(days=1)
        worker_ids = get_available_workers(tenant_id)
        jobs = get_jobs(run_date, 1, tenant_id)    # status 1 is scheduled, status 2 is in-progress todo: make status as 1
        print("Total Jobs:", len(jobs), "Tenant Id:", tenant_id, "Run Date:", run_date)
        print("##########JOBS##########",len(jobs))
        for job in jobs:
            job.pr()
        if len(jobs) > 0:
            print("##########WORKERS##########")
            for worker in worker_ids:
                print(worker)
            temp_jobs = sanitize_jobs(jobs, list(tenant['tenantBlocks'].keys()))
            # print(temp_jobs)
            scheduled_jobs = assignJobs(tenant, temp_jobs, worker_ids)
            print("##########Scheduled JOBS##########")
            passive_print(scheduled_jobs)
            print("##########Creating JOB Sheets##########")
            # create_job_sheets(tenant_id, scheduled_jobs)
        else:
            print("Terminating the process as there are no unscheduled jobs")
    except Exception as e:
        print("An Error Occurred : ", e, traceback.format_exc())
    finally:
        print("Ending Execution:", datetime.now())


# main({"tenant_id":'jains-carlton-creek', "run_date":"25-2-2024"})
main({"tenant_id":'poulomi-aristos', "run_date":"25-2-2024"})
# main({"tenant_id": 'prestige-highfields', "run_date": "19-8-2023"})


# def pub_main(event, context):
#     pubsub_message = base64.b64decode(event['data']).decode('utf-8')
#     print(pubsub_message)
#     main(json.loads(pubsub_message))
