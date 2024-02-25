import math
import re
from typing import List, Any
from itertools import permutations
from job import Job

from geopy.distance import distance

# Global Variables:-
STARTING_TIME = 5
INFINITY = 1000 * 1000 * 1000
VELOCITY = 1.5 
TIME_REQUIRED_FOR_BASEMENT_CHANGE = 90
MAX_CARS_PER_WORKER = 40
BASEMENT_TRAVEL_TIME = 90 
skipped_jobs = []
tenant_data = None
travel_time_map = {}


def timeRequired(jobA, jobB):
    travel_time = travel_time_map.get((jobA.tenantBlockId, jobB.tenantBlockId), INFINITY)
    basement_change_time = TIME_REQUIRED_FOR_BASEMENT_CHANGE * abs(int(jobA.basement[1]) - int(jobB.basement[1]))
    return (travel_time + basement_change_time) / 3600


def getTimeRequired(job):
    try:
        tower_travel_time = distance(
            (tenant_data.get(job.tenantBlockId, {}).get('latitude', 0), tenant_data.get(job.tenantBlockId, {}).get('longitude', 0)),
            (tenant_data.get(job.basement, {}).get('latitude', 0), tenant_data.get(job.basement, {}).get('longitude', 0))
        ).m / VELOCITY
        return tower_travel_time
    except KeyError as e:
        print(f"KeyError in getTimeRequired: {e}")
        return 0

def getTimeRequired(job, last_location):
    try:
        tower_travel_time = distance(
            (tenant_data.get(last_location, {}).get('latitude', 0), tenant_data.get(last_location, {}).get('longitude', 0)),
            (tenant_data.get(job.basement, {}).get('latitude', 0), tenant_data.get(job.basement, {}).get('longitude', 0))
        ).m / VELOCITY
        return tower_travel_time
    except KeyError as e:
        print(f"KeyError in getTimeRequired: {e}")
        return 0

def calculateTravelTime(tenant_data):
    try:
        if 'blocks' not in tenant_data:
            raise ValueError("tenant_data must contain a 'blocks' key")
        block_data = tenant_data['blocks']
        if not isinstance(block_data, list):
            raise ValueError("Block data must be a list of dictionaries")
        travel_time_matrix = {}
        for block in block_data:
            if not isinstance(block, dict):
                raise ValueError("Block data must be a list of dictionaries")
            block_name = block['name']
            travel_time_matrix[block_name] = {}
            for other_block in block_data:
                if block_name != other_block['name']:
                    travel_time = timeRequired(block, other_block)
                    travel_time_matrix[block_name][other_block['name']] = travel_time
        return travel_time_matrix
    except Exception as e:
        print(f"Error in calculateTravelTime: {e}")


def assignJobs(tenant, jobs, workers):
    try:
        print("Assigning jobs...")
        global tenant_data
        tenant_data = tenant
        if not isinstance(tenant_data, dict):
            raise ValueError("tenant_data must be a dictionary")
        calculateTravelTime(tenant_data)
        sorted_jobs = sorted(jobs, key=lambda x: (x.deadline, x.estimatedDuration, x.basement))
        worker_assignments = {worker: {'jobs': [], 'capacity': MAX_CARS_PER_WORKER, 'total_time_worked': 0} for worker in workers}
        for job in sorted_jobs:
            min_travel_time = float('inf')
            best_worker = None
            for worker in workers:
                travel_time_to_job = sum([timeRequired(job, assigned_job) for assigned_job in worker_assignments[worker]['jobs']])
                if worker_assignments[worker]['capacity'] > 0 and worker_assignments[worker]['total_time_worked'] <= sum([worker_assignments[w]['total_time_worked'] for w in workers])/len(workers):
                    prev_job = worker_assignments[worker]['jobs'][-1] if worker_assignments[worker]['jobs'] else None
                    travel_time_to_next_basement = 0
                    if prev_job:
                        travel_time_to_next_basement = timeRequired(prev_job, job)
                    total_travel_time = travel_time_to_job + travel_time_to_next_basement
                    if total_travel_time < min_travel_time:
                        min_travel_time = total_travel_time
                        best_worker = worker
            if best_worker:
                worker_assignments[best_worker]['jobs'].append(job)
                worker_assignments[best_worker]['capacity'] -= 1
                worker_assignments[best_worker]['total_time_worked'] += job.estimatedDuration + travel_time_to_next_basement
            else:
                print(f"No available worker found for job {job.id}.")
        result = {}
        for worker_id, assignments in worker_assignments.items():
            result[worker_id] = {'jobs': [{'id': job.id, 'deadline': job.deadline, 'estimatedDuration': job.estimatedDuration} for job in assignments['jobs']], 'total_time_worked': assignments['total_time_worked']}
        return result
    except Exception as e:
        print(f"Error in assignJobs: {e}")