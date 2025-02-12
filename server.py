from drone_mobile import Vehicle
from flask import Flask, request, Response
from threading import Event
import json

class DroneClient:
    def __init__(self, username, password):
        self.client = self.login(username, password)
        if not self.client:
            raise Exception("Unable to login!")
        self.vehicles = {}
        self.main_vehicle_key = ""
        self.parse_vehicles()
        self.app = Flask(__name__)
        self.app.add_url_rule('/lock', 'lock', self.lock, self.lock)
        self.app.add_url_rule('/unlock', 'unlock', self.unlock, self.unlock)
        self.app.add_url_rule('/start', 'start', self.start, self.start)
        self.app.add_url_rule('/stop', 'stop', self.stop, self.stop)
        self.app.add_url_rule('/lockstatus', 'lockstatus', self.lockstatus, self.lockstatus)
        self.app.add_url_rule('/runstatus', 'runstatus', self.runstatus, self.runstatus)
        self.app.add_url_rule('/vehicles', 'vehicles', self.get_vehicles, self.get_vehicles)

    def parse_vehicles(self):
        vehicles = self.client.getAllVehicles()
        for vehicle in vehicles:
            self.vehicles[vehicle['vehicle_name']] = vehicle['device_key']
        if len(self.vehicles) == 1:
            self.main_vehicle_key = vehicle['device_key']
            print(f"Only 1 vehicle found! Set main vehicle to: {list(self.vehicles.keys())[0]}")
        print(f"Loaded {len(self.vehicles)} vehicle(s)!")

    def run(self):
        self.app.run(host='0.0.0.0', port=3219)

    def login(self, username, password):
        try:
            vehicleObject = Vehicle(username, password)
            vehicleObject.auth()
            return vehicleObject
        except:
            return None

    # Handle flask requests
    def is_vehicle_running(self, key):
        resp = self.client.getAllVehicles()
        for vehicle in resp:
            if vehicle["device_key"] == key:
                if vehicle["last_known_state"]["controller"]["engine_on"]:
                    return True
                else:
                    return False
        raise Exception("Unable to get vehicle status")

    def get_vehicles(self):
        if request.method == "GET":
            response = Response(json.dumps(self.client.getAllVehicles()), 200)
            response.headers["Accept"] = "application/json"
            return response
        else:
            return "Invalid Request Method", 405
    
    def lock(self, key=None):
        if request.method == "GET":
            if not key:
                key = self.main_vehicle_key
            try:
                resp = (self.client.lock(key))
                if resp["command_success"]:
                    return "Vehicle Locked", 200
                else:
                    return "Error Locking Car", 500
            except:
                return "Error Locking Car", 500
        else:
            return "Invalid Request Method", 405

    def unlock(self, key=None):
        if request.method == "GET":
            if not key:
                key = self.main_vehicle_key
            try:
                resp = (self.client.unlock(key))
                if resp["command_success"]:
                    return "Vehicle Unlocked", 200
                else:
                    return "Error Unlocking Car", 500
            except:
                return "Error Unlocking Car", 500
        else:
            return "Invalid Request Method", 405

    def start(self, key=None):
        if request.method == "GET":
            if not key:
                key = self.main_vehicle_key
            try:
                if not self.is_vehicle_running(key):
                    resp = (self.client.start(key))
                    if resp["command_success"]:
                        return "Vehicle Started", 200
                    else:
                        return "Error Starting Car", 500
                else:
                    return "Vehicle Started", 200
            except:
                return "Error Starting Car", 500
        else:
            return "Invalid Request Method", 405

    def stop(self, key=None):
        if request.method == "GET":
            if not key:
                key = self.main_vehicle_key
            try:
                if self.is_vehicle_running(key):
                    resp = (self.client.stop(key))
                    if resp["command_success"]:
                        return "Vehicle Stopped", 200
                    else:
                        return "Error Stopping Car", 500
                else:
                    return "Vehicle Stopped", 200
            except:
                return "Error Stopping Car", 500
        else:
            return "Invalid Request Method", 405

    def lockstatus(self, key=None):
        if request.method == "GET":
            if not key:
                key = self.main_vehicle_key
            try:
                resp = self.client.getAllVehicles()
                for vehicle in resp:
                    if vehicle["device_key"] == key:
                        if vehicle["last_known_state"]["controller"]["armed"]:
                            return "Locked", 200
                        else:
                            return "Unlocked", 200
                return "Unknown", 400
            except:
                return "Unknwon", 500
        else:
            return "Invalid Request Method", 405

    def runstatus(self, key=None):
        if request.method == "GET":
            if not key:
                key = self.main_vehicle_key
            try:
                if self.is_vehicle_running(key):
                    return "Running", 200
                else:
                    return "Not Running", 200
            except:
                return "Unknwon", 500
        else:
            return "Invalid Request Method", 405
        
def main():
    client = DroneClient("DRONE EMAIL GOES HERE", "DRONE PASSWORD GOES HERE")
    client.run()

if __name__ == "__main__":
    main()
