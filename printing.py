from assigning import STARTING_TIME, getTimeRequired

def timeRequired(jobA, jobB):
    time = getTimeRequired(jobA.location, jobB.location)

    time += 30 * abs(jobA.basement - jobB.basement)

    return time / 3600


def print_decimal_time(a, c):
    seconds = a * 3600
    z = seconds / 3600
    z = int(z)
    z = str(z)
    if len(z) == 1:
        z = "0" + z
    sub_string = z + c + ":" + c
    seconds %= 3600
    z = seconds / 60
    z = int(z)
    z = str(z)
    if len(z) == 1:
        z = "0" + z
    sub_string = sub_string + z + c + ":" + c
    seconds %= 60
    z = seconds
    z = int(z)
    z = str(z)
    if len(z) == 1:
        z = "0" + z
    sub_string = sub_string + z
    print(sub_string , end="\t\t")
    return sub_string


def calculate_and_print(jobList):
    for i in jobList.keys():
        time = STARTING_TIME
        zz = 0
        if len(jobList[i]) == 0:
            print("Worker", i, "No jobs to process")
            continue
        prev_job = jobList[i][0]
        for job in jobList[i]:
            time_required = timeRequired(job, prev_job)
            time += time_required
            zz += time_required
            job.startTime = time
            time += job.estimatedDuration / 3600
            job.endTime = time
            prev_job = job
        print("Worker ", i,len(jobList[i]))
        for job in jobList[i]:
            if len(job.parentJobs) == 0:
                job.println()
            else:
                kkk = len(job.parentJobs)
                for jj in range(kkk):
                    job.parentJobs[jj].println()
                    if jj != kkk - 1:
                        print()
            print_decimal_time(job.startTime, ' ')
            print_decimal_time(job.endTime, ' ')
            print()
            # print("\t\t", job.index)
        print("Travelling Time: ")
        print_decimal_time(zz, '-')
        print()
        print()

def passive_print(jobList):
    for key, value in jobList.items():
        print(f"Worker: {key}")
        print(f"Jobs_Assigned: {value}")
        print()
# def passive_print(jobList):
#     for i in jobList.keys():
#         print("Worker ", i,len(jobList[i]))
#         for job in jobList[i]:
#             print(job.id + "\t" + job.deadline +"\t" + job.estimatedDuration)
#             # print(str(job.vehicleId) + "-" + job.tenantBlockId + "-" + str(job.basement) + "\t" + str(job.id) + "\t" + str(job.deadline) + "\t" + str(job.estimatedDuration) + "\t")
#             # print_decimal_time(job.estimatedStartTime, ' ')
#             # print_decimal_time(job.estimatedEndTime, ' ')
#             print()
#             # print("\t\t", job.index)
#         print()
#         print()