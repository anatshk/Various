import pandas as pd


def split_msg(msg):
    """
    Splits message and extracts timestamp, speaker and msg content
    :param msg: string
    :return: timestamp string, speaker string, content string
    """



# read content from txt
fname = 'whatsapp_group_chat.txt'
with open(fname, 'rb') as f:
    content = f.read()

# split into messages by \n
msg_lines = content.split('\n')
del content

