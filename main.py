import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

import time


def updateUserRequest(ref, newUser, status):
    # Updating User Request
    # print(status)
    # print(newUser)
    users_ref = ref.child('requests')
    statusKey = newUser + '/status'
    processKey = newUser + '/process'
    # print('start')
    users_ref.update({
        statusKey: status,
        processKey: True
    })
    print('\t \t USER REQUEST UPDATED')


def updateBookTaken(ref, category, bookBarCodeId, flag):
    # print(flag)
    if(flag):
        books_ref = ref.child('books')
        takenKey = category + '/' + bookBarCodeId + '/taken'
        books_ref.update({
            takenKey: flag
        })
    print('\t \t BOOK TAKEN ' + bookBarCodeId)


def startPicking():
    # Robotic Arm Sequence
    print("|----------------- PICKING BOOK  -----------------------|")
    time.sleep(2)
    return True


def startScanning(barCodeId):
    # Scanning
    print("|---------- SCANNING BOOKS FOR ID: " +
          barCodeId + " ---------------|")
    time.sleep(2)
    return True


def startNavigationTo(location):
    # Navigation To Book's location
    print("|----------------- NAVIGATING TO " +
          str(location) + " -----------------|")
    time.sleep(2)
    return True


def returnToStartPoint(location):
    # Navigation To Start/Collection Point
    print("|----------------- RETURNING TO COLLECTION POINT ----------------------|")
    time.sleep(3)
    return True


# FIREBASE DATABASE PART
# Fetch the service account key JSON file contents
cred = credentials.Certificate('./serviceAccount.json')

# Initialize the app with a service account, granting admin privileges
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://auth-development-ef368-default-rtdb.firebaseio.com/',
})

# As an admin, the app has access to read and write all data, regradless of Security Rules
ref = db.reference()
userIds = []
userTime = []
lastUser = ""

# Introduction
print("--------------------------------------------------------")
print("----------------- STARTING SERVER ----------------------")

while(True):

    # GETTING DATA FROM FIREBASE
    userData = ref.get()
    if(userData != None):
        try:
            newUser = list(userData['requests'].keys())[0]
            # print(newUser)

            data = userData['requests'][newUser]
            # print(data['users'][newUser])
            if(newUser != lastUser):
                userIds.insert(0, newUser)

            if((data['process'] == False) and (data['status'] == 'Pending')):
                print(
                    "|----------------- PROCESSING USER ----------------------|")
                print("|--------------------------------------------------------|")
                print("\tROBOT RECIEVED LOCATION: " + data['location'])
                print("|--------------------------------------------------------|")

                # NAVIGATION to data['location]
                positionReached = startNavigationTo(data['location'])

                # BARCODE SCANNING
                if(positionReached == True):
                    bookFound = startScanning(data['bookBarCodeId'])
                    # print(bookFound)
                    if(bookFound):
                        # ROBOTIC ARM SEQUENCE
                        bookPicked = startPicking()
                        # print('Updated')
                        if(bookPicked):
                            # print('start updating')
                            updateUserRequest(ref, newUser, 'Picked')
                            # print('finish updating')
                            updateBookTaken(
                                ref, data['category'], data['bookBarCodeId'], True)
                            returnToStartPoint('location')
                    else:
                        updateUserRequest('Not Found')
                        returnToStartPoint('location')
                else:
                    updateUserRequest('Robot Error')
                    returnToStartPoint('location')
            lastUser = newUser
            print("|--------------------------------------------------------|")

        except:
            print("----------------- Error ----------------------")

    print("-------------- Waiting for New Request -----------------\n")
    time.sleep(2)
