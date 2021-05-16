from pushsafer import init, Client
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
            if schedule['name'] != "chronodose" or schedule['total'] == 1:
                continue

            available_dose.append({"center_name": center.get('nom'),
                                   "center_address": center.get('metadata').get('address'),
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

    token_api = "XXXXXXXXXXXXXXXXXXX"
    user_api = "XXXXXXXXXXXXXXXXXXXXX"
    notif_title = "CHRONODOSE DISPO"

    if chronodoses:
        print("Some available slots found")
        for dose in chronodoses:
            notif_msg = f"{dose['center_name']}\n" \
                        f"{dose['appointment_url']}\n"

            print(notif_msg + "Sending notification...")

            notif = push_notification(token_api,
                                      user_api,
                                      notif_title,
                                      notif_msg)
            if notif == 200:
                print("Notification sent.")
            else:
                print(f"Notification failed : {notif}")
            print("------------------------------")


if __name__ == "__main__":
    main()
