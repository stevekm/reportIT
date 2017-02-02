#!/bin/bash

# This file contains settings used by the pipeline to mail files
# this should be 'source'd


# Default reciepient list
# recipient_list="address1@gmail.com, address2@gmail.com"
recipient_list="kellys04@nyumc.org"

# check for a saved email recipient list to use instead
email_recipient_file="data/email_recipients.txt"
if [ -f "$email_recipient_file" ] ; then
    recipient_list="$(tr -d '\n' < "$email_recipient_file" )"
fi

# not implemented yet
cc_list=""
bcc_list=""

# reply-to field; PUT YOUR EMAIL HERE
export EMAIL="kellys04@nyumc.org"

# name in the email body signature; YOUR NAME HERE
signature_name="Stephen"

# message at the bottom of the email
message_footer='- This message was sent automatically by the reportIT IonTorrent analysis reporting pipeline -'
