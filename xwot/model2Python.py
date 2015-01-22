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
# #
# This program is distributed in the hope that it will be useful,                                          #
# but WITHOUT ANY WARRANTY; without even the implied warranty of                                           #
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
        self.__isNodeManager = True

    def createServers(self, node):
        """Main Entry point to parse the xWoT file
        Args:
            node: the root node of the xWoT model
            path: full URL path of the current resource
        Returns:
            nothing
        """
        node_type = node.getAttribute('xsi:type')
        node_composed = False
        if node.hasAttribute('composed'):
            node_composed = True
        resourcePath = '/' + node.getAttribute('uri') + '/'
        resourcePath = resourcePath.replace('{', '_int:').replace('}', '_')
        if node_type == 'xwot:Resource' and node_composed:
            ## Create a NodeManager service Reflecting the scenario.
            self.createNodeManagerService(node, resourcePath)
            ## For each child create another service
            for child_node in self.getResourceNodes(node):
                node_type = child_node.getAttribute('xsi:type')
                if node_type == 'xwot:SensorResource' or node_type == 'xwot:ActuatorResource' or node_type == 'xwot:ContextResource' or node_type == 'xwot:Resource':
                    self.createServers(child_node)
        else:#if node_type == 'xwot:SensorResource' or node_type == 'xwot:ActuatorResource' or node_type == 'xwot:ContextResource' or node_type == 'xwot:Resource':
            # Create a purly WoT service which runs on a Device.
            self.createPythonService(node, resourcePath)

    def createPythonService(self, source_node, path):
        """Handles the creation of on device services
        Args:
            source_node: the node of the xWoT model currently working on
            path: full URL path of the current resource
        Returns:
            nothing
        """
        # Todo create unique names for theses
        self.__isNodeManager = False
        project_name = 'REST-Servers/' + path.replace('/', '_') + 'Server'
        self.__log.info('Creating Server: ' + project_name)
        shutil.copytree(resource_filename(Requirement.parse("XWoT_Model_Translator"), 'xwot/REST-Server-Skeleton'),
                        project_name)
        source_node.setAttribute('uri', source_node.getAttribute('uri').replace('{', '').replace('}', ''))
        self.addResourceDefinitions(source_node, project_name, "")

        #do some cleanup. Essentially remove template parameters.
        filein = open(project_name + '/rest-server.py')
        src = string.Template(filein.read())
        r = {'imports': "", 'pathdef': ""}
        result = src.safe_substitute(r)
        filein.close()
        fileout = open(project_name + '/rest-server.py', "w")
        fileout.write(result)
        fileout.close()

        filein = open(project_name + '/rest-documentation.html')
        src = string.Template(filein.read())
        r = {'tablebody': ''}
        result = src.safe_substitute(r)
        filein.close()
        fileout = open(project_name + '/rest-documentation.html', "w")
        fileout.write(result)
        fileout.close()

        self.cleanupServerProject(project_name)

    def createNodeManagerService(self, source_node, path):
        """Handles the creation of NodeManager Services.
        Args:
            source_node: the node of the xWoT model currently working on
            path: full URL path of the current resource
        Returns:
            nothing
        """
        # Todo create unique names for theses
        self.__isNodeManager = True
        project_name = 'REST-Servers/NM-' + path.replace('/', '_') + 'Server'
        self.__log.info('Creating Server: ' + project_name)
        shutil.copytree(resource_filename(Requirement.parse("XWoT_Model_Translator"), 'xwot/NM_REST-Server-Skeleton'),
                        project_name)
        self.addResourceDefinitions(source_node, project_name, "")

        #do some cleanup. Essentially remove template parameters.
        filein = open(project_name + '/rest-server.py')
        src = string.Template(filein.read())
        r = {'imports': "", 'pathdef': ""}
        result = src.safe_substitute(r)
        filein.close()
        fileout = open(project_name + '/rest-server.py', "w")
        fileout.write(result)
        fileout.close()

        filein = open(project_name + '/rest-documentation.html')
        src = string.Template(filein.read())
        r = {'tablebody': ''}
        result = src.safe_substitute(r)
        filein.close()
        fileout = open(project_name + '/rest-documentation.html', "w")
        fileout.write(result)
        fileout.close()

        self.cleanupServerProject(project_name)

    def addResourceDefinitions(self, node, project_path, parent_filename):
        """Creates a new Resource Class for each URL segment and add some standard behaviour
        Args:
            node: the node of the xWoT model currently working on
            project_path: path name of the current rest-service project
            parent_filename: python module file name of the parent resource
        Returns:
            nothing
        """
        self.__log.debug("Working on node: " + node.getAttribute('name').replace(" ", ""))

        #Create the new resource class
        new_parent_filename = self.createResourceFile(node, project_path, parent_filename)
        self.__log.debug("associated file is:  " + new_parent_filename)
        # Fill in the getChild method to delegate the right URL to the right Class
        for resource in self.getResourceNodes(node):
            filein = open(new_parent_filename)
            src = string.Template(filein.read())
            classname = resource.getAttribute('name').replace(" ", "") + "API"
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
            self.addResourceDefinitions(resource, project_path, parent_filename + '/' + node.getAttribute('uri'))
        # Add all the methods:
        resource = {'name': node.getAttribute('name').replace(" ", ""), 'type': node.getAttribute('xsi:type'),
                    'uri': parent_filename + '/' + node.getAttribute('uri')}
        wottype = node.getAttribute('xsi:type')
        if wottype == 'xwot:SensorResource':
            self.addGETMethod(project_path, new_parent_filename, resource)
        elif wottype == 'xwot:ActuatorResource':
            self.addPUTMethod(project_path, new_parent_filename, resource)
        elif wottype == 'xwot:ContextResource':
            self.addGETMethod(project_path, new_parent_filename, resource)
            self.addPUTMethod(project_path, new_parent_filename, resource)
        elif wottype == 'xwot:Resource':
            self.addGETMethod(project_path, new_parent_filename, resource)
            self.addPUTMethod(project_path, new_parent_filename, resource)
        elif wottype == 'xwot:PublisherResource':
            resource['method'] = 'GET'
            self.addHTMLInfoTableBody(os.path.join(project_path, 'rest-documentation.html'), resource)
            resource['method'] = 'POST'
            self.addHTMLInfoTableBody(os.path.join(project_path, 'rest-documentation.html'), resource)
        elif wottype == 'xwot:VResource':
            self.addGETMethod(project_path, new_parent_filename, resource)
            self.addPUTMethod(project_path, new_parent_filename, resource)
            self.addPOSTMethod(project_path, new_parent_filename, resource)
            self.addDELETEMethod(project_path, new_parent_filename, resource)

        # Add the resource itself as a child with as the default child to return. This is used for trailing slashes
        filein = open(new_parent_filename)
        src = string.Template(filein.read())
        if len(self.getResourceNodes(node)) > 0:
            childSubstitute = "else:" + '\n' + "            return " + node.getAttribute(
                'name').replace(" ", "") + "API" + "(self.datagen, name, self.__port, '')" + '\n'
        else:
            childSubstitute = "return " + node.getAttribute(
                'name').replace(" ", "") + "API" + "(self.datagen, name, self.__port, '')" + '\n'
        importSubstitue = "$import"
        d = {'child': childSubstitute, 'import': importSubstitue}
        result = src.safe_substitute(d)
        filein.close()
        class_file = open(new_parent_filename, 'w')
        class_file.write(result)
        class_file.close()

        #do some cleanup. Essentially remove template parameters.
        filein = open(project_path + '/' + node.getAttribute('name').replace(" ", "") + "API" + '.py')
        src = string.Template(filein.read())
        r = {'classname': '', 'child': '', 'import': '', 'render_method': ''}
        result = src.safe_substitute(r)
        filein.close()
        service_file = open(project_path + '/' + node.getAttribute('name').replace(" ", "") + "API" + '.py', "w")
        service_file.write(result)
        service_file.close()

    def createResourceFile(self, node, project_path, parent_filename):
        """Intantiates a new resourceAPI_skeleton.py or publisher_skeleton.py by copy and
        fills in the $import and $child Templates.

        Args:
            node: the node of the xWoT model currently working on
            project_path: path name of the current rest-service project
            parent_filename: python module file name of the parent resource
        Returns:
            the full path + name of the created file
        """
        node_type = node.getAttribute('xsi:type')
        if node_type == 'xwot:PublisherResource' and not self.__isNodeManager:
            filein = open(project_path + '/publisher_skeleton.py')
        else:
            filein = open(project_path + '/resourceAPI_skeleton.py')
        src = string.Template(filein.read())
        classname = node.getAttribute('name').replace(" ", "") + "API"
        childSubstitute = '$child'
        importsubstitue = '$import'
        if node_type == 'xwot:PublisherResource' and not self.__isNodeManager:
            # set the childSubstitute for the *PublisherResourceAPI class
            if 'Publisher' in classname:
                publisherclientclassname = classname.replace('Publisher', 'PublisherClient')
            else:
                publisherclientclassname = classname+"PublisherClientResourceAPI"
            childSubstitute = publisherclientclassname

            # set the import for the *PublisherResourceAPI class
            importsubstitue = 'from ' + publisherclientclassname + ' import ' + publisherclientclassname + '\n'
            importsubstitue += '$import'
            self.createPublisherClient(project_path, publisherclientclassname, parent_filename)

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

        ## If this is the topmost resource, add it to the rest-server.py file
        if parent_filename == "":
            pathdef = classnameClass + "=" + classname + "(data, '', self.__port, '')" + '\n        ' + "root.putChild('" + node.getAttribute(
                'uri').replace('{', '').replace('}', '') + "',  " + classnameClass + ")" + '\n        $pathdef'
            imports = "from " + classname + " import " + classname + '\n' + "$imports"
            r = {'imports': imports, 'pathdef': pathdef}
            class_file_in = class_file_in.safe_substitute(r)
            class_file = open(project_path + '/rest-server.py', "w")
            class_file.write(class_file_in)
            class_file.close()
            filein.close()

        return project_path + '/' + classname + '.py'

    def createPublisherClient(self, project_path, classname, parent_uri):
        """Create the  publisher client class

        Args:
            project_path: path name of the current rest-service project
            classname: Name of the publisher to create
            parent_uri: URL of the parent to which this publisher is attached to
        Returns:
            nothing
        """
        shutil.copy2(os.path.join(project_path, 'publisher_client_skeleton.py'), os.path.join(project_path, classname + '.py'))
        resource = {'name': classname, 'type': 'publisher',
                    'uri': parent_uri + '/pub/{id}'}
        filein = open(project_path + '/' + classname + '.py')
        src = string.Template(filein.read())
        filein.close()
        childSubstitute = "return " + classname + "(self.datagen, name, self.__port, '')" + '\n'
        d = {'classname': classname, 'child': childSubstitute, 'import': '', 'render_method': ''}
        result = src.safe_substitute(d)
        class_file = open(project_path + '/' + classname + '.py', 'w')
        class_file.write(result)
        class_file.close()

        ## Update the index.html page
        resource['method'] = 'GET'
        self.addHTMLInfoTableBody(os.path.join(project_path, 'rest-documentation.html'), resource)
        resource['method'] = 'PUT'
        self.addHTMLInfoTableBody(os.path.join(project_path, 'rest-documentation.html'), resource)
        resource['method'] = 'DELETE'
        self.addHTMLInfoTableBody(os.path.join(project_path, 'rest-documentation.html'), resource)

    def addGETMethod(self, project_path, resourceclassfile, resource):
        methodin = open(project_path + '/render_GET.txt')
        filein = open(resourceclassfile)
        render_method = methodin.read() + '\n' + '$render_method'
        src = string.Template(filein.read())
        d = {'render_method': render_method}
        result = src.safe_substitute(d)
        filein.close()
        class_file = open(resourceclassfile, 'w')
        class_file.write(result)
        class_file.close()
        resource['method'] = 'GET'
        self.addHTMLInfoTableBody(os.path.join(project_path, 'rest-documentation.html'), resource)

    def addPUTMethod(self, project_path, resourceclassfile, resource):
        methodin = open(project_path + '/render_PUT.txt')
        filein = open(resourceclassfile)
        render_method = methodin.read() + '\n' + '$render_method'
        src = string.Template(filein.read())
        d = {'render_method': render_method}
        result = src.safe_substitute(d)
        filein.close()
        class_file = open(resourceclassfile, 'w')
        class_file.write(result)
        class_file.close()
        resource['method'] = 'PUT'
        self.addHTMLInfoTableBody(os.path.join(project_path, 'rest-documentation.html'), resource)

    def addPOSTMethod(self, project_path, resourceclassfile, resource):
        methodin = open(project_path + '/render_POST.txt')
        filein = open(resourceclassfile)
        render_method = methodin.read() + '\n' + '$render_method'
        src = string.Template(filein.read())
        d = {'render_method': render_method}
        result = src.safe_substitute(d)
        filein.close()
        class_file = open(resourceclassfile, 'w')
        class_file.write(result)
        class_file.close()
        resource['method'] = 'POST'
        self.addHTMLInfoTableBody(os.path.join(project_path, 'rest-documentation.html'), resource)

    def addDELETEMethod(self, project_path, resourceclassfile, resource):
        methodin = open(project_path + '/render_DELETE.txt')
        filein = open(resourceclassfile)
        render_method = methodin.read() + '\n' + '$render_method'
        src = string.Template(filein.read())
        d = {'render_method': render_method}
        result = src.safe_substitute(d)
        filein.close()
        class_file = open(resourceclassfile, 'w')
        class_file.write(result)
        class_file.close()
        resource['method'] = 'DELETE'
        self.addHTMLInfoTableBody(os.path.join(project_path, 'rest-documentation.html'), resource)

    def addHTMLInfoTableBody(self, htmlfile, resource):
        tablebody = '    <div id="' + resource[
            'name'] + '" class="method">' + '\n' + '        <tr>' + '\n' + '            <td>' + '\n' + '                <div id="' + \
                    resource['name'] + 'Address" class="address"><a href="' + resource[
                        'uri'] + '">http://localhost:9000' + resource[
                        'uri'] + '</a></div></td>' + '\n' + '            <td>' + '\n' + '                <div id="' + \
                    resource['name'] + 'Label">' + resource['name'] + ' - ' + resource[
                        'type'] + '</div>' + '\n' + '            </td>' + '\n' + '            <div id="' + resource[
                        'name'] + 'Operation" class="operation">' + '\n' + '                <td>' + '\n' + '                    <div id="' + \
                    resource[
                        'name'] + 'Input" class="input">-</div>' + '\n' + '                    /' + '\n' + '                    <div id="' + \
                    resource[
                        'name'] + 'Output" class="output">JSON-XML-HTML</div>' + '\n' + '                </td>' + '\n' + '                <td>' + '\n' + '                    <div class="label">' + \
                    resource[
                        'method'] + '</div>' + '\n' + '                </td>' + '\n' + '            </div>' + '\n' + '            <td></td>' + '\n' + '        </tr>' + '\n' + '    </div>' + '\n' + '$tablebody'
        filein = open(htmlfile)
        src = string.Template(filein.read())
        d = {'tablebody': tablebody}
        result = src.safe_substitute(d)
        filein.close()
        fileout = open(htmlfile, 'w')
        fileout.write(result)
        fileout.close()

    def cleanupServerProject(self, project_path):
        pattern = 'render_\w+.txt'
        self.regexRemove(project_path, pattern)
        pattern = '.*\.pyc'
        self.regexRemove(project_path, pattern)
        pattern = '.*_skeleton\.py'
        self.regexRemove(project_path, pattern)


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
            logging.debug("Entity is: " + entity.getAttribute('name').replace(" ", "").lower())
            self.createServers(ve)
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
