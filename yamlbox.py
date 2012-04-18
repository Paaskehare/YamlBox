#/usr/bin/env python
# encoding: utf-8

import yaml
from   html import escape

ELEMENTS = {}

class Element:

    def __init__(self, item):
        self.item = item
        self.xml = self.toxml()

    def escape(self, name):
        return escape(name)

    def toxml(self):
        return ''

class Item(Element):

    def __init__(self, *args, **kwargs):
        # "Specific" openbox commands, those that would normally go instead of "Execute"
        self.SPECIAL = {
          'Reconfigure': self.reconfigure,
          'Exit': self.exit
        }
        super(Item, self).__init__(*args, **kwargs)

    def execute(self, command, prompt):
        return '<action name="Execute">\n%s<command>%s</command>\n</action>\n' % (
          ('<prompt>yes</prompt>' if prompt else ''),
          command
        )

    def exit(self, command, prompt):
        return '<action name="Exit">%s</action>' % ('<prompt>yes</prompt>' if prompt else '')

    def reconfigure(self, command, prompt):
        self.execute('python yamlbox && openbox --reconfigure', prompt)

    def action(self, execute, prompt=False):
        return self.SPECIAL.get(execute, self.execute)(execute, prompt)

    def toxml(self):

        label   = self.item.get('label')
        icon    = self.item.get('icon')
        execute = self.item.get('execute')
        prompt  = self.item.get('prompt')

        return '<item label="%s"%s>\n%s</item>\n' % (
          (self.escape(label) if label else ''),
          (' icon="%s"' % icon if icon else ''),
          self.action(execute, prompt)
          )

class Separator(Element):

    def toxml(self):

        label   = self.item.get('label')

        return '<separator %s/>\n' % \
          ('label="%s"' % self.escape(label) if label else '')

class Menu(Element):

    def toxml(self):

        id     = self.item.get('id')
        label  = self.item.get('label')
        items  = self.item.get('items')

        xml = '<menu%s%s%s>\n' % (
          (' id="%s"' % id if id else ''),
          (' label="%s"' % self.escape(label) if label else ''),
          ('' if items else '/'),
        )
        if items:

            for item in items:
                c = ELEMENTS.get(item['type'], None)
                if c: xml += c(item).xml

            xml += '</menu>\n'

        return xml

class Openbox:
    Header = '''<?xml version="1.0" encoding="UTF-8"?>
<openbox_menu xmlns="http://openbox.org/3.4/menu">

    '''

    Footer = '</openbox_menu>'

'''
  I dont like to do this, but it seemed there was no other easy way around this.
  We have to define these AFTER, because otherwise the parsers wont know about them.
'''

ELEMENTS = {
   'item': Item,
   'separator': Separator,
   'menu': Menu,
}

def parseYaml(f):
    xml = Openbox.Header
    data = yaml.load(open(f).read())

    for menu in data['menus']:

        xml += Menu(menu).xml

    xml += '<menu id="root-menu" label="Openbox 3">\n'

    for item in data['root']:

        c = ELEMENTS.get(item['type'])

        if c: xml += c(item).xml

    xml += '</menu>\n'
    xml += Openbox.Footer

    return xml

print(parseYaml('menu.yaml'))
