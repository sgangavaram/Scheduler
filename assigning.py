import math
from typing import List, Any

from geopy.distance import distance

# Global Variables:-
STARTING_TIME = 5
INFINITY = 1000 * 1000 * 1000
VELOCITY = 1.5  # meter per sec.
TIME_REQUIRED_FOR_BASEMENT_CHANGE = 90  # meter per sec.
skipped_jobs = []
tenant_data = None

def assignJobs(tenant, jobs, workers):
    global tenant_data
    tenant_data = tenant
    '''Your assigning logic goes here
    This method has to return a dictionay where the key is the worker_id and the value contains a list of jobs basis sorted by the assigning order
    '''
    return jobs