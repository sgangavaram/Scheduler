import math
import re
from typing import List, Any
from itertools import permutations
from job import Job

from geopy.distance import distance

# Global Variables:-
STARTING_TIME = 5
INFINITY = 1000 * 1000 * 1000
VELOCITY = 1.5  # meter per sec.
TIME_REQUIRED_FOR_BASEMENT_CHANGE = 90  # meter per sec.
MAX_CARS_PER_WORKER = 40
BASEMENT_TRAVEL_TIME = 90 
skipped_jobs = []
tenant_data = None
travel_time_map = {}

# def getTimeRequired(t1, t2):
#     # returns time required in seconds
#     global tenant_data
#     # print(tenant_data)
#     # Distance = distance((location1['latitude'],location1['longitude']), (location2['latitude'],location2['longitude'])).m
#     Distance = distance((tenant_data['tenantBlocks'][t1]['locationCoordinates']['latitude'], tenant_data['tenantBlocks'][t1]['locationCoordinates']['longitude']),(tenant_data['tenantBlocks'][t2]['locationCoordinates']['latitude'], tenant_data['tenantBlocks'][t2]['locationCoordinates']['longitude'])).m
#     return Distance / VELOCITY


# def timeRequired(jobA, jobB):
#     # indA = tower_index[jobA.tower]
#     # indB = tower_index[jobB.tower]
#     # time = travellingTimes[indA][indB]
#     time = getTimeRequired(jobA.tenantBlockId, jobB.tenantBlockId)
#     time += TIME_REQUIRED_FOR_BASEMENT_CHANGE * abs(int(jobA.basement[1]) - int(jobB.basement[1]))
#     return time / 3600

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
    
# def calculateTravelTime(tenant_data):
#     for block_id1 in tenant_data:
#         if isinstance(tenant_data[block_id1], dict):
#             for block_id2 in tenant_data:
#                 if block_id1 != block_id2:
#                     coord1 = (tenant_data[block_id1]['locationCoordinates']['latitude'], tenant_data[block_id1]['locationCoordinates']['longitude'])
#                     coord2 = (tenant_data[block_id2]['locationCoordinates']['latitude'], tenant_data[block_id2]['locationCoordinates']['longitude'])
#                     distance_meters = distance(coord1, coord2).m
#                     travel_time = distance_meters / VELOCITY
#                     travel_time_map[(block_id1, block_id2)] = travel_time



   
# def assignJobs(tenant, jobs, workers):
#     global tenant_data
#     tenant_data = tenant
#     calculateTravelTime(tenant_data)
#     for i in jobs:
#         X = i.deadline.split('-')[1]
#         if len(X) == 4:
#             X = X[:2]
#         if len(X) == 3:
#             X = X[:1]
#         i.deadline = float(X)

#     sorted_jobs = sorted(jobs, key=lambda x: (x.deadline, x.estimatedDuration, x.basement))
#     for i in sorted_jobs:
#         i.println()

#     num_workers = len(workers)
#     worker_assignments = {worker: {'jobs': [], 'capacity': MAX_CARS_PER_WORKER} for worker in workers}
    
#     for idx, job in enumerate(sorted_jobs):
#         current_worker = workers[idx % num_workers]
#         if worker_assignments[current_worker]['capacity'] > 0:
#             worker_assignments[current_worker]['jobs'].append(job)
#             worker_assignments[current_worker]['capacity'] -= 1
#         else:
#             print(f"No capacity left for worker {current_worker}.")

#     return_dict = {worker_id: [job.id for job in worker_assignments[worker_id]['jobs']] for worker_id in worker_assignments}
    
#     return return_dict


def calculateTravelTime(tenant_data):
    try:
        print("Calculating travel time...")
        travel_time_map = {}
        for block_id1, block_data_list1 in tenant_data.items():
            if isinstance(block_data_list1, list):
                for block_data1 in block_data_list1:
                    for block_id2, block_data_list2 in tenant_data.items():
                        if block_id1 != block_id2 and isinstance(block_data_list2, list):
                            for block_data2 in block_data_list2:
                                coord1 = (block_data1['locationCoordinates']['latitude'], block_data1['locationCoordinates']['longitude'])
                                coord2 = (block_data2['locationCoordinates']['latitude'], block_data2['locationCoordinates']['longitude'])
                                distance_meters = distance(coord1, coord2).m
                                travel_time = distance_meters / VELOCITY
                                travel_time_map[(block_id1, block_id2)] = travel_time
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
        # num_workers = len(workers)
        worker_assignments = {worker: {'jobs': [], 'capacity': MAX_CARS_PER_WORKER} for worker in workers}
        for job in sorted_jobs:
            min_travel_time = float('inf')
            best_worker = None
            for worker in workers:
                travel_time_to_job = sum([timeRequired(job, assigned_job) for assigned_job in worker_assignments[worker]['jobs']])
                if travel_time_to_job < min_travel_time and worker_assignments[worker]['capacity'] > 0:
                    min_travel_time = travel_time_to_job
                    best_worker = worker
            if best_worker:
                worker_assignments[best_worker]['jobs'].append(job)
                worker_assignments[best_worker]['capacity'] -= 1
            else:
                print(f"No available worker found for job {job.id}.")
        return {worker_id: [job.id for job in worker_assignments[worker_id]['jobs']] for worker_id in worker_assignments}
    except Exception as e:
        print(f"Error in assignJobs: {e}")
