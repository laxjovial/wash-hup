from app.models.auth.user import Notifications
from app.websocket.router import manager
import uuid


class Notification:
    def __init__(self):
        # owners notifications 
        self.login_owner = "Hey {fullname}! Welcome back.\nAmazing discounts and great deals await you! Start by booking a wash now!!!"
        self.signup_owner = "Welcome to Wash-Hup {fullname}, we are glad to have you on board 🎊🎊🎊.\nSet up your profile to get started with your wash."
        self.price_offer = "Helo {fullname}, {washer_name} sent a price offer just now, comfirm to start wash."
        self.wash_created = "{fullname}, you have created a new wash request. Click here to continue with the wash."
        self.wash_accepted = "Hello {fullname}, your wash has been accepted by {washer} successfully. Contect washer for easily comms."

        # washers notifications 
        self.login_washer = "Hey {fullname}! Welcome back. Wash are ready for you"
        self.signup_washer = "Hey {fullname}! Welcome to Wash-Hup. Amazing deals waiting for you, complete your profile to get started."
        self.upcoming_offer = "{fullname} you have a new offer available from {client_name}"
        self.offer_accepted = "Hey {fullname}, you have successfully accepted an offer, keep moving to complete the wash."
        self.price_offer_accepted = "Hey {fullname}, price offer for {client_name} has been accepted."
        self.request_review = "Hey {fullname} requested for a review on their wash."

        # admin notifications 
        self.login_admin = "Welcome admin {fullname}"
        self.signup_admin = "Welcome {fullname}, you are now added as an admin."

        # other notifications 
        self.logout = "{fullname} logged out successfully at {time}"
        self.new_address = "Hello {fullname}, a new address has been added to your profile."
        self.address_updated = "Hello {fullname}, your address has been updated."

    
        self.profile_update = "Hello {fullname}, your profile has just been updated. Profile details can only be changed in the next 14 days"
        self.password_change = "Hey {fullname}, your password has recently been changed.\nIf you didn't change it please reach out to our support team."
        self.transaction_success = "Hey {fullname}, your transaction was successful.\nPayment of N{amount} made to {receiver} account."
        self.transaction_failure = "Hey {fullname}, there was an issue with your transaction.\nPayment of N{amount} was not made to {receiver} account"
        self.issue_created = "Hey {fullname}, you successfully created and issue. Tell us how we can help you."
        self.issue_messages = "Hello {fullname}, you have a new message in your issue inbox."
        self.discount_available = "{fullname}, Good news you have received a discount bonus for your next wash.\n{dicount_details}."
        self.discount_expired = "Hello {fullname}, your discount has expired.\n{discount_details}"
        self.washer_message = "Hey {fullname}, you've a new message from a washer.\n{washer} sent a message. Click to see it."
        self.new_notification = ""
        self.verify_email = "{fullname}, your email {email} has not been verified. Please do that."
        self.email_verfied = "Hey {fullname}, your email has been verified successfully. You can continue with your washes."
        self.rate_request = ""
        self.wash_completed = ""
        self.wash_cancelled = ""
        self.wash_request = ""
        self.wash_offer = ""
        self.wash_offer_accepted = ""
        self.wash_offer_rejected = ""
        self.wash_started = ""
        self.payment_request = ""
        self.payment_success = ""
        self.payment_failure = ""
        self.other_messages = {}

    def add_message(self, name: str, message: str):
        self.other_messages[name] = message

class Notify:
    def format(self, message: str, **kwarg):
        return message.format(**kwarg)

    async def create(self, db, id: str, title: str, message: str, fullname: str, **kwargs):

        notification_model = Notifications(
            id=str(uuid.uuid4()),
            profile_id=id,
            title=title,
            message=self.format(message, fullname=fullname, **kwargs)
        )

        db.add(notification_model)
        db.commit()
        db.refresh(notification_model)
        
        data = {
            "action": "notification",
            "id": notification_model.id,
            "title": notification_model.title,
            "message": notification_model.message,
        }
        await manager.send_personal(data, notification_model.profile_id)


NOTIFICATION = Notification()
NOTIFY = Notify()



    

