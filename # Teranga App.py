####### Teranga App --> 15112 Term Project #######

from cmu_graphics import *
import csv
import json
from PIL import Image
# from notifypy import Notify


##### Notification Handling #####
# Adapted from https://medium.com/@rajputgajanan50/simplify-desktop-notifications-with-notify-py-in-python-e8ea48fead08

# def sendUserNotification(submittedTitle, submittedMessage):

#     notification = Notify()
#     notification.title = submittedTitle
#     notification.message = submittedMessage
#     notification.timeout = 5000  # 5 seconds
#     notification.send()

# def recentlyPurchasedItemsNotification(submittedTitle, submittedMessage):
#     notification = Notify()
#     notification.title = submittedTitle
#     notification.message = submittedMessage
#     notification.timeout = 5000  # 5 seconds
#     notification.send()

##### Load data from the CSV File ##### 

# Adapted from https://www.digitalocean.com/community/tutorials/parse-csv-files-in-python 
def loadData():
    allProducts = []
    spacing = 160
    with open('ProductInfo.csv', 'r') as csv_file:
        reader = csv.reader(csv_file)
        next(reader) # skip headers
        for line in reader:
            # The CSV has two columns: name and price
            name, price = line
            product = Products(name, int(price), 1920/3, 360 - len(allProducts) * 70+spacing)
            spacing -= 40
            allProducts.append(product)

    return allProducts


##### All classes #####

class Products:
    def __init__(self, name, price, x, y, quantity=0, selected=False):
        self.name = name
        self.price = price
        self.quantity = quantity
        self.selected = selected
        self.x = x
        self.y = y
        self.subtotal = self.quantity*self.price
    
    def updateQuantity(self, newQuantity):
        self.quantity = newQuantity
        self.subtotal = self.quantity * self.price

    def draw(self):
        leftMargin = 400  # White box x + margin

        # Draw product name and price
        drawLabel(f'{self.name}', leftMargin, self.y+40, size=25,align='left')
        drawLabel(f'{self.price} XOF', leftMargin+700, self.y+40, size=25,align='right')
        # Draw quantity and subtotal
        drawLabel('Quantity: ', leftMargin+30, self.y+90, size=20,fill='gray',align='left')
        drawLabel(f'Subtotal: {self.subtotal} XOF', leftMargin+700, self.y+90, size=20, fill='gray', align='right')

class Buttons:
    def __init__(self, xpos, ypos, text, size=20):
        self.text = text
        self.size = size
        self.width = len(text) * size * 0.8
        self.height = size * 2
        self.xpos = xpos
        self.ypos = ypos
        
    def draw(self):
        drawRect(self.xpos, self.ypos, self.width, self.height, fill=rgb(251, 112, 65))
        labelX = self.xpos + self.width / 2
        labelY = self.ypos + self.height / 2
        drawLabel(self.text, labelX, labelY, fill='white', size=self.size, align='center')

    def drawNav(self):
        labelX = self.xpos + self.width / 2
        labelY = self.ypos + self.height / 2
        drawLabel(self.text, labelX, labelY, fill='blue', size=self.size, align='center')

    def containsPoint(self, x, y):
        # Check if within the button's bounds
        return (self.xpos <= x <= self.xpos + self.width) and (self.ypos <= y <= self.ypos + self.height)
    
class User:
    def __init__(self,name,number,username,password,address,order=(),budget=0,concern=None,orderHistory=[],userCart=[0,0,0,0]):
        self.name = name
        self.number = number
        self.username = username
        self.password = password
        self.address = address
        self.order = order
        self.budget = budget
        self.concern = concern
        self.orderHistory = orderHistory
        self.userCart = userCart

        self.userInfo = {
            'name': self.name, 
            'number': self.number, 
            'username': self.username, 
            'password': self.password,
            'address': self.address,
            'order': self.order, 
            'budget': self.budget,
            'concern': self.concern,
            'Order History': self.orderHistory
        }

    def __repr__(self):
        return str(self.userInfo)

class textInput:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = ''

    def draw(self):
        # Draw the text inside the textbox
        drawLabel(self.text, self.x + 5, self.y + self.height / 2, size=20, align='left')

    def addText(self, character):
        maxChars = self.width // 10  # Estimate based on average character width
        if len(self.text) < maxChars:
            self.text += character
    

####### Backtracking Integration #######

def isLegal(remainingBudget, productPrice):
    return remainingBudget - productPrice >= 0

def maximizePurchase(products, budget):
    result = dict()
    bestSolution = (dict(), 0, 0)  # (current best solution, total weight, total price)
    return optimizer(products, 0, budget, result, 0, 0, bestSolution)

