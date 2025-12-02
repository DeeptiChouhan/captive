import json
import time
from pages.job_page import JobPage
from pages.login_page import LoginPage
from pathlib import Path

def load_job_data():
    DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "job_data.json"
    with open(DATA_PATH, "r") as f:
        return json.load(f)

def login_as_super_admin(page):
    login = LoginPage(page)
    login.goto()
    print("DEBUG: Login page loaded:", page.url)
    login.login_with_role("superAdmin")

def test_new_install_job_creation(page):
    login_as_super_admin(page)
    data = load_job_data()
    job = JobPage(page) 
    job.add_job()
    job.select_new_install_job_type()
    job.fill_order_number(data["orderNumber"])
    job.select_technician(data["technician"])
    scheduled_time = job.schedule_one_hour_later()
    job.select_customer(data["customer"]) 

    """job.select_subsidiary(data["subsidiary"])
    job.verify_contact_person_options([
        data["customer"],
        data["subsidiary"]
    ])"""

    job.select_address(data["address"])
    job.select_device_type(1)
    v1 = data["vehicle1"]
    job.fill_vehicle(
        index=0,
        license_plate=v1["licensePlate"],
        vin=v1["vin"],
        brand=v1["brand"],
        vtype=v1["type"]
    )  
    job.add_new_vehicle()

    v2 = data["vehicle2"]
    job.fill_vehicle(
        index=1,
        license_plate=v2["licensePlate"],
        vin=v2["vin"],
        brand=v2["brand"],
        vtype=v2["type"]
    )
    job.save_job()
    job.validate_job_created() 
    time.sleep(1)

def test_install_change_job_creation(page):
    login_as_super_admin(page)
    data = load_job_data()
    job = JobPage(page) 
    job.add_job()
    job.select_install_change_job_type()
    job.select_change_reason("Hardware Repair")
    job.fill_order_number(data["orderNumber"])
    job.select_technician(data["technician"])
    scheduled_time = job.schedule_one_hour_later()
    job.select_customer(data["customer"]) 

    """job.select_subsidiary(data["subsidiary"])
    job.verify_contact_person_options([
        data["customer"],
        data["subsidiary"]
    ])"""

    job.select_address(data["address"])
    job.select_device_type(2)
    v1 = data["vehicle1"]
    job.fill_vehicle(
        index=0,
        license_plate=v1["licensePlate"],
        vin=v1["vin"],
        brand=v1["brand"],
        vtype=v1["type"]
    )
    job.save_job()
    job.validate_job_created() 
    time.sleep(1)

def test_install_change_job_for_Service_intervention(page):
    login_as_super_admin(page)
    data = load_job_data()
    job = JobPage(page) 
    job.add_job()
    job.select_install_change_job_type()
    job.select_change_reason("Service Intervention")
    job.fill_order_number(data["orderNumber"])
    job.select_technician(data["technician"])
    scheduled_time = job.schedule_one_hour_later()
    job.select_customer(data["customer"]) 

    """job.select_subsidiary(data["subsidiary"])
    job.verify_contact_person_options([
        data["customer"],
        data["subsidiary"]
    ])"""

    job.select_address(data["address"])
    job.select_device_type(3)
    v1 = data["vehicle1"]
    job.fill_vehicle(
        index=0,
        license_plate=v1["licensePlate"],
        vin=v1["vin"],
        brand=v1["brand"],
        vtype=v1["type"]
    )
    job.save_job()
    job.validate_job_created() 
    time.sleep(1)
