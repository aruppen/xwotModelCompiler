#!/usr/bin/env python
# -*- coding: utf-8 -*-

# #############################################################################################################
# Takes a xwot specification and creates a valid WADL file #
# ---------------------------------------------------------------------------------------------------------- #
# #
# Author: Andreas Ruppen                                                                                     #
# License: GPL                                                                                               #
# This program is free software; you can redistribute it and/or modify                                       #
# it under the terms of the GNU General Public License as published by                                     #
# the Free Software Foundation; either version 2 of the License, or                                        #
# (at your option) any later version.                                                                      #
#                                                                                                            #
#   This program is distributed in the hope that it will be useful,                                          #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of                                           #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                                            #
#   GNU General Public License for more details.                                                             #
#                                                                                                            #
#   You should have received a copy of the GNU General Public License                                        #
#   along with this program; if not, write to the                                                            #
#   Free Software Foundation, Inc.,                                                                          #
#   59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.                                                #
##############################################################################################################
import os
import shutil
import string
import logging
import logging.config
import sys
import xml.dom.minidom
import argparse
import traceback
import re
from os.path import dirname, join, expanduser
from pkg_resources import Requirement, resource_filename

if float(sys.version[:3]) < 3.0:
    import ConfigParser
else:
    import configparser as ConfigParser


