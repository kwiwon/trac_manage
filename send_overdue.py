from xmlrpclib import ServerProxy
from datetime import date
import smtplib
import string
import sys
import getopt
import urllib
import json

PROJECTS = {'hisi3516', 'gm8128'}
FROM = "kwiwon_cheng@provideo.com.tw"
CC = ["kwiwon_cheng@provideo.com.tw"]
class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg
def main(argv=None):
    today = date.today().strftime("%m-%d-%Y")
    account_list = json.load(urllib.urlopen('http://192.168.128.96/py/account.py'))
    server = prepare_send()
    for project in PROJECTS:
        p = ServerProxy('http://kwiwon:kwiwon@192.168.128.96/trac/%s/login/rpc' %project)
        nonclosed_ticket = p.ticket.query("status!=closed")
        for ticket_id in nonclosed_ticket:
            ticket = p.ticket.get(ticket_id)
            if 'userfinish' not in ticket[3]:
                continue
            ticket_context = ticket[3]
            if ticket_context['userfinish'] == '':
                continue
            if ticket_context['userfinish'] > today:
                continue
            owner = ticket[3]['owner']
            name = account_list[owner]['name']
            email = account_list[owner]['email']
            if ticket_context['userfinish'] < today:
                sendMail(server, project, ticket_id, email, name, True)
            else:
                sendMail(server, project, ticket_id, email, name, False)
    end_send(server)

def prepare_send():
    server = smtplib.SMTP("ms1.provideo.com.tw")
    return server
def sendMail(server, project, ticket_id, email_to, name_to, overdue):
    SUBJECT = ""
    if overdue:
        SUBJECT = "[%s]Your ticket #%d is overdued" %(project, ticket_id)
        TEXT = 'Dear %s,\n\n' %name_to + 'Remind you that your ticket #%d' %ticket_id + '(http://192.168.128.96/trac/%s/ticket/%d/)' %(project, ticket_id) +' is overdued.\nPlease finish ASAP.\n\nThanks,\nKwiwon'
    else:
        SUBJECT = "[%s]The due day of your ticket #%d is today" %(project, ticket_id)
        TEXT = 'Dear %s,\n\n' %name_to + 'Remind you that your ticket #%d' %ticket_id + '(http://192.168.128.96/trac/%s/ticket/%d/)' %(project, ticket_id) +' due day is today.\n\nRegards,\nKwiwon'

    TO = to
    BODY = string.join(("From: %s" % FROM,"To: %s" % TO,"CC: %s" % string.join(CC), "Subject: %s" % SUBJECT ,"",TEXT), "\r\n")
    TO = [TO] + CC
    server.sendmail(FROM, TO, BODY)
def end_send(server):
    server.quit()
if __name__ == "__main__":
    sys.exit(main())
