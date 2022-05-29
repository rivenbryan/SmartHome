# Smart IOT Home
 An IOT project that uses smart-door with 2-factor authentication and live CCTV footage. 
 This project was done using RaspberryPi.


## Overview of Project
### A. What is Smart Home about?
This project is a security solution for a Smart Home by implementing different security features such as a Smart Door with 2-Factor Authentication, Smart car-plate authentication and live CCTV footage.

At the entrance of the Smart Garage, the camera will take a snapshot of the carplate. Next, the 
Garage door will only be opened if the car-plate is authorised. Once the owner has parked his car, 
he can proceed to enter his Smart Home. 

There is also an ongoing livestream that shows real time 
footage of what happens just outside the Garage, to deter any possible intruders.

To enter his Smart Home, the owner has to key in a 4-pin password into the keypad. The owner has 
only a limited number of times that he can try or else he will be locked out of the door. When the 
user hits the number of thresholds, he will receive an email with the new pin. He can then key in 
the new pin to pass the first authentication process. 

The owner will also be alerted with a Telegram 
message informing him that someone had exceeded the number of thresholds.
Next, the facial recognition will begin and the camera will start scanning for faces in the room. The 
user has only 10 seconds to complete this process. If the facial recognition recognises the owner, it 
will allow the user to access the Smart Home. The LCD screen will then welcome and address the 
owner by his name.
Once the user enters the room, the room will start recording Temperature and these values are 
recorded to the Amazon Web Service (AWS) database. Later on, the recorded values can be seen 
via the web-page in the form of a line graph.
Lastly, the LCD screen will flash the current temperature that is detected in the Smart Home

### B. How the final RPI set-up looks like
![image](https://user-images.githubusercontent.com/9747097/170878764-66959aa0-bde9-4d8e-8874-9a62bc689f7b.png)
![image](https://user-images.githubusercontent.com/9747097/170878812-1cf760c9-aee2-4e90-a402-6f0b6e41d66c.png)


### C. How the final Website looks like
![image](https://user-images.githubusercontent.com/9747097/170878851-0befc9d9-624d-458a-b522-c84b02231e89.png)
![image](https://user-images.githubusercontent.com/9747097/170878864-23e0333d-6160-4a45-9eaa-b58ed0f8ebab.png)
![image](https://user-images.githubusercontent.com/9747097/170878875-b2440711-8650-44ff-ab01-a93e1ddcc4a0.png)



