from config import DEBUG, EPOCH
# ======<Sync Setting>======= #
# if sending email after code running stop.(type: bool)
SEND_MAIL = True
SEND_MAIL = False if EPOCH < 5 or DEBUG else SEND_MAIL
# address and password(not your real password, but a code used for SMTP login service.)
FROM_ADDRESS = 'email address1'
# PASSWD = 'kqddfbmxiipqcaeg'
PASSWD = 'hqytohqljgnebhhg'

# address you want to send mail to.
TO_ADDRESS = 'email address2'

# SMTP server address.
SMTP_SERVER = 'smtp.qq.com'

# usable SMTP port, please check at your email settings.(type: int)
SMTP_PORT = 465
