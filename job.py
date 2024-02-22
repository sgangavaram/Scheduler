class Job:
    id = None
    jobSheetId = None
    bookingItemId = None
    deadline = None
    userId = None
    tenantId = None
    tenantName = None
    tenantBlockId = None
    tenantBlockName = None
    basement = None
    status = None
    actualEndTime = None
    actualStartTime = None
    locationCoordinates = None
    assignedTo = None
    assignedToName = None
    estimatedStartTime = None
    estimatedEndTime = None
    estimatedDuration = None
    date = None
    team = None
    servicesInfo = None
    job_type = None
    emailOnFailure = False
    notifyOnFailure = False
    stage = None
    vehicleId = None
    # vehicleMakeName = None
    # vehicleMakeId = None
    # vehicleModelName = None
    # vehicleModelId = None
    vehicleNumber = None
    # vehicleImageUrl = None
    # vehicleInternalImageUrl = None
    parkingLocation = None
    # parentJobs = []
    # isSkipped = False
    isFlagged = None
    rescheduleStreak = None

    def __init__(self, _id, booking_item_id, deadline, user_id, tenant_id, tenant_name, tenant_block_id, tenant_block_name, basement, status, location_coordinates, assigned_to, assigned_to_name, estimated_duration, date, team, services_info, _type, email_on_failure, notify_on_failure, stage, vehicle_id, vehicle_make_name, vehicle_make_id, vehicle_model_name, vehicle_model_id, vehicle_number, vehicle_image_url, vehicle_internal_image_url, parking_location, is_flagged, reschedule_streak):
        self.id = _id
        self.bookingItemId = booking_item_id
        self.deadline = deadline
        self.userId = user_id
        self.tenantId = tenant_id
        self.tenantName = tenant_name
        self.tenantBlockId = tenant_block_id
        self.tenantBlockName = tenant_block_name
        self.basement = basement
        self.status = status
        self.locationCoordinates = location_coordinates
        self.assignedTo = assigned_to
        self.assignedToName = assigned_to_name
        self.estimatedDuration = estimated_duration
        self.date = date
        self.team = team
        self.servicesInfo = services_info
        self.job_type = _type
        self.emailOnFailure = email_on_failure
        self.notifyOnFailure = notify_on_failure
        self.stage = stage
        self.vehicleId = vehicle_id
        self.vehicleMakeName = vehicle_make_name
        self.vehicleMakeId = vehicle_make_id
        self.vehicleModelName = vehicle_model_name
        self.vehicleModelId = vehicle_model_id
        self.vehicleNumber = vehicle_number
        self.vehicleImageUrl  = vehicle_image_url
        self.vehicleInternalImageUrl = vehicle_internal_image_url
        self.parkingLocation = parking_location
        self.parentJobs = []
        self.isFlagged = is_flagged
        self.rescheduleStreak = reschedule_streak
    def pr(self):
        print("deadline:", self.deadline, "job_id:", self.id, "vid:", self.vehicleId, "duration:", self.estimatedDuration)

    def println(self):
        print(str(self.vehicleId) + "-" + self.tenantBlockId + "-" + str(self.basement) + "\t" + str(self.id) + "\t" + str(self.deadline) + "\t" + str(self.estimatedDuration) + "\t", end=" ")


def sanitize_jobs(jobs, tenant_blocks):
    print(tenant_blocks)
    print("You can perform your sanitizations here!!!")
    return jobs