def optimizer(products, i, budget, result, totalWeight, totalPrice, bestSolution):
    if i == len(products):  # Base case where all products are considered
        if totalWeight > bestSolution[1]:  # Update best solution if current one is better
            bestSolution = (dict(result), totalWeight, totalPrice)
        return bestSolution
    else:
        for quantity in range(budget // products[i]['price'] + 1):
            newPrice = products[i]['price'] * quantity
            newWeight = products[i]['amount (kg)'] * quantity
            if isLegal(budget, newPrice):  # If move is legal, make move
                result[products[i]['name']] = quantity
                bestSolution = optimizer(products, i + 1, budget - newPrice, result, totalWeight + newWeight, totalPrice + newPrice, bestSolution)

                result.pop(products[i]['name']) # Undo move if it doesn't lead to a better solution

        return bestSolution

productsBacktracking = [
    {'name': 'Farine Beignet (5kg)', 'price': 2250, 'amount (kg)': 5},
    {'name': 'Farine Beignet (25kg)', 'price': 12000, 'amount (kg)': 25},
    {'name': 'Farine Patisserie (25kg)', 'price': 12000, 'amount (kg)': 25},
    {'name': 'Farine Complete (25kg)', 'price': 10000, 'amount (kg)': 25}
]


####### App #######

def onAppStart(app):
    reset(app)
    loadUsers(app)

def loadUsers(app):
    with open('UserInfo.json', 'r') as file:
        userList = json.load(file)
        for elem in userList:
            app.users[elem['username']] = User(*elem)
            # Load user cart data
            user = app.users[elem['username']]
            if 'user cart' in elem:
                user.userCart = elem['user cart']

def loadUserCart(app, user):
    if len(user.userCart) == 4:
        app.farineComplete, app.farinePatisserie, app.farineBeignetBig, app.farineBeignetSmall = user.userCart
    else:
        # Handle error or initialize with default values
        app.farineComplete = 0
        app.farinePatisserie = 0
        app.farineBeignetBig = 0
        app.farineBeignetSmall = 0

    for product in app.products:
        if product.name == "Farine Complete (25kg)":
            product.updateQuantity(app.farineComplete)
        elif product.name == "Farine Patisserie (25kg)":
            product.updateQuantity(app.farinePatisserie)
        elif product.name == "Farine Beignet (25kg)":
            product.updateQuantity(app.farineBeignetBig)
        elif product.name == "Farine Beignet (5kg)":
            product.updateQuantity(app.farineBeignetSmall)
    calculateTotal(app)

def reset(app):
    app.users = {} 
    app.newUser = None
    # Textboxes
    app.usernameTextBoxPressed = False
    app.passwordTextBoxPressed = False
    app.nameSignUpTextBoxPressed = False
    app.phoneNumberSignUpTextBoxPressed = False
    app.createUsernameInputPressed = False
    app.createPasswordInputPressed = False
    app.addressTextboxPressed = False

    app.loggedIn = False

    with open('UserInfo.json', 'r') as file: # Got help in OH and from https://www.geeksforgeeks.org/python-json/
        userList = json.load(file)
    for elem in userList:
        app.users[elem['username']] = User(*elem)

    # textInput
    app.userProblemReport = textInput(375, 100, 800, 350)
    app.budgetAmount = 0
    app.budgetInput = textInput(350, 120, 180, 245)
    app.solution = None
    app.products = loadData()
    app.usernameInput = textInput(340, 520, 380, 50)
    app.passwordInput = textInput(340, 620, 380, 50)
    app.nameSignUpInput = textInput(340, 520, 380, 50)
    app.phoneNumberSignUpInput = textInput(340, 620, 380, 50)
    app.createUsernameInput = textInput(800, 520, 380, 50)
    app.createPasswordInput = textInput(800, 620, 380, 50)
    app.addressInput = textInput(356, 700, 800, 150)

    # Images --> Worked with OLAM SA for another project and they gave access to their product image posters
    app.farineBeignetSmallPicture = Image.open("FarineBeignet5kgPhoto.png")
    app.farineBeignetSmallPicture = CMUImage(app.farineBeignetSmallPicture)
    app.farineBeignetBigPicture = Image.open("FarineBeignet25kgPhoto.png")
    app.farineBeignetBigPicture = CMUImage(app.farineBeignetBigPicture)
    app.farinePatisseriePicture = Image.open("FarinePatisserie25kgPhoto.png")
    app.farinePatisseriePicture = CMUImage(app.farinePatisseriePicture)
    app.farineCompletePicture = Image.open("FarineComplete25kgPhoto.png")
    app.farineCompletePicture = CMUImage(app.farineCompletePicture)


    app.width = 1920
    app.height = 1080
    app.total = 0

    app.showThankYouPage = False
    app.notificationTime = False

    # Buttons
    app.signUpButton = Buttons(app.width/3-100, 830, 'Sign Up')
    app.signUpButtonPressed = False
    app.createAccountButton = Buttons(app.width/3, 720, 'Create Account')
    app.createAccountButtonPressed = False
    app.loginButton = Buttons(340, 680, 'Login')
    app.productsButton = Buttons(app.width/3 + 30, app.height/2 - 50, 'Products')
    app.productsNavButton = Buttons(app.width/3 + 350, 30, 'Product') # adjust with font='symbols'
    app.recommendationsButton = Buttons(app.width/3 - 30, app.height/2, 'Recommendations')
    app.recommendationsNavButton = Buttons(app.width/3 + 470, 30, 'Recommendations')
    app.contactUsButton = Buttons(app.width/3 + 15, app.height/2 + 50, 'Contact Us')
    app.contactUsNavButton = Buttons(app.width/3 + 700, 30, f'Contact Us')
    app.submitConcernButton = Buttons(1080, 620, 'Submit')
    app.clearBudgetButton = Buttons(340, 275, 'Clear')
    app.submitProductPageButton = Buttons(app.width/2+100,870,'Submit')
    app.submitBudgetButton = Buttons(543, 275, 'Submit')
    app.productsButtonPressed = False
    app.recommendationsButtonPressed = False
    app.contactUsButtonPressed = False
    app.backButtonPressed = False
    app.submitBudgetButtonPressed = False
    app.submitProductPageButtonPressed = False
    app.returnToLoginPage = False
    app.loginError = False
    app.backButton = Buttons(160,30,'Back')
    app.logoutButton = Buttons(30, 30, 'Logout')

def calculateTotal(app):
    app.total = sum(product.subtotal for product in app.products)

def collectOrder(app):
    orderDict = {}
    totalPrice = 0
    for product in app.products:
        orderDict[product.name] = product.quantity
        totalPrice = app.total
    return orderDict, totalPrice

def handleOrderSubmission(app):
    app.currentUsername = app.usernameInput.text
    currentOrder = collectOrder(app)
    if app.currentUsername in app.users and app.newUser is not None:
        app.newUser.order = currentOrder
        app.newUser.userInfo['order'] = currentOrder
        if not isinstance(app.newUser.orderHistory, list):
            app.newUser.orderHistory = []
            app.newUser.userInfo['Order History'] = []
        app.newUser.orderHistory.append(app.newUser.order)
        app.newUser.userInfo['Order History'] += app.newUser.order

    app.showThankYouPage = True

def saveUserData(app):
    app.currentUsername = app.usernameInput.text
    if app.currentUsername in app.users:
        app.currentUser = app.users[app.currentUsername]

        # Load existing users from the JSON file
        with open('UserInfo.json', 'r') as file:
            userList = json.load(file)

        # Update the data of the current user in the userList
        for userDict in userList:
            if userDict['username'] == app.currentUsername:
                userDict['address'] = app.currentUser.address
                userDict['budget'] = app.currentUser.budget
                userDict['concern'] = app.currentUser.concern
                userDict['Order History'] = app.currentUser.orderHistory
                userDict['order'] = app.currentUser.order
                userDict['user cart'] = [app.farineComplete, app.farinePatisserie,
                                         app.farineBeignetBig,app.farineBeignetSmall]
                break

        # Save the updated userList back to the JSON file
        with open('UserInfo.json', 'w') as file:
            json.dump(userList, file)

def onMousePress(app, mouseX, mouseY):
    # Username
    if (340 <= mouseX <= 720) and (520 <= mouseY <= 570):  
        app.usernameTextBoxPressed = True
    else:
        app.usernameTextBoxPressed = False
    # Password
    if (340 <= mouseX <= 720) and (620 <= mouseY <= 670):
        app.passwordTextBoxPressed = True
    else:
        app.passwordTextBoxPressed = False
    # Name
    if (340 <= mouseX <= 720) and (520 <= mouseY <= 570) and app.signUpButtonPressed:  
        app.nameSignUpTextBoxPressed = True
        app.usernameTextBoxPressed = False
        app.phoneNumberSignUpTextBoxPressed = False
    else:
        app.nameSignUpTextBoxPressed = False

    # Phone
    if (340 <= mouseX <= 720) and (620 <= mouseY <= 670) and app.signUpButtonPressed:
        app.phoneNumberSignUpTextBoxPressed = True
        app.passwordTextBoxPressed = False
        app.nameSignUpTextBoxPressed = False
    else:
        app.phoneNumberSignUpTextBoxPressed = False

    # Create Username
    if (800 <= mouseX <= 1180) and (520 <= mouseY <= 570) and app.signUpButtonPressed: 
        app.createUsernameInputPressed = True
    else:
        app.createUsernameInputPressed = False

    # Create Password
    if (800 <= mouseX <= 1180) and (620 <= mouseY <= 670) and app.signUpButtonPressed: 
        app.createPasswordInputPressed = True
    else:
        app.createPasswordInputPressed = False

    # Create Account + Fill in User Class
    if (app.createAccountButton.containsPoint(mouseX, mouseY) and 
        app.nameSignUpInput.text != '' and app.phoneNumberSignUpInput.text != ''
        and app.createUsernameInput.text != '' and 
        app.createPasswordInput.text != ''):
        app.newUser = User(
            name=app.nameSignUpInput.text,
            number=app.phoneNumberSignUpInput.text,
            username=app.createUsernameInput.text,
            password=app.createPasswordInput.text,
            address=app.addressInput.text,
            budget=app.budgetAmount,
            concern=app.userProblemReport.text,
            orderHistory = [],
            userCart = [0,0,0,0]
        )
        if len(app.newUser.userCart) == 4:
            app.farineComplete, app.farinePatisserie, app.farineBeignetBig, app.farineBeignetSmall = app.newUser.userCart
        else:
            # Handle error or initialize with default values
            app.farineComplete = 0
            app.farinePatisserie = 0
            app.farineBeignetBig = 0
            app.farineBeignetSmall = 0
        # Add the new user to the app.users dictionary
        app.users[app.newUser.username] = app.newUser
        app.returnToLoginPage = True
        app.signUpButtonPressed = False

        # Clear the input fields
        app.nameSignUpInput.text = ""
        app.phoneNumberSignUpInput.text = ""
        app.createUsernameInput.text = ""
        app.createPasswordInput.text = ""

        with open('UserInfo.json', 'r') as file:  
            userList = json.load(file)
        with open('UserInfo.json', 'w') as file:
            json.dump(userList + [app.newUser.userInfo], file)
        
        

    # Log In
    if app.loginButton.containsPoint(mouseX, mouseY):
        enteredUsername = app.usernameInput.text
        enteredPassword = app.passwordInput.text
        # Check if entered credentials match any user
        user = app.users.get(enteredUsername)
        if user and user.password == enteredPassword:
            app.newUser = user
            app.loggedIn = True
            app.currentUsername = enteredUsername
            app.currentUser = app.users[app.currentUsername]
            loadUserCart(app, app.currentUser)
            if len(app.currentUser.userCart) == 4:
                app.farineComplete, app.farinePatisserie, app.farineBeignetBig, app.farineBeignetSmall = app.currentUser.userCart
            else:
                # Handle error or initialize with default values
                app.farineComplete = 0
                app.farinePatisserie = 0
                app.farineBeignetBig = 0
                app.farineBeignetSmall = 0
        else:
            app.loginError = True

    if app.signUpButton.containsPoint(mouseX,mouseY):
        app.signUpButtonPressed = True

        app.usernameInput.text = ''
        app.passwordInput.text = ''
        app.loginError = False
    
    if app.submitProductPageButton.containsPoint(mouseX,mouseY):
        app.submitProductPageButtonPressed = True
        saveUserData(app)
    
    # Products Page Address Entry
    if (app.loggedIn and ((356 <= mouseX <= 1156) 
        and (750 <= mouseY <= 850) and app.productsButton)):
        app.addressTextboxPressed = True
        saveUserData(app)

    if app.loggedIn and app.productsButton and app.submitProductPageButtonPressed:
        app.farineComplete = 0
        app.farinePatisserie = 0
        app.farineBeignetBig = 0
        app.farineBeignetSmall = 0
        app.notificationTime = True
        if app.newUser is not None: 
            handleOrderSubmission(app)
            saveUserData(app)
        if app.notificationTime:

            sendUserNotification('Thank you for your purchase!', 'Your order will be delivered within 24 hours')
            recentlyPurchasedItemsNotification('Here is your recently purchased history', app.newUser.userInfo['Order History'])

        app.notificationTime = False

    # Recommendations Page Budget Entry
    if (app.loggedIn and app.submitBudgetButton.containsPoint(mouseX,mouseY) 
        and app.recommendationsButtonPressed): 
        app.submitProductPageButtonPressed = False
        app.submitBudgetButtonPressed = True
        app.budgetAmount = int(app.budgetInput.text)
        app.currentUsername = app.usernameInput.text
        if app.currentUsername in app.users and app.newUser is not None:
            app.newUser.budget = app.budgetAmount
            app.newUser.userInfo['budget'] = app.budgetAmount

        app.solution = maximizePurchase(productsBacktracking, app.budgetAmount)
        saveUserData(app)
        app.budgetInput.text = ''

    # Contact us Chatbox
    if app.loggedIn and app.submitConcernButton.containsPoint(mouseX, mouseY):
        # Store the text from the userProblemReport textInput into new attribute
        app.submitProductPageButtonPressed = False
        app.currentUsername = app.usernameInput.text
        if app.currentUsername in app.users:
            app.newUser.budget = app.budgetAmount
            app.newUser.userInfo['budget'] = app.budgetAmount

            app.userProblemReport.text = ''

    if app.loggedIn and app.clearBudgetButton.containsPoint(mouseX, mouseY):
        app.budgetInput.text = ''
    
    if (app.loggedIn and ((app.productsButton.containsPoint(mouseX, mouseY) or 
        app.productsNavButton.containsPoint(mouseX, mouseY)))):
        app.submitProductPageButtonPressed = False
        app.productsButtonPressed = True
        app.recommendationsButtonPressed = False
        app.contactUsButtonPressed = False

    elif (app.loggedIn and ((app.recommendationsButton.containsPoint(mouseX, mouseY) 
        or app.recommendationsNavButton.containsPoint(mouseX, mouseY)))):
        app.submitProductPageButtonPressed = False
        app.productsButtonPressed = False
        app.recommendationsButtonPressed = True
        app.contactUsButtonPressed = False

    elif (app.loggedIn and ((app.contactUsButton.containsPoint(mouseX, mouseY) or 
        app.contactUsNavButton.containsPoint(mouseX,mouseY)))):
        app.submitProductPageButtonPressed = False
        app.productsButtonPressed = False
        app.recommendationsButtonPressed = False
        app.contactUsButtonPressed = True

    elif app.loggedIn and app.backButton.containsPoint(mouseX,mouseY):
        app.submitProductPageButtonPressed = False
        app.productsButtonPressed = False
        app.recommendationsButtonPressed = False
        app.contactUsButtonPressed = False
        app.backButtonPressed = True
    
    elif app.loggedIn and app.logoutButton.containsPoint(mouseX,mouseY):
    # Save user data to JSON before logging out
        saveUserData(app)
        # Resetting app state for logout
        app.loggedIn = False
        app.productsButtonPressed = False
        app.recommendationsButtonPressed = False
        app.contactUsButtonPressed = False
        app.backButtonPressed = False
        app.budgetInput.text = ''
        app.userProblemReport.text = ''

        if not app.loggedIn:
            reset(app)
            loadUsers(app)




# Product Page +/-
    # Farine Complete "+" button
    if (580 <= mouseX <= 605) and (268 <= mouseY <= 293) and app.farineComplete<99:
        app.farineComplete += 1
        for product in app.products:
            if product.name == "Farine Complete (25kg)":
                product.updateQuantity(app.farineComplete)
        calculateTotal(app)
    # Farine Complete "-" button
    elif (605 <= mouseX <= 630) and (268 <= mouseY <= 293) and app.farineComplete>0:
        app.farineComplete-=1
        for product in app.products:
            if product.name == "Farine Complete (25kg)":
                product.updateQuantity(app.farineComplete)
        calculateTotal(app)

     # Farine Patisserie "+" button
    if (580 <= mouseX <= 605) and (378 <= mouseY <= 403) and app.farinePatisserie<99:
        app.farinePatisserie += 1
        for product in app.products:
            if product.name == "Farine Patisserie (25kg)":
                product.updateQuantity(app.farineComplete)
        calculateTotal(app)
    # Farine Patisserie "-" button
    elif (605 <= mouseX <= 630) and (378 <= mouseY <= 403) and app.farinePatisserie>0:
        app.farinePatisserie-=1
        for product in app.products:
            if product.name == "Farine Patisserie (25kg)":
                product.updateQuantity(app.farinePatisserie)
        calculateTotal(app)

    # Farine Beignet Big "+" button
    if (580 <= mouseX <= 605) and (488 <= mouseY <= 513) and app.farineBeignetBig<99:
        app.farineBeignetBig += 1
        for product in app.products:
            if product.name == "Farine Beignet (25kg)":
                product.updateQuantity(app.farineBeignetBig)
        calculateTotal(app)

    # Farine Beignet Big "-" button
    elif (605 <= mouseX <= 630) and (488 <= mouseY <= 513) and app.farineBeignetBig>0:
        app.farineBeignetBig-=1    
        for product in app.products:
            if product.name == "Farine Beignet (25kg)":
                product.updateQuantity(app.farineBeignetBig)
        calculateTotal(app)
    
    # Farine Beignet Small "+" button
    if (580 <= mouseX <= 605) and (598 <= mouseY <= 623) and app.farineBeignetSmall<99:
        app.farineBeignetSmall += 1
        for product in app.products:
            if product.name == "Farine Beignet (5kg)":
                product.updateQuantity(app.farineBeignetSmall)
        calculateTotal(app)

    # Farine Beignet Small "-" button
    elif (605 <= mouseX <= 630) and (598 <= mouseY <= 623) and app.farineBeignetSmall>0:
        app.farineBeignetSmall-=1  
        for product in app.products:
            if product.name == "Farine Beignet (5kg)":
                product.updateQuantity(app.farineBeignetSmall)
        calculateTotal(app)

def onKeyPress(app, key):
    # Username
    if app.usernameTextBoxPressed:
        if key == 'backspace':
            app.usernameInput.text = app.usernameInput.text[:-1] 
        elif (key == 'left' or key == 'right' or key == 'space' or key == 'tab'
            or key == 'up' or key == 'down' or key == 'enter' or key == 'escape'):
            pass  # Do nothing for these keys
        else:
           app.usernameInput.addText(key) 

    # Password
    elif app.passwordTextBoxPressed:
        if key == 'backspace':
            app.passwordInput.text = app.passwordInput.text[:-1] 
        elif (key == 'left' or key == 'right' or key == 'space' or key == 'tab'
            or key == 'up' or key == 'down' or key == 'enter' or key == 'escape'):
            pass  # Do nothing for these keys
        else:
           app.passwordInput.addText(key) 

    # Name
    elif app.nameSignUpTextBoxPressed:
        if key == 'backspace':
            app.nameSignUpInput.text = app.nameSignUpInput.text[:-1]
        elif (key == 'left' or key == 'right' or key == 'up' or key == 'down' 
              or key == 'enter' or key == 'escape' or key == 'tab'):
            pass  # Do nothing for these keys
        elif key == 'space':
            app.nameSignUpInput.text += ' '
        else:
           app.nameSignUpInput.addText(key)

    # Phone
    elif app.phoneNumberSignUpTextBoxPressed:
        if key == 'backspace':
            app.phoneNumberSignUpInput.text = app.phoneNumberSignUpInput.text[:-1] 
        elif key.isdigit() and len(app.phoneNumberSignUpInput.text)<11:
           app.phoneNumberSignUpInput.addText(key)

    # Create Username
    elif app.createUsernameInputPressed:
        if key == 'backspace':
            app.createUsernameInput.text = app.createUsernameInput.text[:-1] 
        elif (key == 'left' or key == 'right' or key == 'space' or key == 'tab'
            or key == 'up' or key == 'down' or key == 'enter' or key == 'escape'):
            pass  # Do nothing for these keys
        else:
           app.createUsernameInput.addText(key) 

    # Create Password
    elif app.createPasswordInputPressed:
        if key == 'backspace':
            app.createPasswordInput.text = app.createPasswordInput.text[:-1] 
        elif (key == 'left' or key == 'right' or key == 'space' or key == 'tab'
            or key == 'up' or key == 'down' or key == 'enter' or key == 'escape'):
            pass  # Do nothing for these keys
        else:
           app.createPasswordInput.addText(key)

    # Address
    if app.loggedIn and app.addressTextboxPressed and app.productsButtonPressed:
        if key == 'space':
            app.addressInput.addText(' ')   
        elif key == 'backspace':
            app.addressInput.text = app.addressInput.text[:-1]
        elif (key == 'left' or key == 'right' or key == 'tab' or
            key == 'up' or key == 'down' or key == 'enter' or key == 'escape'):
            app.addressInput.addText('') 
        else:
           app.addressInput.addText(key)
        app.currentUsername = app.usernameInput.text
        if app.currentUsername in app.users:
            app.newUser.address = app.addressInput.text
            app.newUser.userInfo['address'] = app.addressInput.text

    # Concern
    if app.loggedIn and app.contactUsButtonPressed:
        if key == 'space':
            app.userProblemReport.addText(' ')   
        elif key == 'backspace':
            app.userProblemReport.text = app.userProblemReport.text[:-1]
        elif (key == 'left' or key == 'right' or key == 'tab' or
            key == 'up' or key == 'down' or key == 'enter' or key == 'escape'):
            app.userProblemReport.addText('') 
        else:
           app.userProblemReport.addText(key)
        app.currentUsername = app.usernameInput.text
        if app.currentUsername in app.users:
            app.newUser.concern = app.userProblemReport.text
            app.newUser.userInfo['concern'] = app.userProblemReport.text

    # Budget
    elif app.loggedIn and app.recommendationsButtonPressed:
        if key.isdigit() or key == "backspace":
            if key == "backspace":
                app.budgetInput.text = app.budgetInput.text[:-1]
            else:
                app.budgetInput.addText(key)

        app.currentUsername = app.usernameInput.text
        if app.currentUsername in app.users and app.budgetInput.text.isdigit():
            app.users[app.currentUsername].budget = int(app.budgetInput.text)


###### DRAW ######

def drawHome(app):
    drawRect(0, 0, app.width, app.height, fill=rgb(255, 223, 121)) # background
    drawRect(0, 370, app.width, 630, fill=rgb(251, 112, 65)) # background colors
    drawRect(320, 300, 900, 800, fill='white') # white box
    drawUpperNav(app)

    drawLabel('Teranga', app.width/2, app.height/2 - 250, fill ='black',size=70, bold=True)
    drawLine(app.width/2-140, app.height/2-215,app.width/2+150, app.height/2-215,lineWidth=3)
    drawLabel(f'Welcome!', app.width / 2, app.height / 2 - 100, fill='brown', size=60, bold=True)
    drawLabel('Please click one of the buttons below:', app.width / 2, app.height / 2 - 40, fill='brown', size=30, align='center')
    drawHomeButtons(app)

def drawHomeButtons(app):
    app.productsButton.draw()
    app.recommendationsButton.draw()
    app.contactUsButton.draw()

def drawUpperNav(app):
    drawRect(0, 0, app.width, 80, fill='white')
    app.productsNavButton.drawNav()
    app.recommendationsNavButton.drawNav()
    app.contactUsNavButton.drawNav()
    app.backButton.drawNav()
    app.logoutButton.draw()

def drawProductsPage(app):
    drawRect(0, 0, app.width, app.height, fill=rgb(251, 112, 65))
    drawRect(320, 100, 900, 980, fill='white')
    drawLabel('What would you like to order?', app.width/2, app.height/6,size=30)
    drawUpperNav(app)
    for product in app.products:
        product.draw()

    drawLabel(f'Your total is: {app.total} XOF',400,670,size=25,
              fill='black', align='left')
    app.submitProductPageButton.draw()
    drawInformationForm(app)
    drawQuantityBox(app)
    drawProductsPlusMinus(app)

def drawQuantityBox(app):
    drawRect(520,280,50,30,fill=None,align='left',border='black')
    drawLabel(app.farineComplete, 536,280,align='left',size=25)
    drawRect(520,390,50,30,fill=None,align='left',border='black')
    drawLabel(app.farinePatisserie, 536,390,align='left',size=25)
    drawRect(520,500,50,30,fill=None,align='left',border='black')
    drawLabel(app.farineBeignetBig, 536,500,align='left',size=25)
    drawRect(520,610,50,30,fill=None,align='left',border='black')
    drawLabel(app.farineBeignetSmall, 536,610,align='left',size=25)

def drawProductsPlusMinus(app):
    # Farine Complete
    drawRect(580, 268, 25, 25, fill=None,border='black')
    drawRect(605, 268, 25, 25, fill=None,border='black')
    drawLabel('+',592,284,size=30, fill='gray')
    drawLabel('-',617,284,size=30, fill='gray')

    # Farine Patisserie
    drawRect(580,378,25,25,fill=None,border='black')
    drawRect(605, 378, 25, 25, fill=None,border='black')
    drawLabel('+',592,394,size=30, fill='gray')
    drawLabel('-',617,394,size=30, fill='gray')

    # Farine Beignet Big
    drawRect(580,488,25,25,fill=None,border='black')
    drawRect(605, 488, 25, 25, fill=None,border='black')
    drawLabel('+',592,504,size=30, fill='gray')
    drawLabel('-',617,504,size=30, fill='gray')

    # Farine Beignet Small
    drawRect(580,598,25,25,fill=None,border='black')
    drawRect(605, 598, 25, 25, fill=None,border='black')
    drawLabel('+',592,614,size=30, fill='gray')
    drawLabel('-',617,614,size=30, fill='gray')

def drawInformationForm(app):
    drawLabel('Please Enter Your Address:',app.width/2-400,720,size=20,
              fill='black', align='left')
    drawRect(app.width/2-400, 750, 800, 100, fill=None, 
             border='black',borderWidth=2)
    app.addressInput.draw()
    drawImages(app)

def drawRecommendationsPage(app):
    drawRect(0, 0, app.width, app.height, fill=rgb(251, 112, 65))
    drawRect(320, 100, 900, 980, fill='white')
    drawUpperNav(app)
    drawRect(0, 0, app.width, app.height, fill=rgb(251, 112, 65))
    drawRect(320, 100, 900, 980, fill='white')
    drawUpperNav(app)
    drawLabel("Unsure of what to get?",
              app.width / 2, 150, fill='brown', size=30, align='center')
    drawLabel('Give us your budget below and we will let you know what you can buy!',
               app.width/2-100,200,size=20,fill='brown', align='center')
    drawRect(340, 220, 300, 50, fill=None, border='black',borderWidth=2)
    drawLabel('XOF',600,245,fill='gray',size=18)
    app.clearBudgetButton.draw()
    app.submitBudgetButton.draw()
    app.budgetInput.draw()  # Draw the budget input box
    if app.submitBudgetButtonPressed:
        drawLabel('Calculating... ', app.width/2,400,size=30,fill='brown', 
                  align='center')
        drawLabel('You should buy the following:', app.width/2,450,size=30,
                  fill='brown', align='center')
        
        startingYPos = 500  # Start position for Y
        lineSpacing = 45  # Space between lines

        # Display each product and the quantity to buy
        for product in app.solution[0]:
            startingYPos += lineSpacing
            drawLabel(f'{product}: {app.solution[0][product]}', app.width/2, 
                      startingYPos, size=20, fill='brown', align='center')

        # Display total kg and price
        startingYPos += lineSpacing
        drawLabel(f'Total Kg bought: {app.solution[1]} kg', app.width/2, 
                  startingYPos, size=20, fill='black', align='center')
        startingYPos += lineSpacing
        drawLabel(f'Total Price: {app.solution[2]} XOF', app.width/2, 
                  startingYPos, size=20, fill='black', align='center')

def drawContactUsPage(app):
    drawRect(0, 0, app.width, app.height, fill=rgb(251, 112, 65))
    drawRect(320, 100, 900, 980, fill='white')
    drawUpperNav(app)
    drawLabel('Need any help? Call us at: +221 77 752 1257', app.width / 2, 
              150, fill='brown', size=30, align='center')
    drawLabel('Have a pressing question? Submit it below:', app.width / 2, 
              225, fill='brown', size=20, align='right')
    drawRect(375, 260, 800, 350, fill=None, border='black',borderWidth=2)
    app.userProblemReport.draw()
    app.submitConcernButton.draw()

def drawLoginPage(app):
    drawRect(0,0,1920,1080,fill='black',opacity=50)
    drawRect(320, 300, 900, 620, fill='white')
    drawLabel('Login', app.width / 2, app.height / 2 - 100, fill='black', size=60, bold=True)
    drawLine(320, 420, 1220, 420, fill='gray', opacity=60)
    drawLabel('Username', 340, 500, size=20,align='left')
    drawRect(340, 520, 380, 50, border='gray',fill=None)
    drawLabel('Password', 340, 600, size=20,align='left')
    drawRect(340, 620, 380, 50, border='gray',fill=None)
    app.loginButton.draw()
    drawLine(320, 780, 1220, 780, fill='gray', opacity=60)
    drawLabel('Not a member?', 340, 850, size=20,align='left',fill='gray')
    app.signUpButton.draw()
    app.passwordInput.draw()
    app.usernameInput.draw()
    if app.loginError:
        drawLabel('Incorrect login credentials!', 840, 600, size=25, 
                  align='left',fill='red')
    
def drawSignUpPage(app):
    drawRect(320, 300, 900, 620, fill='white')
    drawLabel('Sign Up', app.width / 2, app.height / 2 - 100, fill='black', size=60, bold=True)
    drawLine(320, 420, 1220, 420, fill='gray', opacity=60)

    drawLabel('Name', 340, 500, size=20,align='left')
    drawRect(340, 520, 380, 50, border='gray',fill=None)
    drawLabel('Phone Number', 340, 600, size=20,align='left')
    drawRect(340, 620, 380, 50, border='gray',fill=None)

    drawLabel('Create a Username', 800, 500, size=20,align='left')
    drawRect(800, 520, 380, 50, border='gray',fill=None)
    drawLabel('Create a Password', 800, 600, size=20,align='left')
    drawRect(800, 620, 380, 50, border='gray',fill=None)

    app.createAccountButton.draw()
    app.nameSignUpInput.draw()
    app.phoneNumberSignUpInput.draw()
    app.createUsernameInput.draw()
    app.createPasswordInput.draw()
    if app.returnToLoginPage:
        drawLabel('Account Created Successfully!', app.width/2, 800)
        drawLoginPage(app) 

def drawImages(app):
    imageWidth,imageHeight = getImageSize(app.farineBeignetSmallPicture)
    drawImage(app.farineBeignetSmallPicture,app.width/2-400, app.height/2+130, width=imageWidth*0.15, height=imageHeight*0.15, align='center')
    drawImage(app.farineBeignetBigPicture, app.width/2-400, app.height/2+20, width=imageWidth*0.15, height=imageHeight*0.15, align='center')
    drawImage(app.farinePatisseriePicture,app.width/2-400, app.height/2-90, width=imageWidth*0.15, height=imageHeight*0.15, align='center')
    drawImage(app.farineCompletePicture, app.width/2-400, app.height/2-200, width=imageWidth*0.15, height=imageHeight*0.15, align='center')

def drawThankYouPage(app):
    drawRect(0, 0, app.width, app.height, fill=rgb(255, 223, 121)) # background
    drawRect(0, 370, app.width, 630, fill=rgb(251, 112, 65)) # background colors
    drawRect(320, 300, 900, 200, fill='white') # white box
    drawLabel('Teranga', app.width/2, app.height/2 - 250, fill ='black',size=70, bold=True)
    drawUpperNav(app)
    drawLabel(f'Thank You For Your Purchase!', app.width / 2, app.height / 2 - 50, fill='brown', size=55, bold=True)

def redrawAll(app):
    if not app.loggedIn:
        drawHome(app)
        drawLoginPage(app)
    if app.signUpButtonPressed:
        drawSignUpPage(app)
    if app.loggedIn:
        drawHome(app)
        if app.productsButtonPressed:
            drawProductsPage(app)
            if app.showThankYouPage:
                drawThankYouPage(app)
        elif app.recommendationsButtonPressed:
            drawRecommendationsPage(app)
        elif app.contactUsButtonPressed:
            drawContactUsPage(app)


##### MAIN #####

def main():
    runApp(width=app.width, height=app.height)

main()
