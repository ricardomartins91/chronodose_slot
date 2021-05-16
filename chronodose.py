from pushsafer import init, Client
from time import sleep
import requests


def chonodose_available(department_number):
    r = requests.get(f"https://vitemadose.gitlab.io/vitemadose/{department_number}.json")
    if r.status_code != 200:
        print(f"Failed : Status code {r.status_code}")
        return
    centers_available = r.json().get('centres_disponibles', [])

    available_dose = []
    for center in centers_available:
        appointment_schedules = center.get('appointment_schedules', [])
        for schedule in appointment_schedules:
            if schedule['name'] != "chronodose" or schedule['total'] == 0:
                continue

            available_dose.append({"center_name": center.get('nom'),
                                   "center_address": center.get('metadata').get('address'),
                                   "next_schedule": center.get('prochain_rdv'),
                                   "appointment_url": center.get('url'),
                                   "maps_url": f"http://maps.google.com/maps?q={center.get('location').get('latitude')},"
                                               f"{center.get('location').get('longitude')}"})

    return available_dose


def push_notification(token, user, title, message):
    r = requests.post("https://api.pushover.net/1/messages.json",
                      data={"token": token,
                            "user": user,
                            "title": title,
                            "message": message})
    return r.status_code


def main():
    department_number = XX
    chronodoses = chonodose_available(department_number)

    token_api = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
    user_api = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
    notif_title = "CHRONODOSE DISPO"

    log_file = "./chronodose.log"
    if chronodoses:
        print("Some available slots found")
        for dose in chronodoses:
            notif_msg = f"{dose['center_name']}\n" \
                        f"{dose['appointment_url']}\n\n" \
                        f"{dose['maps_url']}\n"

            print(notif_msg + "Sending notification...")

            new_appointment = True
            with open(log_file, "r") as f:
                for line in f:
                    if f"{dose['appointment_url']} {dose['next_schedule']}" in line:
                        new_appointment = False
                        continue

            if new_appointment:
                with open(log_file, "a") as f:
                    f.write(f"{dose['appointment_url']} {dose['next_schedule']}\n")
                notif = push_notification(token_api,
                                          user_api,
                                          notif_title,
                                          notif_msg)
                if notif == 200:
                    print("Notification sent.")
                else:
                    print(f"Notification failed : {notif}")
            else:
                print("Old appointment. Notification already sent")
            print("------------------------------")
    else:
        print("There are no available slots")


if __name__ == "__main__":
    main()