class Model2Python:
    """
        Created on 27 June 2014
        @author: ruppena
    """

    def __init__(self):
        """Do some initialization stuff"""
        self.__INSTALL_DIR = dirname(__file__)
        self.__CONFIG_DIR = '/etc/Model2WADL/'
        logging.basicConfig(level=logging.ERROR)
        logging.config.fileConfig(
            [join(self.__CONFIG_DIR, 'logging.conf'), expanduser('~/.logging.conf'), 'logging.conf'])
        self.__log = logging.getLogger('thesis')

        self.__log.debug("Reading general configuration from Model2WADL.cfg")
        self.__m2wConfig = ConfigParser.SafeConfigParser()
        self.__m2wConfig.read(
            [join(self.__CONFIG_DIR, 'Model2WADL.cfg'), expanduser('~/.Model2WADL.cfg'), 'Model2WADL.cfg'])

        #you could read here parameters of the config file instead of passing them on cmd line
        self.__baseURI = self.__m2wConfig.get("Config", "baseURI")
        self.__basePackage = self.__m2wConfig.get("Config", "basePackage")
        self.__schemaFile = self.__m2wConfig.get("Config", "schemaFile")
        self.__model = None
        self.__input = None

    def createServers(self, node, path):
        node_type = node.getAttribute('xsi:type')
        resourcePath = path + node.getAttribute('uri') + '/'
        resourcePath = resourcePath.replace('{', '_int:').replace('}', '_')
        if node_type == 'xwot:SensorResource' or node_type == 'xwot:ActuatorResource' or node_type == 'xwot:ContextResource' or node_type == 'xwot:Resource':
            # Create a purly WoT service which runs on a Device.
            self.createPythonService(node, resourcePath)
        elif node_type == 'xwot:VResource':
            # Create a NodeManager service Reflecting the scenario.
            self.createNodeManagerService(node, resourcePath)
            for child_node in self.getResourceNodes(node):
                node_type = child_node.getAttribute('xsi:type')
                if node_type == 'xwot:SensorResource' or node_type == 'xwot:ActuatorResource' or node_type == 'xwot:ContextResource' or node_type == 'xwot:Resource':
                    resourcePath = '/'
                self.createServers(child_node, resourcePath)

    def createPythonService(self, source, path):
        """Handles the creation of on device services"""
        # Todo create unique names for theses
        project_name = 'REST-Servers/' + path.replace('/', '_') + 'Server'
        self.__log.info('Creating Server: ' + project_name)
        shutil.copytree(resource_filename(Requirement.parse("XWoT_Model_Translator"), 'src/REST-Server-Skeleton'),
                        project_name)
        self.addResourceDefinitions(source, project_name, "root")

        #do some cleanup. Essentially remove template parameters.
        filein = open(project_name + '/rest-server.py')
        src = string.Template(filein.read())
        r = {'imports': "", 'pathdef': ""}
        result = src.safe_substitute(r)
        filein.close()
        service_file = open(project_name + '/rest-server.py', "w")
        service_file.write(result)
        service_file.close()
        self.cleanupServerProject(project_name)

    def createNodeManagerService(self, source, path):
        """Handles the creation of NodeManager Services."""
        # Todo create unique names for theses
        project_name = 'REST-Servers/NM-' + path.replace('/', '_') + 'Server'
        self.__log.info('Creating Server: ' + project_name)
        shutil.copytree(resource_filename(Requirement.parse("XWoT_Model_Translator"), 'src/NM_REST-Server-Skeleton'),
                        project_name)
        self.addResourceDefinitions(source, project_name, "root")

        #do some cleanup. Essentially remove template parameters.
        filein = open(project_name + '/rest-server.py')
        src = string.Template(filein.read())
        r = {'imports': "", 'pathdef': ""}
        result = src.safe_substitute(r)
        filein.close()
        service_file = open(project_name + '/rest-server.py', "w")
        service_file.write(result)
        service_file.close()
        self.cleanupServerProject(project_name)

    def addResourceDefinitions(self, node, project_path, parent_filename):
        """Creates a new Resource Class for each URL segment"""
        self.__log.debug("Working on node: " + node.getAttribute('name'))

        #Create the new resource class
        new_parent_filename = self.doAddResourceDefinitions(node, project_path, parent_filename)
        self.__log.debug("associated file is:  " + new_parent_filename)
        # Fill in the getChild method to delegate the right URL to the right Class
        for resource in self.getResourceNodes(node):
            filein = open(new_parent_filename)
            src = string.Template(filein.read())
            classname = resource.getAttribute('name') + "API"
            if '{' in resource.getAttribute('uri'):
                childSubstitute = 'if name.isdigit():' + '\n' + "            return " + classname + "(self.datagen, name, self.__port, '')" + '\n' + "        $child"
            else:
                childSubstitute = "if name == '" + resource.getAttribute(
                    'uri') + "':" + '\n' + "            return " + classname + "(self.datagen, name, self.__port, '')" + '\n' + "        $child"
            importSubstitue = "from " + classname + " import " + classname + '\n' + "$import"
            d = {'child': childSubstitute, 'import': importSubstitue}
            result = src.safe_substitute(d)
            filein.close()
            class_file = open(new_parent_filename, 'w')
            class_file.write(result)
            class_file.close()
            self.addResourceDefinitions(resource, project_path, new_parent_filename)
        # Add all the methods:
        wottype = node.getAttribute('xsi:type')
        if wottype == 'xwot:SensorResource':
            self.addGETMethod(project_path, new_parent_filename)
        elif wottype == 'xwot:ActuatorResource':
            self.addPUTMethod(project_path, new_parent_filename)
        elif wottype == 'xwot:ContextResource':
            self.addGETMethod(project_path, new_parent_filename)
            self.addPUTMethod(project_path, new_parent_filename)
        elif wottype == 'xwot:Resource':
            self.addGETMethod(project_path, new_parent_filename)
            self.addPUTMethod(project_path, new_parent_filename)
        elif wottype == 'xwot:PublisherResource':
            self.addGETMethod(project_path, new_parent_filename)
            self.addPOSTMethod(project_path, new_parent_filename)
        elif wottype == 'xwot:VResource':
            self.addGETMethod(project_path, new_parent_filename)
            self.addPUTMethod(project_path, new_parent_filename)
            self.addPOSTMethod(project_path, new_parent_filename)
            self.addDELETEMethod(project_path, new_parent_filename)

        # Add the resource itself as a child with as the default child to return. This is used for trailing slashes
        filein = open(new_parent_filename)
        src = string.Template(filein.read())
        if len(self.getResourceNodes(node)) > 0:
            childSubstitute = "else:" + '\n' + "            return " + node.getAttribute(
                'name') + "API" + "(self.datagen, name, self.__port, '')" + '\n'
        else:
            childSubstitute = "return " + node.getAttribute(
                'name') + "API" + "(self.datagen, name, self.__port, '')" + '\n'
        importSubstitue = "$import"
        d = {'child': childSubstitute, 'import': importSubstitue}
        result = src.safe_substitute(d)
        filein.close()
        class_file = open(new_parent_filename, 'w')
        class_file.write(result)
        class_file.close()

        #do some cleanup. Essentially remove template parameters.
        filein = open(project_path + '/' + node.getAttribute('name') + "API" + '.py')
        src = string.Template(filein.read())
        r = {'classname': '', 'child': '', 'import': '', 'render_method': ''}
        result = src.safe_substitute(r)
        filein.close()
        service_file = open(project_path + '/' + node.getAttribute('name') + "API" + '.py', "w")
        service_file.write(result)
        service_file.close()

    def doAddResourceDefinitions(self, node, project_path, parent_filename):
        """Intantiates a new resourceAPI.py by copy and fills in the $import and $child Templates"""
        filein = open(project_path + '/resourceAPI.py')
        src = string.Template(filein.read())
        classname = node.getAttribute('name') + "API"
        importsubstitue = '$import'
        childSubstitute = '$child'
        if node.getAttribute('uri') == 'pub':
            # set the childSubstitute for the *PublisherResourceAPI class
            publisherclassname = classname.replace('ResourceAPI', 'ClientResourceAPI')
            childSubstitute = "if name == '':" + '\n'
            childSubstitute = childSubstitute + '            ' + 'ServerFactory = HeartRateBroadcastFactory' + '\n'
            childSubstitute = childSubstitute + '            ' + 'factory = ServerFactory("ws://localhost:"+str(self.__port)+"/", self.datagen, debug = False,  debugCodePaths = False)' + '\n'
            childSubstitute = childSubstitute + '            ' + 'factory.protocol = wotStreamerProtocol' + '\n'
            childSubstitute = childSubstitute + '            ' + 'factory.setProtocolOptions(allowHixie76 = True)' + '\n'
            childSubstitute = childSubstitute + '            ' + 'return WebSocketResource(factory)' + '\n'
            childSubstitute = childSubstitute + '        ' + 'else:' + '\n'
            childSubstitute = childSubstitute + '            ' + "return " + publisherclassname + "(self.datagen, name, self.__port, '')" + '\n'
            childSubstitute = childSubstitute + '            ' + '' + '\n'

            # set the import for the *PublisherResourceAPI class
            importsubstitue = 'from ' + publisherclassname + ' import ' + publisherclassname + '\n'
            importsubstitue += "from WebSocketSupport import wotStreamerProtocol" + '\n'
            importsubstitue += "from WebSocketSupport import HeartRateBroadcastFactory" + '\n'
            importsubstitue += '$import'
            self.createPublisherClient(project_path, publisherclassname)

        d = {'classname': classname, 'child': childSubstitute, 'import': importsubstitue}
        result = src.safe_substitute(d)
        filein.close()
        class_file = open(project_path + '/' + classname + '.py', 'w')
        class_file.write(result)
        class_file.close()

        # Add the definitions to rest_server.py
        filein = open(project_path + '/rest-server.py')
        class_file_in = string.Template(filein.read())
        classnameClass = classname.lower()
        if parent_filename == "root":
            pathdef = classnameClass + "=" + classname + "(data, '', self.__port, '')" + '\n        ' + parent_filename + ".putChild('" + node.getAttribute(
                'uri').replace('{', '').replace('}', '') + "',  " + classnameClass + ")" + '\n        $pathdef'
            imports = "from " + classname + " import " + classname + '\n' + "$imports"
            r = {'imports': imports, 'pathdef': pathdef}
            class_file_in = class_file_in.safe_substitute(r)
            class_file = open(project_path + '/rest-server.py', "w")
            class_file.write(class_file_in)
            class_file.close()
            filein.close()

        return project_path + '/' + classname + '.py'

    def createPublisherClient(self, project_path, classname):
        """Create the  publisher client class"""
        shutil.copy2(os.path.join(project_path, 'resourceAPI.py'), os.path.join(project_path, classname+'.py'))
        self.addGETMethod(project_path, os.path.join(project_path, classname + '.py'))
        self.addPUTMethod(project_path, os.path.join(project_path, classname + '.py'))
        self.addDELETEMethod(project_path, os.path.join(project_path, classname + '.py'))
        filein = open(project_path + '/' + classname + '.py')
        src = string.Template(filein.read())
        filein.close()
        childSubstitute = "return " + classname + "(self.datagen, name, self.__port, '')" + '\n'
        d = {'classname': classname, 'child': childSubstitute, 'import': '', 'render_method': ''}
        result = src.safe_substitute(d)
        class_file = open(project_path + '/' + classname + '.py', 'w')
        class_file.write(result)
        class_file.close()

    @staticmethod
    def addGETMethod(project_path, resource):
        methodin = open(project_path + '/render_GET.txt')
        filein = open(resource)
        render_method = methodin.read() + '\n' + '$render_method'
        src = string.Template(filein.read())
        d = {'render_method': render_method}
        result = src.safe_substitute(d)
        filein.close()
        class_file = open(resource, 'w')
        class_file.write(result)
        class_file.close()

    @staticmethod
    def addPUTMethod(project_path, resource):
        methodin = open(project_path + '/render_PUT.txt')
        filein = open(resource)
        render_method = methodin.read() + '\n' + '$render_method'
        src = string.Template(filein.read())
        d = {'render_method': render_method}
        result = src.safe_substitute(d)
        filein.close()
        class_file = open(resource, 'w')
        class_file.write(result)
        class_file.close()

    @staticmethod
    def addPOSTMethod(project_path, resource):
        methodin = open(project_path + '/render_POST.txt')
        filein = open(resource)
        render_method = methodin.read() + '\n' + '$render_method'
        src = string.Template(filein.read())
        d = {'render_method': render_method}
        result = src.safe_substitute(d)
        filein.close()
        class_file = open(resource, 'w')
        class_file.write(result)
        class_file.close()

    @staticmethod
    def addDELETEMethod(project_path, resource):
        methodin = open(project_path + '/render_DELETE.txt')
        filein = open(resource)
        render_method = methodin.read() + '\n' + '$render_method'
        src = string.Template(filein.read())
        d = {'render_method': render_method}
        result = src.safe_substitute(d)
        filein.close()
        class_file = open(resource, 'w')
        class_file.write(result)
        class_file.close()

    def cleanupServerProject(self, project_path):
        pattern = 'render_\w+.txt'
        self.regexRemove(project_path, pattern)
        pattern = '.*\.pyc'
        self.regexRemove(project_path, pattern)
        os.remove(os.path.join(project_path, 'resourceAPI.py'))

    @staticmethod
    def regexRemove(path, pattern):
        for root, dirs, files in os.walk(path):
            for filteredfile in filter(lambda x: re.match(pattern, x), files):
                os.remove(os.path.join(root, filteredfile))

    @staticmethod
    def getResourceNodes(parent):
        resources = []
        for child in parent.childNodes:
            if child.localName == 'Resource':
                resources.append(child)
        return resources

    def main(self):
        """The main function"""
        self.__log.debug("input File is: " + self.__input)
        self.__model = xml.dom.minidom.parse(self.__input)
        output_dir = 'REST-Servers'
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
        os.mkdir(output_dir)
        entity = self.__model.getElementsByTagName('xwot:Entity')[0]
        ve = self.__model.getElementsByTagName('VirtualEntity')[0]
        try:
            self.__log.info("Start processing")
            logging.debug("Entity is: " + entity.getAttribute('name').lower())
            self.createServers(ve, entity.getAttribute('name').lower())
            self.__log.info("Successfully created the necessary service(s)")
        except Exception as err:
            self.__log.error("Something went really wrong")
            self.__log.debug(err)
            traceback.print_exc(file=sys.stdout)

    def getArguments(self, argv):
        parser = argparse.ArgumentParser()
        parser.add_argument("-i", "--input", help="input xWoT file containing the Model to be translated",
                            required=True)
        args = parser.parse_args(argv)
        self.__input = args.input
        self.main()


if __name__ == "__main__":
    prog = Model2Python()
    prog.getArguments(sys.argv[1:])
