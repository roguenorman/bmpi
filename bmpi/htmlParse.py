#!/usr/bin/python3
from html.parser import HTMLParser


class parser(HTMLParser):

    def handle_endtag(self, tag):
        print("End tag  :", tag)

    def handle_data(self, data):
        print("Data     :", data)


    def handle_decl(self, data):
        print("Decl     :", data)